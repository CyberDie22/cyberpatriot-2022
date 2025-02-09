#!/usr/bin/python3

import platform, subprocess, os


def run(command):
    return subprocess.check_call(command)


uname = platform.uname()


if "Ubuntu" in uname.version:
    if os.geteuid() != 0:
        print("You must run this as root!")
        exit(1)

    os.chdir(os.getcwd() + "/ubuntu")

    run(["/bin/bash", "start.sh"])
if "fedora" in uname.node:
    if os.geteuid() != 0:
        print("You must run this as root!")
        exit(1)

    os.chdir(os.getcwd() + "/fedora")

    run(["/bin/bash", "start.sh"])
else:
    print("We don't support anything other than Ubuntu right now!")
    print("(Debug: " + str(uname) + ")")