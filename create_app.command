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
