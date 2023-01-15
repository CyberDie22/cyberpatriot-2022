#!/usr/bin/env bash
apt update -y
apt install python3-pip -y
python3 -m pip install tqdm
python3 main.py