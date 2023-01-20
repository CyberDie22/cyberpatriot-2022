#!/usr/bin/env bash
dnf update -y >/dev/null 2>/dev/null

echo "Installing python3-pip"
dnf install python3-pip -y >/dev/null 2>/dev/null
echo "Installed python3-pip"

echo "Installing tqdm from pip"
python3 -m pip install tqdm >/dev/null 2>/dev/null
echo "Installed tqdm from pip"

echo "Installing python-apt from pip"
python3 -m pip install python-apt >/dev/null 2>/dev/null
echo "Installed python-apt from pip"

python3 main.py