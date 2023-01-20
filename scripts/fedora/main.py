#!/usr/bin/python3

import platform, subprocess, os


def run(command: [str]) -> int:
    return subprocess.check_call(command)


def run_with_output(command: [str]) -> str:
    return subprocess.check_output(command).decode()


with open("/etc/fedora-release", "r") as f:
    release = int(f.readline().split(" ")[2])

match release:
    # TODO: maybe have different ones for ~these
    case 37 | 36:
        os.chdir(os.getcwd() + "/36")

        run(["/bin/bash", "start.sh"])
        # TODO
    case _:
        print("We don't support Ubuntu " + release + "!")
        exit(0)
