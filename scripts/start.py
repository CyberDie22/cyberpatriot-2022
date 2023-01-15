#!/usr/bin/python3

import platform, subprocess, os


def run(command):
    return subprocess.check_call(command)


uname = platform.uname()


if "Ubuntu" in uname.version:
    if os.geteuid() != 0:
        print("You must run this as root!")
        exit(1)

    run("bash " + os.getcwd() + "/ubuntu/start.sh")
else:
    print("We don't support anything other than Ubuntu right now!")