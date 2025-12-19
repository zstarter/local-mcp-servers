#!/usr/bin/env bash
set -e

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

python install.py

echo "Installation complete. Restart Kiro / Amazon Q."
