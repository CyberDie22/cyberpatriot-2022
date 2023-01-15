#!/usr/bin/python3

import subprocess, os, pwd, grp, crypt


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
user_names = list(map(lambda x: x.pw_name, users))

groups = grp.getgrall()
sudo_group = list(filter(lambda x: x.gr_name == 'sudo', groups))[0]

if sudo_group is None:
    print("ERROR: group 'sudo' does not exist!")
    exit(1)

allowed_admins = input("Enter comma seperated list of admins: ").split(",")
allowed_users = input("Enter comma seperated list of users: ").split(",")
allowed_accounts = allowed_admins + allowed_users

for user in allowed_admins:
    if user not in user_names:
        run(["adduser", "--disabled-login", user])
    if user not in sudo_group.gr_mem:
        run(["adduser", user, "sudo"])

for user in sudo_group.gr_mem:
    if user not in allowed_admins:
        run(["deluser", "user", "sudo"])
        print("Removed user '" + user + "' from sudo group!")

for user in allowed_users:
    if user not in user_names:
        run(["adduser", "--disabled-login", user])
        print("Created user '" + user + "'!")

for user in users:
    if user not in allowed_accounts:
        run(["deluser", user])
        print("Deleted user '" + user + "'!")

users = pwd.getpwall()
users = list(filter(lambda x: x.pw_uid in range(UID_MIN, UID_MAX), users))
user_names = list(map(lambda x: x.pw_name, users))

groups = grp.getgrall()
sudo_group = list(filter(lambda x: x.gr_name == 'sudo', groups))[0]

print("Finished user audit")

print("Updating passwords...")

# FIXME: not secure, puts password in terminal
password = input("Set password: ")

hashed_password = crypt.crypt(password)

for user in user_names:
    if user == ME:
        continue

    run(["usermod", "-p", hashed_password, user])

print("Finished updating passwords")

print("Enabling firewall...")
run(["ufw", "enable"])
print("Finished enabling fireall")


print("Blocking non-essential ports...")
ports_to_block = "20, 21, 23, 69, 135, 411, 412, 1080, 1194, 2302, 2745, 3074, 3124, 3127, 3128, 8080, 3306, 3724, 3784, 3785, 4333, 4444, 4664, 5004, 5005, 5500, 5554, 5800, 5900, 6112, 6500, 6699, 6881, 6882, 6883, 6884, 6885, 6886, 6887, 6888, 6889, 6890, 6891, 6892, 6893, 6894, 6895, 6896, 6897, 6898, 6999, 8767, 8866, 9898, 9988, 12035, 12036, 12345, 14567, 27015, 27374, 28960, 31337, 33434".split(", ")
for port in tqdm(ports_to_block, desc="ports"):
    run('ufw deny ' + port)
print("Done blocking non-essential ports, you should reenable needed ports!")

print("Enabling unattended upgrades...")
install_packages("unattended-upgrades update-notifier-common")
print("Finished enabling unattended upgrades...")
