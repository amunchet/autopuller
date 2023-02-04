#!/usr/bin/env python3
"""Autopuller - Continuous Delivery"""
import uuid
import dotenv
import requests
import os
import semantic_version
import sys
import shlex

from email.mime.text import MIMEText
import subprocess
from subprocess import Popen, PIPE

from autopuller_logger import *


# Logging
logger.debug("Autopuller starting up...")


# Load env variables
if os.path.exists(".env"): # pragma: no cover
    dotenv.load_dotenv()
elif os.path.exists(".env.sample"):
    logger.debug("Loading sample environment...")
    dotenv.load_dotenv(".env.sample")
else: # pragma: no cover
    raise Exception ("No .env file found")

# TODO: Env variables
GITHUBKEY=os.environ.get("GITHUBKEY") 

if not GITHUBKEY: # pragma: no cover
    raise Exception("No GITHUBKEY found")

REPONAME=os.environ.get("REPONAME")
if not REPONAME: # pragma: no cover
    raise Exception("No REPONAME set")

REPODIR=os.environ.get("REPODIR")
if not REPODIR: # pragma: no cover
    raise Exception("No REPODIR set")

MASTERFILE="/repo/.git/refs/heads/master" # Docker-compose mounts repo to /repo

TO=os.environ.get("EMAIL_TO")
FROM=os.environ.get("EMAIL_FROM")
SUBJECT= os.environ.get("EMAIL_SUBJECT")

SENDMAIL = os.environ.get("SENDMAIL_CMD") or "mail -s"
LINTING_COMMIT_MSG=os.environ.get("LINTING_COMMIT_MSG") or "Automatic linting fix"

INTERVAL = os.environ.get("INTERVAL") or "60"

def send_email(TEXT): # pragma: no cover
    """Send email helper"""

    cmd  = f"echo '{TEXT}' | {SENDMAIL} '{SUBJECT}' -r '{FROM}' '{TO}'"
    raise Exception("TODO: Need to put in shlex to sanitize")
    return subprocess.call(cmd, shell=True)

def check_lastrun(sha):
    """Checks the last action run from the github"""
    # Step 2: Test to see if the tests are passing
    logger.debug(f"Checking last run of sha:{sha}")
    headers = { 'Authorization' : f"token {GITHUBKEY}" }
    a = requests.get(f"https://api.github.com/repos{REPONAME}actions/runs", headers=headers)

    logger.debug(a)
    
    # Check if automatic linting fix
    if fetchSum()['commit']['message'] == LINTING_COMMIT_MSG:
        logger.debug("Found automatic linting fix, returning true")
        return True

    for item in a.json()['workflow_runs']:
        logger.debug(f"Current sha {item['head_sha']}")

        if item['head_sha'] == sha and item['conclusion'] == 'success':
            logger.debug("Found workflow run for sha sum - success!")
            return True
        if item['head_sha'] == sha:
            logger.debug("Workflow run for sha sum failed.")
            return False
    
    logger.debug("No workflow runs found - probably not completed yet.")
    return False

def check_differences(older_sha, newer_sha):
    """
    Checks differences between two commits
        - ORDER MATTERS - newer needs to be second
    """
    logger.debug(f"Check differences - older sha: {older_sha}")
    logger.debug(f"Check differences - newer sha: {newer_sha}")
    # Step 2: Test to see if the tests are passing
    headers = { 'Authorization' : f"token {GITHUBKEY}" }

    url = f"https://api.github.com/repos{REPONAME}compare/{older_sha}...{newer_sha}"
    logger.debug(url)
    a = requests.get(url, headers=headers)

    try:
        return [x['filename'] for x in a.json()['files']]
    except Exception: # pragma: no cover
        logger.error(a.json())
        raise Exception("Error comparing commits")

def fetchSum():
    """Fetches the sum from github"""
    try:
        headers = { 'Authorization' : f"token {GITHUBKEY}" }
        a = requests.get(f"https://api.github.com/repos{REPONAME}commits/master", headers=headers)
    except TypeError: # pragma: no cover
        logger.error(f"Fetch Sum failed: {REPONAME}")
        raise Exception("Fetch Sum failed.  ENV file is probably empty.  Create .env with contents GITHUBKEY=XXXX")

    return a.json()

def restart_service(repo_dir, dry_run = False):
    """
    Restarts the docker-compose stack
    """
    cmd = ["docker-compose", "up", "--build", "-d"]

    os.chdir(repo_dir)

    if dry_run:
        return cmd
    else: # pragma: no cover
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            logger.debug(result.stdout.decode('utf-8'))
        else:
            logger.error(result.stderr.decode('utf-8'))
        return result.returncode

def list_differences_commits(older_sha, newer_sha):
    headers = { "Authorization" : f"token {GITHUBKEY}" }
    a = requests.get(f"https://api.github.com/repos{REPONAME}compare/{older_sha}...{newer_sha}", headers=headers)

    return [x['commit']['message'] for x in a.json()['commits']]

def main(filename="/var/log/autopuller"): # pragma: no cover
    """Main running function"""
    logger.debug("Filename is: " + filename)

    # Step 1: Check if we have a difference
    with open(MASTERFILE) as f:
        master_sum = f.read().strip()

    fetch_sum = fetchSum()['sha'].strip()    

    if master_sum.strip() != fetch_sum.strip():
        logger.debug("Master sum: " + master_sum)
        logger.debug("Fetch sum: " + fetch_sum)
        logger.debug("Sums do not match!")

        if(check_lastrun(fetch_sum)):
            logger.debug("Last run passed, proceeding.")
            diffs = check_differences(master_sum, fetch_sum)

            if diffs == []:
                logger.debug("No files changed.  Probably we have a newer version of the repo.  Exiting")
                return False
            
            # Need to run git pull here
            os.system("git config credential.helper store")

            logger.debug("Starting git pull...")
            os.system("git pull")

            logger.debug("Git pull ended")


            # Restarts the services
            restart_service(REPODIR)

            
            with open(filename, "r") as f:
                send_email(f.read())

            return True

        else:
            logger.debug("Last run failed or not found.  Exiting")
            return False

    else:
        logger.debug("Sums match.  Nothing to do.")
        return False

if __name__ == "__main__": # pragma: no cover
    try:
        while True:
            main()
            os.sleep(int(INTERVAL))
    except Exception as e:
        logger.error(str(e))
        logger.error(sys.exc_info()[1])
        with open(filename) as f:
            send_email(f.read())


