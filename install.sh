#!/usr/bin/env bash
set -e

echo -e "\033[36m==========================================\033[0m"
echo -e "\033[32m  Installing YNCLI Autonomous AI Agent... \033[0m"
echo -e "\033[36m==========================================\033[0m"

# Check Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "\033[31m[ERROR] Python 3 is not installed.\033[0m"
    echo -e "Please install Python 3 (https://www.python.org/downloads/) and try again."
    exit 1
fi

echo -e "\033[36mInstalling yncli from PyPI...\033[0m"
$PYTHON_CMD -m pip install --upgrade yncli

echo -e "\n\033[32m[SUCCESS] YNCLI has been successfully installed!\033[0m"
echo -e "\033[33mType 'yncli' in your terminal to begin.\033[0m"
