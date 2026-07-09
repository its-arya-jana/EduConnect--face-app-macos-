#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install opencv-python opencv-contrib-python numpy Pillow pymongo bcrypt
    pip install face_recognition
    if command -v git &>/dev/null; then
        pip install git+https://github.com/ageitgey/face_recognition_models
    else
        pip install https://github.com/ageitgey/face_recognition_models/archive/refs/heads/master.zip
    fi
    python3 patch_models.py
fi

source venv/bin/activate
python gui_launcher.py "$@"
