#!/bin/sh

set -e

# on debian:
# sudo apt install python3.13-venv

python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt

sed "s/placeholder_user/$USER/" <anti-spam-bot.service \
  | sed "s|placeholder_dir|$PWD|" \
  | sudo tee /etc/systemd/system/anti-spam-bot.service
sudo systemctl daemon-reload

sudo systemctl enable --now anti-spam-bot.service
