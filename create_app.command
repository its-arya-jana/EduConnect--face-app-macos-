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
</dict>
</plist>
EOF

cat > "$APP_BUNDLE/Contents/MacOS/$APP_NAME" <<'EXEC'
#!/bin/bash
DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$DIR"

if [ ! -d "venv" ]; then
    clear
    echo "============================================"
    echo "  EduConnect Face Attendance — First-Time Setup"
    echo "============================================"
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate

    echo "Upgrading pip..."
    pip install --upgrade pip

    echo ""
    echo "Installing dependencies (this may take 5–15 minutes)..."
    pip install opencv-python opencv-contrib-python numpy Pillow requests face_recognition

    echo ""
    echo "Setup complete! Launching app..."
else
    source venv/bin/activate
fi

python gui_launcher.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Something went wrong. Try deleting the 'venv' folder and running again."
    read -p "Press Enter to close..."
fi
EXEC

chmod +x "$APP_BUNDLE/Contents/MacOS/$APP_NAME"

echo ""
echo "Done! Located at: $APP_BUNDLE"
echo ""
echo "On first launch, macOS may show a security warning."
echo "If so: Right-click the app → Open → click 'Open' in the dialog."
echo ""
echo "To remove the quarantine flag (prevents the warning entirely):"
echo "  xattr -d com.apple.quarantine '$APP_BUNDLE'"
