#!/usr/bin/python3

# Copyright (c) 2023, Ben Buzard
#
# SPDX-License-Identifier: MIT OR Apache-2.0

import platform
import subprocess, os, pwd, grp, crypt
from tqdm import tqdm

def run_with_output(command: [str]) -> int:
    return subprocess.check_call(command)


def run_get_output(command: [str]) -> str:
    return subprocess.check_output(command).decode()


def run(command: [str]):
    subprocess.check_output(command)


def install_packages(packages: str):
    print("Installing " + packages)
    run(["dnf", "update"])
    for package in packages.split(" "):
        run(["dnf", "install", package, "-y"])
    print("Finished installing " + packages)


def remove_package(package: str):
    print("Removing " + package)
    run(["dnf", "remove", package])


print("Running CyberPatriot 2022 Script on Ubuntu 22.04")

print("\nUpdating system...")
run(["dnf", "update"])
run(["dnf", "upgrade", "-y"])
print("\nDone updating system")

print("\nAudit users...")
with open("/etc/login.defs", "r") as f:
    for line in f.readlines():
        if line.startswith("UID_MIN"):
            UID_MIN = int(line.split(" ")[-1].strip())
        if line.startswith("UID_MAX"):
            UID_MAX = int(line.split(" ")[-1].strip())

ME = run_get_output("logname")

users = pwd.getpwall()
users = [x for x in users if x.pw_uid in range(UID_MIN, UID_MAX)]
user_names = [x.pw_name for x in users]

groups = grp.getgrall()
wheel_group = [x for x in groups if x.gr_name == 'wheel'][0]

if wheel_group is None:
    print("ERROR: group 'sudo' does not exist!")
    exit(1)

allowed_admins = input("Enter comma seperated list of admins: ").split(",")
allowed_users = input("Enter comma seperated list of users: ").split(",")
allowed_accounts = allowed_admins + allowed_users

for user in allowed_admins:
    if user not in user_names:
        run_with_output(["adduser", user])
    if user not in wheel_group.gr_mem:
        run(["adduser", user, "wheel"])

for user in wheel_group.gr_mem:
    if user not in allowed_admins:
        run(["deluser", "user", "wheel"])
        print("Removed user '" + user + "' from wheel group!")

for user in allowed_users:
    if user not in user_names:
        run_with_output(["adduser", user])
        print("Created user '" + user + "'!")

for user in user_names:
    if user not in allowed_accounts:
        run(["deluser", user])
        print("Deleted user '" + user + "'!")

users = pwd.getpwall()
users = [x for x in users if x.pw_uid in range(UID_MIN, UID_MAX)]
user_names = [x.pw_name for x in users]

groups = grp.getgrall()
wheel_group = [x for x in groups if x.gr_name == 'wheel'][0]

print("Finished user audit")

print("\nUpdating passwords...")

# FIXME: not secure, puts password in terminal
password = input("Set password: ")

hashed_password = crypt.crypt(password)

for user in user_names:
    if user == ME:
        continue

    run(["usermod", "-p", hashed_password, user])

print("Finished updating passwords")

print("\nEnabling firewall...")
install_packages("ufw")
run_with_output(["ufw", "enable"])
print("Finished enabling fireall")


print("\nBlocking non-essential ports...")
ports_to_block = "20, 21, 23, 69, 135, 411, 412, 1080, 1194, 2302, 2745, 3074, 3124, 3127, 3128, 8080, 3306, 3724, 3784, 3785, 4333, 4444, 4664, 5004, 5005, 5500, 5554, 5800, 5900, 6112, 6500, 6699, 6881, 6882, 6883, 6884, 6885, 6886, 6887, 6888, 6889, 6890, 6891, 6892, 6893, 6894, 6895, 6896, 6897, 6898, 6999, 8767, 8866, 9898, 9988, 12035, 12036, 12345, 14567, 27015, 27374, 28960, 31337, 33434".split(", ")
for port in tqdm(ports_to_block, desc="ports"):
    run(["ufw", "deny", port])
print("Done blocking non-essential ports, you should reenable needed ports!")

print("\nEnabling unattended upgrades...")
install_packages("dnf-automatic")
run(["systemctl", "enable", "--now", "dnf-automatic-install.timer"])
print("Finished enabling unattended upgrades...")

print("\nDisabling ssh root login and ssh X11 forwarding...")
with open("/etc/ssh/sshd_config", "r") as f:
    text = f.readlines()
