#!/usr/bin/env bash

brew bundle
rm -rf ./.venv
rm -rf movielog.egg-info
python3 -m venv ./.venv
source ./.venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
which python3
pip install -e .
