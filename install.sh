#!/usr/bin/env bash
set -e

#!/bin/sh
set -e

# Function to detect Python command
detect_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        # Check if python points to Python 3
        if python -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" 2>/dev/null; then
            echo "python"
        else
            echo ""
        fi
    else
        echo ""
    fi
}

# Detect Python command
PYTHON_CMD=$(detect_python)

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3.6+ not found. Please install Python 3.6 or higher."
    echo "   Try: sudo apt update && sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"
"$PYTHON_CMD" --version

echo "Creating virtual environment..."
"$PYTHON_CMD" -m venv .venv

echo "Activating virtual environment..."
. .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running configuration..."
python install.py

echo "Installation complete! Please restart Kiro to load the new MCP servers."

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running configuration..."
python install.py

echo "Installation complete! Please restart Kiro to load the new MCP servers."
