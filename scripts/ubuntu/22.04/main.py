#!/usr/bin/python3
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
    run(["apt", "update", "-y"])
    run(["apt", "install", "-y"] + packages.split(" "))
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

for user in user_names:
    if user not in allowed_accounts:
        run(["deluser", user])
        print("Deleted user '" + user + "'!")

users = pwd.getpwall()
users = list(filter(lambda x: x.pw_uid in range(UID_MIN, UID_MAX), users))
user_names = list(map(lambda x: x.pw_name, users))

groups = grp.getgrall()
sudo_group = list(filter(lambda x: x.gr_name == 'sudo', groups))[0]

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
run_with_output(["ufw", "enable"])
print("Finished enabling fireall")


print("\nBlocking non-essential ports...")
ports_to_block = "20, 21, 23, 69, 135, 411, 412, 1080, 1194, 2302, 2745, 3074, 3124, 3127, 3128, 8080, 3306, 3724, 3784, 3785, 4333, 4444, 4664, 5004, 5005, 5500, 5554, 5800, 5900, 6112, 6500, 6699, 6881, 6882, 6883, 6884, 6885, 6886, 6887, 6888, 6889, 6890, 6891, 6892, 6893, 6894, 6895, 6896, 6897, 6898, 6999, 8767, 8866, 9898, 9988, 12035, 12036, 12345, 14567, 27015, 27374, 28960, 31337, 33434".split(", ")
for port in tqdm(ports_to_block, desc="ports"):
    run(["ufw", "deny", port])
print("Done blocking non-essential ports, you should reenable needed ports!")

print("\nEnabling unattended upgrades...")
install_packages("unattended-upgrades update-notifier-common")

with open("/etc/apt/apt.conf.d/50unattended-upgrades", "r") as f:
    text = f.read()
with open("/etc/apt/apt.conf.d/50unattended-upgrades", "w") as f:
    text = text.replace("//Unattended-Upgrade::Automatic-Reboot \"false\";", "Unattended-Upgrade::Automatic-Reboot \"true\";")
    text = text.replace("//Unattended-Upgrade::Automatic-Reboot-WithUsers \"true\";", "Unattended-Upgrade::Automatic-Reboot-WithUsers \"true\";")
    f.write(text)
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
            newtext.append("PASS_MIN_DAYS\t1")
        elif "PASS_MAX_DAYS" in line:
            newtext.append("PASS_MAX_DAYS\t30")
        elif "PASS_WARN_DAYS" in line:
            newtext.append("PASS_WARN_DAYS\t7")
        else:
            newtext.append(line)
    f.writelines(newtext)
print("Updated password aging")

print("\nUpdating password quality settings")
install_packages("libpam-pwquality")
with open("/etc/pam.d/common-password", "r") as f:
    text = f.readlines()
with open("/etc/pam.d/common-password", "w") as f:
    newtext = []
    for line in text:
        if "pam_pwquality.so" in line:
            newtext.append("password requisite pam_pwquality.so retry=3 minlen=10 dcredit=-2 ucredit=-2 lcredit=-2 ocredit=-2")
        elif "pam_unix.so" in line:
            newtext.append("password [success=1 default=ignore] pam_unix.so obscure use_authtok try_first_pass sha512 remember=5")
        elif "pam_deny.so" in line:
            newtext.append("password requisite pam_deny.so")
        elif "pam_permit.so" in line:
            newtext.append("password required pam_permit.so")
        elif "pam_gnome_keyring.so" in line:
            newtext.append("password optional pam_gnome_keyring,so")
        else:
            newtext.append(line)
    f.writelines(text)
print("Updated password quality settings")

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

print("\nCheck installed packages...")
with open("packages.txt", "r") as f:
    default_packages = f.readlines()
packages = run_get_output(["apt", "list", "--installed"]).split("\n")
print(packages)
print(default_packages)

print("\nRun clamav")
print(platform.uname())
# FIXME: this only runs on x86-64
# run(["apt", "install", "./clamav-1.0.0.linux.x86_64.deb", "-y"])
# run(["rm", "-rf", "/var/log/clamav/freshclam.log"])
# run_with_output(["freshclam"])
# run_with_output(["clamscan", "--infected", "--recursive", "/"])
# run_with_output(["clamscan", "--memory"])
print("Finished running clamav (remove the infected files manually)")

print("\nRun openscap script")
run_with_output(["bash", "ubuntu2204-script-cis_level2_workstation.sh"])
run_with_output(["bash", "firefox-script-stig.sh"])
print("Finished running openscap script")
