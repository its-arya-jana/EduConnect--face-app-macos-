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
    echo "Installing face_recognition (includes dlib, face_recognition_models)..."
    echo "This may take 5-15 minutes — dlib is compiling from source."
    pip install face_recognition

    echo ""
    echo "Installing additional packages..."
    pip install opencv-python opencv-contrib-python numpy Pillow pymongo bcrypt

    echo ""
    echo "Patching face_recognition_models for Python 3.14+..."
    python3 patch_models.py 2>/dev/null || true

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
