#!/usr/bin/env bash
set -e

echo "Installing MCP server dependencies..."

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python install.py

echo "Installation complete. Restart Kiro / Amazon Q."
