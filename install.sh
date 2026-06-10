#!/bin/sh

set -e

python -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt

sed "s/placeholder_user/$USER/" <anti-spam-bot.service \
  | sed "s/placeholder_dir/$PWD/" \
  | sudo tee /etc/systemd/system/anti-spam-bot.service
sudo systemctl daemon-reload
