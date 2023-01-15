import subprocess, platform, os
from tqdm import tqdm


def run(command):
    return subprocess.getoutput(command)


def run_print(command):
    out = run(command)
    print(out)
    return out


uname = platform.uname()

if "Ubuntu" in uname.version:
    import pwd, grp

    if os.geteuid() != 0:
        print("This script requires root privliges!")
        exit(1)

    lsb_release = run('lsb_release -r').split(':')[1].strip()
    if lsb_release == "22.04":
        def install_packages(packages):
            print("Installing " + packages)
            run('apt update -y')
            run('apt install -y ' + packages)
            print("Finished installing " + packages)
        def start_service(service):
            run('systemctl start ' + service)
        print("Running on Ubuntu Linux 22.04")

        print("\nUpdate System...")
        run('apt update -y')
        run('apt upgrade -y')
        print("\nDone updating system")

        print("\nAudit Users...")
        UID_MIN = int(run("awk '/^UID_MIN/ {print $2}' /etc/login.defs"))
        UID_MAX = int(run("awk '/^UID_MAX/ {print $2}' /etc/login.defs"))
        ME = run("logname")

        all_users = pwd.getpwall()
        users = []
        groups = grp.getgrall()
        sudo_group = None

        for group in groups:
            if group.gr_name == 'sudo':
                sudo_group = group
                break
        if sudo_group is None:
            print("ERROR: 'sudo' group does not exist!")
            exit(1)

        for user in all_users:
            if user.pw_uid in range(UID_MIN, UID_MAX):
                users.append(user.pw_name)

        allowed_admins_input = input("Enter comma seperated list of admins: ")
        allowed_users_input = input("Enter comma seperated list of users: ")

        allowed_admins = allowed_admins_input.split(",")
        allowed_users = allowed_users_input.split(",")
        all_allowed_users = allowed_users + allowed_admins

        for user in allowed_admins:
            if not user in users:
                run('adduser ' + user)
            if not user in sudo_group.gr_mem:
                run('adduser ' + user + ' sudo')

        for user in sudo_group.gr_mem:
            if not user in allowed_admins:
                run('deluser ' + user + ' sudo')
                print("Removed user '" + user + "' from sudo group!")

        for user in allowed_users:
            if not user in users:
                run('adduser ' + user)
                print("Created user '" + user + "'!")

        for user in users:
            if not user in all_allowed_users:
                run('deluser ' + user)
                print("Deleted user '" + user + "'!")
        print("Finished user audit")

        print("Updating passwords...")
        all_allowed_users.append("root")
        for user in all_allowed_users:
            if user == ME: continue

            while True:
                print('Username: ' + user)
                print('Password: ')
                output = run('passwd ' + user)
                if 'passwd: password unchanged' not in output:
                    break
        all_allowed_users.pop()
        print("Done updating passwords")

        print("Enable firewall...")
        run('ufw enable')
        print("Finished enabling firewall")

        print("Blocking non-essential ports...")
        ports_to_block = "20, 21, 23, 69, 135, 411, 412, 1080, 1194, 2302, 2745, 3074, 3124, 3127, 3128, 8080, 3306, 3724, 3784, 3785, 4333, 4444, 4664, 5004, 5005, 5500, 5554, 5800, 5900, 6112, 6500, 6699, 6881, 6882, 6883, 6884, 6885, 6886, 6887, 6888, 6889, 6890, 6891, 6892, 6893, 6894, 6895, 6896, 6897, 6898, 6999, 8767, 8866, 9898, 9988, 12035, 12036, 12345, 14567, 27015, 27374, 28960, 31337, 33434".split(", ")
        for port in tqdm(ports_to_block, desc="ports"):
            run('ufw deny ' + port)
        print("Done blocking non-essential ports, you should reenable needed ports!")

        print("Enable unattended upgrades...")
        install_packages("unattended-upgrades")
        start_service("unattended-upgrades")
        print("Finished enabling unattended upgrades")

        print("Disable ssh root login...")
        run("sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config")
        run("sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config")
        print("Disabled ssh root login")

        print("Disable ssh X11 forwarding...")
        run("sed -i 's/X11Forwarding yes/X11Forwarding no/' /etc/ssh/sshd_config")
        print("Disabled ssh X11 forwarding")

        print("Update password aging...")
        run("sed -i '/PASS_MIN_DAYS/s/.*/PASS_MIN_DAYS    1' /etc/login.defs")
        run("sed -i '/PASS_MAX_DAYS/s/.*/PASS_MAX_DAYS    30' /etc/login.defs")
        run("sed -i '/PASS_WARN_DAYS/s/.*/PASS_WARN_DAYS    7' /etc/login.defs")
        print("Updated password aging")

        print("Update password quality settings")
        # sed '/match/s/.*/replacement/' file
        run("sed -i '/pam_pwquality.so/s/.*/password requisite pam_pwquality.so retry=3 minlen=10 dcredit=-2 ucredit=-2 lcredit=-2 ocredit=-2/' /etc/pam.d/common-password")
        run("sed -i '/pam_unix.so/s/.*/password [success=1 default=ignore] pam_unix.so obscure use_authtok try_first_pass sha512 remember=5/' /etc/pam.d/common-password")
        run("sed -i '/pam_deny.so/s/.*/password requisite pam_deny.so' /etc/pam.d/common-password")
        run("sed -i '/pam_deny.so/s/.*/password required pam_permit.so' /etc/pam.d/common-password")
        run("sed -i '/pam_deny.so/s/.*/password optional pam_gnome_keyring.so' /etc/pam.d/common-password")
        print("Updated password quality settings")
        
        print("Fix /etc/sudoers.d/ ...")
        files = os.listdir("/etc/sudoers.d")
        for file in files:
            if file != "README":
                os.remove("/etc/sudoers.d/" + file)
        print("Fixed /etc/sudoers.d/")

        # LAST
        print("Run clamav")
        install_packages("clamav libclamunrar9")
        run_print("freshclam")
        run_print("clamscan --infected --recursive /")
        run_print("clamscan --memory")
        print("Finished clamav")

        # LAST
        print("Run openscap script")
        run_print("bash ./ubuntu2204-script-cis_level2_workstation.sh")
        run_print("bash ./firefox-script-stig.sh")
        print("Finished running openscap scripts")

    elif lsb_release == "20.04":
        def install_packages(packages):
            print("Installing " + packages)
            run('apt update -y')
            run('apt install -y ' + packages)
            print("Finished installing " + packages)
        def start_service(service):
            run('systemctl start ' + service)
        print("Running on Ubuntu Linux 20.04")

        # print("\nUpdate System...")
        # run('apt update -y')
        # run('apt upgrade -y')
        # print("\nDone updating system")

        print("\nAudit Users...")
        UID_MIN = int(run("awk '/^UID_MIN/ {print $2}' /etc/login.defs"))
        UID_MAX = int(run("awk '/^UID_MAX/ {print $2}' /etc/login.defs"))
        ME = run("logname")

        all_users = pwd.getpwall()
        users = []
        groups = grp.getgrall()
        sudo_group = None

        for group in groups:
            if group.gr_name == 'sudo':
                sudo_group = group
                break
        if sudo_group is None:
            print("ERROR: 'sudo' group does not exist!")
            exit(1)

        for user in all_users:
            if user.pw_uid in range(UID_MIN, UID_MAX):
                users.append(user.pw_name)

        allowed_admins_input = input("Enter comma seperated list of admins: ")
        allowed_users_input = input("Enter comma seperated list of users: ")

        allowed_admins = allowed_admins_input.split(",")
        allowed_users = allowed_users_input.split(",")
        all_allowed_users = allowed_users + allowed_admins

        for user in allowed_admins:
            if not user in users:
                run('adduser ' + user)
            if not user in sudo_group.gr_mem:
                run('adduser ' + user + ' sudo')

        for user in sudo_group.gr_mem:
            if not user in allowed_admins:
                run('deluser ' + user + ' sudo')
                print("Removed user '" + user + "' from sudo group!")

        for user in allowed_users:
            if not user in users:
                run('adduser ' + user)
                print("Created user '" + user + "'!")

        for user in users:
            if not user in all_allowed_users:
                run('deluser ' + user)
                print("Deleted user '" + user + "'!")
        print("Finished user audit")

        print("Updating passwords...")
        all_allowed_users.append("root")
        for user in all_allowed_users:
            if user == ME: continue

            while True:
                print('Username: ' + user)
                print('Password: ')
                output = run('passwd ' + user)
                if 'passwd: password unchanged' not in output:
                    break
        all_allowed_users.pop()
        print("Done updating passwords")

        print("Enable firewall...")
        run('ufw enable')
        print("Finished enabling firewall")

        print("Blocking non-essential ports...")
        ports_to_block = "20, 21, 23, 69, 135, 411, 412, 1080, 1194, 2302, 2745, 3074, 3124, 3127, 3128, 8080, 3306, 3724, 3784, 3785, 4333, 4444, 4664, 5004, 5005, 5500, 5554, 5800, 5900, 6112, 6500, 6699, 6881, 6882, 6883, 6884, 6885, 6886, 6887, 6888, 6889, 6890, 6891, 6892, 6893, 6894, 6895, 6896, 6897, 6898, 6999, 8767, 8866, 9898, 9988, 12035, 12036, 12345, 14567, 27015, 27374, 28960, 31337, 33434".split(", ")
        for port in tqdm(ports_to_block, desc="ports"):
            run('ufw deny ' + port)
        print("Done blocking non-essential ports, you should reenable needed ports!")

        print("Enable unattended upgrades...")
        install_packages("unattended-upgrades")
        start_service("unattended-upgrades")
        print("Finished enabling unattended upgrades")

        print("Disable ssh root login...")
        run("sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config")
        run("sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config")
        print("Disabled ssh root login")

        print("Disable ssh X11 forwarding...")
        run("sed -i 's/X11Forwarding yes/X11Forwarding no/' /etc/ssh/sshd_config")
        print("Disabled ssh X11 forwarding")

        print("Update password aging...")
        run("sed -i '/PASS_MIN_DAYS/s/.*/PASS_MIN_DAYS    1' /etc/login.defs")
        run("sed -i '/PASS_MAX_DAYS/s/.*/PASS_MAX_DAYS    30' /etc/login.defs")
        run("sed -i '/PASS_WARN_DAYS/s/.*/PASS_WARN_DAYS    7' /etc/login.defs")
        print("Updated password aging")

        print("Update password quality settings")
        # sed '/match/s/.*/replacement/' file
        run("sed -i '/pam_pwquality.so/s/.*/password requisite pam_pwquality.so retry=3 minlen=10 dcredit=-2 ucredit=-2 lcredit=-2 ocredit=-2/' /etc/pam.d/common-password")
        run("sed -i '/pam_unix.so/s/.*/password [success=1 default=ignore] pam_unix.so obscure use_authtok try_first_pass sha512 remember=5/' /etc/pam.d/common-password")
        run("sed -i '/pam_deny.so/s/.*/password requisite pam_deny.so' /etc/pam.d/common-password")
        run("sed -i '/pam_deny.so/s/.*/password required pam_permit.so' /etc/pam.d/common-password")
        run("sed -i '/pam_deny.so/s/.*/password optional pam_gnome_keyring.so' /etc/pam.d/common-password")
        print("Updated password quality settings")
        
        print("Fix /etc/sudoers.d/ ...")
        files = os.listdir("/etc/sudoers.d")
        for file in files:
            if file != "README":
                os.remove("/etc/sudoers.d/" + file)
        print("Fixed /etc/sudoers.d/")

        # LAST
        print("Run clamav")
        install_packages("clamav libclamunrar9")
        run_print("freshclam")
        run_print("clamscan --infected --recursive /")
        run_print("clamscan --memory")
        print("Finished clamav")

        # LAST
        print("Run openscap script")
        run_print("bash ./ubuntu2004-script-cis_level2_workstation.sh")
        run_print("bash ./firefox-script-stig.sh")
        print("Finished running openscap scripts")
else:
    print(uname)
    print("Your system is not supported!")
    exit(0)
