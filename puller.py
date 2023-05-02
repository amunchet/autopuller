#!/usr/bin/env python3
"""Autopuller - Continuous Delivery"""
import uuid
import dotenv
import requests
import os
import time
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
if os.path.exists(".env"):  # pragma: no cover
    dotenv.load_dotenv()
elif os.path.exists(".env.sample"):
    logger.debug("Loading sample environment...")
    dotenv.load_dotenv(".env.sample")
else:  # pragma: no cover
    raise Exception("No .env file found")

# TODO: Env variables
GITHUBKEY = os.environ.get("GITHUBKEY")

if not GITHUBKEY:  # pragma: no cover
    raise Exception("No GITHUBKEY found")

REPONAME = (
    os.environ.get("REPONAME").replace("www.", "").replace("https://github.com/", "")
)
if not REPONAME:  # pragma: no cover
    raise Exception("No REPONAME set")

if REPONAME[0] != "/":
    REPONAME = f"/{REPONAME}"
if REPONAME[-1] != "/":
    REPONAME = f"{REPONAME}/"


REPODIR = os.environ.get("REPODIR")
if not REPODIR:  # pragma: no cover
    raise Exception("No REPODIR set")

MASTERFILE = f"{REPODIR}/.git/refs/heads/master"  # Docker-compose mounts repo to /repo


SENDMAIL = os.environ.get("SENDMAIL_CMD") or "mail -s"
LINTING_COMMIT_MSG = os.environ.get("LINTING_COMMIT_MSG") or "Automatic linting fix"

INTERVAL = os.environ.get("INTERVAL") or "60"
COMPOSEFILE = os.environ.get("COMPOSEFILE") or "docker-compose.yml"


def check_lastrun(sha):
    """Checks the last action run from the github"""
    # Step 2: Test to see if the tests are passing
    logger.debug(f"Checking last run of sha:{sha}")
    headers = {"Authorization": f"token {GITHUBKEY}"}
    url = f"https://api.github.com/repos{REPONAME}actions/runs"
    logger.debug(f"Check last run url: {url}")
    a = requests.get(url, headers=headers)

    logger.debug(a)

    # Check if automatic linting fix
    if fetchSum()["commit"]["message"] == LINTING_COMMIT_MSG:
        logger.debug("Found automatic linting fix, returning true")
        return True

    for item in a.json()["workflow_runs"]:
        logger.debug(f"Current sha {item['head_sha']}")

        if item["head_sha"] == sha and item["conclusion"] == "success":
            logger.debug("Found workflow run for sha sum - success!")
            return True
        if item["head_sha"] == sha:
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
    headers = {"Authorization": f"token {GITHUBKEY}"}

    url = f"https://api.github.com/repos{REPONAME}compare/{older_sha}...{newer_sha}"
    logger.debug(url)
    a = requests.get(url, headers=headers)

    try:
        return [x["filename"] for x in a.json()["files"]]
    except Exception:  # pragma: no cover
        logger.error(a.json())
        raise Exception("Error comparing commits")


def fetchSum():
    """Fetches the sum from github"""
    try:
        headers = {"Authorization": f"token {GITHUBKEY}"}
        url = f"https://api.github.com/repos{REPONAME}commits/master"
        a = requests.get(url, headers=headers)
    except TypeError:  # pragma: no cover
        logger.error(f"Fetch Sum failed: {REPONAME}")
        raise Exception(
            "Fetch Sum failed.  ENV file is probably empty.  Create .env with contents GITHUBKEY=XXXX"
        )
    return a.json()


def restart_service(repo_dir, dry_run=False):
    """
    Restarts the docker-compose stack
    """
    cmd = ["docker-compose", "-f", COMPOSEFILE, "up", "--build", "-d"]

    os.chdir(repo_dir)

    if dry_run:
        return cmd
    else:  # pragma: no cover
        logger.debug("Restarting dockers...")
        logger.debug(cmd)

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={"PWD": repo_dir}
        )
        if result.returncode == 0:
            logger.debug("Service restart success!")
            logger.debug(result.stdout.decode("utf-8"))
        else:
            logger.error("Service restart failed!")
            logger.error(result.stderr.decode("utf-8"))
        return result.returncode


def list_differences_commits(older_sha, newer_sha):
    headers = {"Authorization": f"token {GITHUBKEY}"}
    a = requests.get(
        f"https://api.github.com/repos{REPONAME}compare/{older_sha}...{newer_sha}",
        headers=headers,
    )

    return [x["commit"]["message"] for x in a.json()["commits"]]


def main(filename="/var/log/autopuller"):  # pragma: no cover
    """Main running function"""
    logger.debug("Filename is: " + filename)

    # Step 1: Check if we have a difference
    with open(MASTERFILE) as f:
        master_sum = f.read().strip()

    fetch_sum = fetchSum()["sha"].strip()

    if master_sum.strip() != fetch_sum.strip():
        logger.debug("Master sum: " + master_sum)
        logger.debug("Fetch sum: " + fetch_sum)
        logger.debug("Sums do not match!")

        if check_lastrun(fetch_sum):
            logger.warning("Last run passed, proceeding.")
            diffs = check_differences(master_sum, fetch_sum)

            if diffs == []:
                logger.error(
                    "No files changed.  Probably we have a newer version of the repo.  Exiting"
                )
                return False

            # Need to run git pull here

            os.chdir(REPODIR)
            logger.debug("Current directory:")
            logger.debug(os.listdir("."))

            subprocess.run(
                "git config credential.helper store",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Add global safe directory
            cmd = f"git config --global --add safe.directory {REPODIR}"
            logger.debug("Adding safe directory...")
            logger.debug(str(cmd))

            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                logger.debug("Git permissions OK")
                logger.debug(result.stdout.decode("utf-8"))
            else:
                logger.error("Git permissions failed!")
                logger.debug(result.stdout.decode("utf-8"))
                logger.error(result.stderr.decode("utf-8"))
                raise Exception("Git permissions failed")

            logger.debug("Starting git pull...")
            result = subprocess.run(
                "git pull", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            if result.returncode == 0:
                logger.warning("Git pull OK")
                logger.warning(result.stdout.decode("utf-8"))
            else:
                logger.error("Git pull failed!")
                logger.error(result.stderr.decode("utf-8"))
                raise Exception("Git pull failed")

            logger.warning("Git pull ended")

            # Restarts the services
            restart_service(REPODIR)

            return True

        else:
            logger.error("Last run failed or not found.  Exiting")
            return False

    else:
        logger.debug("Sums match.  Nothing to do.")
        return False


if __name__ == "__main__":  # pragma: no cover
    try:
        while True:
            main()
            time.sleep(int(INTERVAL))
            logger.warning(f"Sleeping {INTERVAL}...")
    except Exception as e:
        logger.error(str(e))
        logger.error(sys.exc_info()[1])
