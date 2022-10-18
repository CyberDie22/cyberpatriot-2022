import platform, os, time, subprocess, pwd, grp

def run(command):
    return subprocess.getoutput(command)

uname = platform.uname()

if "Ubuntu" in uname.version or "Debian" in uname.version:
    if os.geteuid() != 0:
        print("This script requires root privliges!")
        exit(-1)
    
    # update system

    os.system('apt-get update')
    os.system('apt-get upgrade')

    # get users

    UID_MIN = int(run("awk '/^UID_MIN/ {print $2}' /etc/login.defs"))
    UID_MAX = int(run("awk '/^UID_MAX/ {print $2}' /etc/login.defs"))
    ME = run("whoami")

    all_users = pwd.getpwall()
    users = []
    groups = grp.getgrall()
    sudo = None
    allowed_users = []

    for group in groups:
        if group.gr_name == 'sudo':
            sudo = group
    
    for user in all_users:
        if user.pw_uid in range(UID_MIN, UID_MAX):
            users.append(user.pw_name)

    print("Enter '$DONE$' to stop input")
    print("Enter all allowed administrators, enter you're name first")
    first = True
    useracc = ""
    while True:
        name = input("Admin Name: ")
        if name == '$DONE$':
            break
        allowed_users.append(name)
        if not name in users:
            os.system("adduser " + name)
            os.system("adduser " + name + " sudo")
        else:
            if not name in sudo.gr_mem:
                os.system("adduser " + name + " sudo")
        if first:
            useracc = name
            first = False

    for admin in sudo.gr_mem:
        if not admin in allowed_users:
            os.system("deluser " + admin + " sudo")

    print("Enter '$DONE$' to stop input")
    print("Enter all allowed regular users")
    while True:
        name = input("User Name: ")
        if name == '$DONE$':
            break
        allowed_users.append(name)
        if not name in users:
            os.system("adduser " + name)

    for user in users:
        if not user in allowed_users:
            os.system("deluser " + user)

    for user in allowed_users:
        if user == useracc: continue
        os.system("passwd " + user)

elif "Darwin" in uname.version:
    print("Darwin not supported!")
    exit(-1)
