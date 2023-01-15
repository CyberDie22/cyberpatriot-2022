#!/usr/bin/env bash
apt update
apt install python3-pip
python3 -m pip install tqdm
python3 main.py