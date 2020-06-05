#!/usr/local/bin/python3.7

import re
import subprocess
import sys


BRANCHES_TO_SKIP = ["develop", "master", "test-release", "live-release"]
ISSUE_NUMBER_REGEX = "[a-z]+#[0-9]+$"


def prepare_commit_msg(commit_editmsg_path):
    current_branch_name = subprocess.check_output("git branch | grep '*'", shell=True).decode().split()[1]
    if current_branch_name in BRANCHES_TO_SKIP:
        return

    issue_number = current_branch_name.split("-")[0]
    if not re.match(ISSUE_NUMBER_REGEX, issue_number):
        return

    subprocess.check_output("echo {}".format(issue_number), shell=True)

    with open(commit_editmsg_path, mode="r+") as f:
        msg = f.read()
        f.seek(0, 0)
        f.write("{issue_number} {msg}".format(issue_number=issue_number, msg=msg))


if __name__ == "__main__":
    prepare_commit_msg(sys.argv[1])
