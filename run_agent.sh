#!/bin/bash

# Define the path to the virtual environment python
VENV_PYTHON="$HOME/.venv/bin/python"

# Check if the virtual environment python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment python not found at $VENV_PYTHON"
    echo "Please ensure you have a virtual environment set up."
    exit 1
fi

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Run the agent
echo "Running Gmail Agent with: $VENV_PYTHON"
"$VENV_PYTHON" main.py "$@"
