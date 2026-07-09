#!/usr/bin/env bash
# EduConnect Face App — alternative one-line setup from terminal
# For double-click convenience, use EduConnect-Face-Attendance.command instead
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install opencv-python opencv-contrib-python numpy Pillow requests face_recognition
else
    source venv/bin/activate
fi

python gui_launcher.py "$@"
