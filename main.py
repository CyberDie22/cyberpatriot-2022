import subprocess, platform

def run(command):
    return subprocess.getoutput(command)

uname = platform.uname()

print(uname)