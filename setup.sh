#!/usr/bin/env bash
# EduConnect Face App — one-line setup from terminal
# For double-click, use EduConnect-Face-Attendance.command instead
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install opencv-python opencv-contrib-python numpy Pillow requests
    pip install face_recognition
    pip install git+https://github.com/ageitgey/face_recognition_models
else
    source venv/bin/activate
fi

python gui_launcher.py "$@"
