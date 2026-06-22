#!/bin/bash
# Launcher — use Homebrew Python 3.11+ with Tk (NOT system python3 on macOS)
cd "$(dirname "$0")"
export TK_SILENCE_DEPRECATION=1

if [ -x "/opt/homebrew/bin/python3.11" ]; then
  exec /opt/homebrew/bin/python3.11 main.py "$@"
elif command -v python3.11 &>/dev/null; then
  exec python3.11 main.py "$@"
elif [ -x "/opt/homebrew/bin/python3" ]; then
  exec /opt/homebrew/bin/python3 main.py "$@"
else
  echo "Install: brew install python-tk@3.11"
  exec python3 main.py "$@"
fi
