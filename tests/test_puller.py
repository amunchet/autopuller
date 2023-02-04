#!/usr/bin/env python
"""Tests for autopuller"""
import subprocess
import os
import puller

KNOWNSHA="1957e04f8c8b294785826f763c008d111bc5019b"
KNOWNFAIL="1957e04f8c8b294785826f763c008d111bc5019b"
RANDOMSHA = "55"

DIFFONE="TODO:c8fd8e841e2f6fb5f3"
DIFFTWO = "TODO:cc26ac06658c3aa7"



def test_check_lastrun():
    """Tests last run to see if actions completed correctly"""
    assert puller.check_lastrun(KNOWNSHA) is True
    assert puller.check_lastrun(KNOWNFAIL) is False
    assert puller.check_lastrun(RANDOMSHA) is False

def test_check_differences():
    """
    Tests the differences between two commits
    """
    a = puller.check_differences(DIFFTWO, DIFFONE)
    assert "serve.py" in str(a)



def test_check_fetchSum():
    """
    Checks that we are succesfully receiving the latest sum from github
    """
    assert len(puller.fetchSum()) > 5

def test_restart_service():
    """
    Tests restarting the service
    """
    assert puller.restart_service("test", 1) == puller.BACKEND_RESTART + " test"


def test_differences_commits():
    a = puller.list_differences_commits(DIFFTWO, DIFFONE)
    assert "fix" in a[0]

def test_bump_version_helper():
    """Tests the commit helper"""
    version = "v1.7.2"
    commit_msgs = [
        "feat: test",
        "chore: test",
        "fix: fixed test",
        "BREAKING CHANGE: Big problem",
        "docs: update",
    ]
    assert str(puller.bump_version_helper(version, commit_msgs)) == "2.8.23"



def test_bump_version():
    """
    Tests bumping the version and creation of the gittag
    """
    # Check current git tag
    result = subprocess.run(["git", "describe"], stdout=subprocess.PIPE)

    current_git_version = str(result.stdout).split('-')[0]
    assert len(current_git_version) > 3

    # Check the current version
    with open(VERSIONFILE) as f:
        current_version = f.read().split("\"")[1]
    
    assert len(current_version) > 3

    # Run the version bump

    commit_msgs = ["feat: test"]

    new_version = puller.bump_version(commit_msgs)
    assert new_version != None
    assert new_version != current_version
    assert new_version != current_git_version

    # Check the new git tag
    result = subprocess.run(["git", "tag"], stdout=subprocess.PIPE)

    all_versions = str(result.stdout).split("\\n")
    assert "v" + new_version in all_versions

    # Check the new version
    with open(VERSIONFILE) as f:
        new_file_version = f.read().split("\"")[1]

    assert len(new_file_version) > 3
    assert new_file_version != current_version
    

    # Revert the git tag
    os.system("git tag -d v" + new_version)
    result = subprocess.run(["git", "tag"], stdout=subprocess.PIPE)

    all_versions = str(result.stdout).split("\\n")
    assert "v" + new_version not in all_versions

    # Revert the version
    os.system("rm -rf " + VERSIONFILE)
    with open(VERSIONFILE, "w") as f:
        f.write("__version__ = \"" + current_version + "\"")
    
    with open(VERSIONFILE) as f:
        new_file_version = f.read().split("\"")[1]

    assert new_file_version == current_version




