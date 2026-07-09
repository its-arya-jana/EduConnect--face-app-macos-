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
    pip install opencv-python opencv-contrib-python numpy Pillow requests
    pip install face_recognition

    echo ""
    echo "Installing face_recognition_models..."
    if command -v git &>/dev/null; then
        pip install git+https://github.com/ageitgey/face_recognition_models 2>&1
    else
        echo "Git not found — trying direct download..."
        python3 -c "
import urllib.request, zipfile, io, os, sys
url = 'https://github.com/ageitgey/face_recognition_models/archive/refs/heads/master.zip'
try:
    req = urllib.request.urlopen(url)
    z = zipfile.ZipFile(io.BytesIO(req.read()))
    z.extractall('/tmp/frm')
    sys.path.insert(0, '/tmp/frm/face_recognition_models-master')
    # Copy models to site-packages
    import site
    dest = os.path.join(site.getsitepackages()[0], 'face_recognition_models')
    if os.path.exists(dest):
        import shutil; shutil.rmtree(dest)
    os.rename('/tmp/frm/face_recognition_models-master/face_recognition_models', dest)
    print('face_recognition_models installed successfully')
except Exception as e:
    print(f'Failed: {e}')
    print('Please install git and run again, or run:')
    print('  xcode-select --install')
" 2>&1
    fi

    echo ""
    echo "Setup complete!"
else
    source venv/bin/activate
fi

echo ""
echo "Launching app..."
python gui_launcher.py

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "App exited with error code: $EXIT_CODE"
fi

echo ""
read -p "Press Enter to close this window..."
