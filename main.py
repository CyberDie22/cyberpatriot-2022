import subprocess, platform

def run(command):
    return subprocess.getoutput(command)

uname = platform.uname()

if uname.system == 'Linux':
    if "Ubuntu" in system.version:
        lsb_release = run('lsb_release -r').split(':').strip()
        print(lsb_release)
