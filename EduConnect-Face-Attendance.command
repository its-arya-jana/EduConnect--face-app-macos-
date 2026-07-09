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
    echo ""
    echo "Download from: https://www.python.org/downloads/"
    echo "Make sure to check 'Add Python to PATH' during installation."
    echo ""
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
    echo "Installing packages (5-15 minutes)..."
    pip install opencv-python opencv-contrib-python numpy Pillow requests face_recognition

    echo ""
    echo "Setup complete!"
else
    source venv/bin/activate
fi

echo ""
echo "Launching app..."
python gui_launcher.py

echo ""
echo "App closed."
read -p "Press Enter to close this window..."
