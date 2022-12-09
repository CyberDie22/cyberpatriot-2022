import platform, os, time, subprocess, pwd, grp

def run(command):
    return subprocess.getoutput(command)

uname = platform.uname()

if "Ubuntu" in uname.version or "Debian" in uname.version:
    if os.geteuid() != 0:
        print("This script requires root privliges!")
        exit(-1)
    
    # update system

    os.system('apt-get update -y')
    os.system('apt-get upgrade -y')

    # install openscap dependencies

    # install unattended upgrades

    os.system("apt install unattended-upgrades -y")
    os.system("apt install update-notifier-common -y")


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
        print("Username: " + user)
        os.system("passwd " + user)

    # run openscap

    print("running openscap")
    os.system("oscap oval eval --results oscap_results.xml --report oscap_report.html com.ubuntu.xenial.cve.oval.xml")

    # enable firewall
    print("firewall")
    os.system("ufw enable")

    # do last
    os.system("firefox oscap_report.html &")

    ports_to_block = "20, 21, 23, 69, 135, 411, 412, 1080, 1194, 2302, 2745, 3074, 3124, 3127, 3128, 8080, 3306, 3724, 3784, 3785, 4333, 4444, 4664, 5004, 5005, 5500, 5554, 5800, 5900, 6112, 6500, 6699, 6881, 6882, 6883, 6884, 6885, 6886, 6887, 6888, 6889, 6890, 6891, 6892, 6893, 6894, 6895, 6896, 6897, 6898, 6999, 8767, 8866, 9898, 9988, 12035, 12036, 12345, 14567, 27015, 27374, 28960, 31337, 33434".split(", ")

    for port in ports_to_block:
        os.system("ufw deny " + port)

    # this won't work in 20.04
    # disable root login ssh
    os.system('sed "s/PermitRootLogin.*/PermitRootLogin no/g" /etc/ssh/ssh_config > /etc/ssh/ssh_config')

    # enable unattended upgrades
    os.system('sed "s/Unattended-Upgrade::Automatic-Reboot \"false\"/Unattended-Upgrade::Automatic-Reboot \"true\"/g" /etc/apt/apt.conf.d/50unattended-upgrades > /etc/apt/apt.conf.d/50unattended-upgrades')
    os.system('sed "s/APT::Periodic::Unattended-Upgrade \"0\";/APT::Periodic::Unattended-Upgrade \"1\";" /etc/apt/apt.conf.d/20auto-upgrades > /etc/apt/apt.conf.d/20auto-upgrades')

elif "Darwin" in uname.version:
    print("Darwin not supported!")
    exit(-1)

else:
    print("I don't recognize this OS")
    print(uname)
