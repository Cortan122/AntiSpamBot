#!/bin/sh

set -e

cd -- "$(dirname -- "$0")"
. ./venv/bin/activate
python bot.py
