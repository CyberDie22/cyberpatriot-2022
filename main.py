import subprocess, platform, os

def run(command):
    out = subprocess.getoutput(command)
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
        print("Running on Ubuntu Linux 22.04")

        # print("\nUpdate System")
        # run('apt update -y')
        # run('apt upgrade -y')

        print("\nUpdate Users")
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

        for user in allowed_users:
            if not user in users:
                run('adduser ' + user)

        for user in users:
            if not user in all_allowed_users:
                run('deluser ' + user)

        for user in all_allowed_users:
            if user == ME: continue

            while True:
                print('Username: ' + user)
                output = run('passwd ' + user)
                if 'passwd: password unchanged' not in output:
                    break
        



else:
    print("Your system is not supported!")
    exit(0)