with open("/etc/ssh/sshd_config", "w") as f:
    newtext = []
    for line in text:
        if "PermitRootLogin" in line:
            newtext.append("PermitRootLogin no")
        elif "X11Forwarding" in line:
            newtext.append("X11Forwarding no")
        else:
            newtext.append(line)
    f.writelines(newtext)
print("Disabled ssh root login and ssh X11 forwarding")

print("\nUpdate password aging...")
with open("/etc/login.defs", "r") as f:
    text = f.readlines()
with open("/etc/login.defs", "w") as f:
    newtext = []
    for line in text:
        if "PASS_MIN_DAYS" in line:
            newtext.append("PASS_MIN_DAYS\t1\n")
        elif "PASS_MAX_DAYS" in line:
            newtext.append("PASS_MAX_DAYS\t30\n")
        elif "PASS_WARN_DAYS" in line:
            newtext.append("PASS_WARN_DAYS\t7\n")
        else:
            newtext.append(line)
    f.writelines(newtext)
print("Updated password aging")

# TODO: doesn't seem to exist, maybe find and add?
# print("\nUpdating password quality settings")
# install_packages("libpam-pwquality")
# with open("/etc/pam.d/common-password", "r") as f:
#     text = f.readlines()
# with open("/etc/pam.d/common-password", "w") as f:
#     newtext = []
#     for line in text:
#         if "pam_pwquality.so" in line:
#             newtext.append("password requisite pam_pwquality.so retry=3 minlen=10 dcredit=-2 ucredit=-2 lcredit=-2 ocredit=-2\n")
#         elif "pam_unix.so" in line:
#             newtext.append("password [success=1 default=ignore] pam_unix.so obscure use_authtok try_first_pass sha512 remember=5\n")
#         elif "pam_deny.so" in line:
#             newtext.append("password requisite pam_deny.so\n")
#         elif "pam_permit.so" in line:
#             newtext.append("password required pam_permit.so\n")
#         elif "pam_gnome_keyring.so" in line:
#             newtext.append("password optional pam_gnome_keyring,so\n")
#         else:
#             newtext.append(line)
#     f.writelines(text)
# print("Updated password quality settings")

print("\nUpdating password aging settings for users")
for user in user_names:
    run(["chage", "--mindays", "1", "--maxdays", "30", "--warndays", "7", user])
print("Updated password aging settings for users")

print("\nFix /etc/sudoers.d/ ...")
files = os.listdir("/etc/sudoers.d")
for file in files:
    if file != "README":
        os.remove("/etc/sudoers.d/" + file)
print("Fixed /etc/sudoers.d/")

print("\nCheck installed packages... (too tired to impl right now, just check manually with dnf list installed :^))")
print("Finished checking installed packages")
# print("\nCheck installed packages...")
# with open("packages.txt", "r") as f:
#     default_packages = [x.strip() for x in f.readlines() if x.strip() != ""]
# packages = cache.keys()
# packages = [x for x in packages if cache[x].is_installed]
#
# non_default_packages = [x for x in packages if x not in default_packages]
# non_default_packages = [x for x in non_default_packages if not cache[x].essential]
#
# for (idx, package) in enumerate(non_default_packages):
#     print(chr(27) + "[H" + chr(27) + "[J")
#     print("Package (" + str(idx) + "/" + str(len(non_default_packages)) + "): " + package)
#     print("Description: " + cache[package].versions[0].description)
#     okay = True if input("Is this package okay (Y/N)? ") == "Y" else False
#     if not okay:
#         sure = True if input("Are you sure (Y/N)? ") == "Y" else False
#         if sure:
#             remove_package(package)
# print("Finished checking installed packages")

print("\nRun clamav")
# FIXME: this only runs on x86-64
match platform.uname().machine:
    case "x86_64":
        run(["apt", "install", "./clamav-1.0.0.linux.x86_64.rpm", "-y"])
        run(["rm", "-rf", "/var/log/clamav/freshclam.log"])
        run_with_output(["freshclam"])
        run_with_output(["clamscan", "--infected", "--recursive", "/"])
        run_with_output(["clamscan", "--memory"])
    case _:
        print("We don't support running clamav on " + platform.uname().machine + " at this time!")
print("Finished running clamav (remove the infected files manually)")

print("\nRun openscap script")
run_with_output(["bash", "fedora-script-standard.sh"])
run_with_output(["bash", "firefox-script-stig.sh"])
print("Finished running openscap script")
