#!/usr/bin/python3

import platform, subprocess, os


def run(command: [str]) -> int:
    return subprocess.check_call(command)


def run_with_output(command: [str]) -> str:
    return subprocess.check_output(command)


release = run_with_output(["lsb_release", "-r"]).split(" ")[-1]

print(release)
