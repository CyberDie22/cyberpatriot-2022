#!/usr/bin/python3

import subprocess, os, pwd


def run_with_output(command: [str]) -> int:
    return subprocess.check_call(command)


def run_get_output(command: [str]) -> str:
    return subprocess.check_output(command).decode()


def run(command: [str]):
    subprocess.check_output(command)


def install_packages(packages: str):
    print("Installing " + packages)
    run(["apt", "update", "-y"])
    run(["apt", "install", "-y", packages])
    print("Finished installing " + packages)


print("Running CyberPatriot 2022 Script on Ubuntu 22.04")

# print("\nUpdating system...")
# run(["apt", "update", "-y"])
# run(["apt", "upgrade", "-y"])
# print("\nDone updating system")

print("\nAudit users...")
with open("/etc/login.defs", "r") as f:
    for line in f.readlines():
        if line.startswith("UID_MIN"):
            UID_MIN = int(line.split("\t")[-1].strip())
        if line.startswith("UID_MAX"):
            UID_MAX = int(line.split("\t")[-1].strip())

ME = run_get_output("logname")

users = pwd.getpwall()
users = list(filter(lambda x: x.pw_uid in range(UID_MIN, UID_MAX), users))

print(users)

