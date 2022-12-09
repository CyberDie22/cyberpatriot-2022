import subprocess, platform, os

def run(command):
    return subprocess.getoutput(command)

uname = platform.uname()

if "Ubuntu" in uname.version:
    if os.geteuid() != 0:
        print("This script requires root privliges!")
        exit(1)

    lsb_release = run('lsb_release -r').split(':')[1].strip()
    if lsb_release == "22.04":
        print("Running on Ubuntu Linux 22.04")

        # print("\nUpdate System")
        # run('apt update -y')
        # run('apt upgrade -y')

        print("\nUpdate Users")
        UID_MIN = int(run("awk '/^UID_MIN/ {print $2}' /etc/login.defs"))
        UID_MAX = int(run("awk '/^UID_MAX/ {print $2}' /etc/login.defs"))
        ME = run("logname")

        print(UID_MIN, UID_MAX, ME)


else:
    print("Your system is not supported!")
    exit(0)