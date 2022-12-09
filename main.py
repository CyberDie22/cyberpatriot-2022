import subprocess, platform

def run(command):
    return subprocess.getoutput(command)

uname = platform.uname()

if uname.system == 'Linux':
    if "Ubuntu" in uname.version:
        lsb_release = run('lsb_release -r').split(':')[1].strip()
        print(lsb_release)
