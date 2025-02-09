#!/usr/bin/python3

import platform, subprocess, os


def run(command: [str]) -> int:
    return subprocess.check_call(command)


def run_with_output(command: [str]) -> str:
    return subprocess.check_output(command).decode()


release = run_with_output(["lsb_release", "-r"]).split("\t")[-1].strip()

match release:
    case "22.04":
        os.chdir(os.getcwd() + "/22.04")

        run(["/bin/bash", "start.sh"])
        # TODO
    case _:
        print("We don't support Ubuntu " + release + "!")
        exit(0)
