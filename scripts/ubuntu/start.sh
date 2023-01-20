#!/usr/bin/env bash
apt update -y >/dev/null 2>/dev/null

echo "Installing python3-pip"
apt install python3-pip -y >/dev/null 2>/dev/null
echo "Installed python3-pip"

echo "Installing tqdm from pip"
python3 -m pip install tqdm
echo "Installed tqdm from pip"

echo "Installing python-apt from pip"
python3 -m pip install python-apt
echo "Installed python-apt from pip"

python3 main.py