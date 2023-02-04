#!/usr/bin/env python
"""Tests for autopuller"""
import subprocess
import os
import puller

KNOWNSHA = "1957e04f8c8b294785826f763c008d111bc5019b"
KNOWNFAIL = "b74e27446c1397a4c3fbb18fe6cbffda44abf1a6"
RANDOMSHA = "55"

DIFFONE = "b74e27446c1397a4c3fbb18fe6cbffda44abf1a6"
DIFFTWO = "3b63eb8191d3ba86c509e297cd9b88bfbfb49162"


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
    assert "Dockerfile" in str(a)


def test_check_fetchSum():
    """
    Checks that we are succesfully receiving the latest sum from github
    """
    assert len(puller.fetchSum()) > 5


def test_differences_commits():
    a = puller.list_differences_commits(DIFFTWO, DIFFONE)
    assert "chore" in a[0]


def test_restart_service():
    """
    Tests restarting the service
    """
    assert os.getcwd() != "/tmp"
    assert puller.restart_service("/tmp", True) == [
        "docker-compose",
        "up",
        "-f",
        "{{COMPOSEFILE}}",
        "--build",
        "-d",
    ]
    assert os.getcwd() == "/tmp"
