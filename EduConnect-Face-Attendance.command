#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

clear
echo "============================================"
echo "  EduConnect Face Attendance"
echo "============================================"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Download from: https://www.python.org/downloads/"
    read -p "Press Enter to close..."
    exit 1
fi
echo "Python: $(python3 --version)"

if [ ! -d "venv" ]; then
    echo ""
    echo "First-time setup: Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate

    echo "Upgrading pip..."
    pip install --upgrade pip

    echo ""
    echo "Installing packages..."
    pip install opencv-python opencv-contrib-python numpy Pillow cloudscraper
    pip install face_recognition

    echo ""
    echo "Installing face_recognition_models..."
    if command -v git &>/dev/null; then
        pip install git+https://github.com/ageitgey/face_recognition_models 2>&1
    else
        pip install https://github.com/ageitgey/face_recognition_models/archive/refs/heads/master.zip 2>&1
    fi

    echo ""
    echo "Patching models for Python compatibility..."
    python3 patch_models.py
    if [ $? -ne 0 ]; then
        echo "Patch failed — app may not work correctly."
        read -p "Press Enter to close..."
        exit 1
    fi

    echo ""
    echo "Setup complete!"
else
    source venv/bin/activate
fi

echo ""
echo "Launching app..."
python3 gui_launcher.py

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "App exited with error code: $EXIT_CODE"
fi

echo ""
read -p "Press Enter to close this window..."
