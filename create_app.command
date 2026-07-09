#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="EduConnect-Face-Attendance"
APP_BUNDLE="$DIR/$APP_NAME.app"

echo "Creating $APP_NAME.app..."

mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

cat > "$APP_BUNDLE/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.educonnect.face-attendance</string>
    <key>CFBundleName</key>
    <string>EduConnect Face Attendance</string>
    <key>CFBundleDisplayName</key>
    <string>EduConnect Face Attendance</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

cat > "$APP_BUNDLE/Contents/MacOS/$APP_NAME" <<'EXEC'
#!/bin/bash
DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
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

if ! command -v pip3 &>/dev/null && ! python3 -m pip --version &>/dev/null; then
    echo "ERROR: pip is not installed."
    read -p "Press Enter to close..."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo ""
    echo "First-time setup: Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate

    echo "Upgrading pip..."
    pip install --upgrade pip

    echo ""
    echo "Installing opencv, numpy, Pillow, requests..."
    pip install opencv-python opencv-contrib-python numpy Pillow requests

    echo ""
    echo "Installing face_recognition..."
    pip install face_recognition

    echo ""
    echo "Installing face_recognition_models..."
    if command -v git &>/dev/null; then
        pip install git+https://github.com/ageitgey/face_recognition_models 2>&1
    else
        python3 -c "
import urllib.request, zipfile, io, os, sys, site
url = 'https://github.com/ageitgey/face_recognition_models/archive/refs/heads/master.zip'
try:
    req = urllib.request.urlopen(url)
    z = zipfile.ZipFile(io.BytesIO(req.read()))
    z.extractall('/tmp/frm')
    dest = os.path.join(site.getsitepackages()[0], 'face_recognition_models')
    if os.path.exists(dest):
        import shutil; shutil.rmtree(dest)
    os.rename('/tmp/frm/face_recognition_models-master/face_recognition_models', dest)
    print('face_recognition_models installed successfully')
except Exception as e:
    print(f'Failed: {e}')
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
    echo "Try deleting the 'venv' folder and running again."
fi

echo ""
read -p "Press Enter to close this window..."
EXEC

chmod +x "$APP_BUNDLE/Contents/MacOS/$APP_NAME"

echo ""
echo "Done! Located at: $APP_BUNDLE"
echo ""
echo "On first launch, macOS may show a security warning."
echo "If so: Right-click the app -> Open -> click 'Open' in the dialog."
echo ""
echo "To remove the warning permanently:"
echo "  xattr -d com.apple.quarantine '$APP_BUNDLE'"
