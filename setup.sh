#!/usr/bin/env bash
set -euo pipefail

APP_NAME="EduConnect Face Recognition"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo "  $APP_NAME - Setup"
echo "========================================"
echo ""

OS="$(uname -s)"
echo "Detected OS: $OS"

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "ERROR: Python 3 not found. Please install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

echo "Using Python: $($PYTHON --version)"

if [ "$OS" = "Darwin" ]; then
    echo ""
    echo "[macOS] Checking Homebrew..."
    if ! command -v brew &>/dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    echo "[macOS] Installing cmake (required for dlib)..."
    brew install cmake
elif [ "$OS" = "Linux" ]; then
    echo "[Linux] Installing system packages..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3-pip python3-tk cmake build-essential
fi

echo ""
echo "Creating virtual environment..."
cd "$SCRIPT_DIR"
$PYTHON -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing Python packages (this may take a while)..."
echo "  Step 1/3: numpy, opencv, Pillow, requests..."
pip install opencv-python opencv-contrib-python numpy Pillow requests

echo ""
echo "  Step 2/3: Installing face_recognition (includes dlib compile)..."
echo "  This may take 5-10 minutes..."
pip install face_recognition

echo ""
echo "Verifying installation..."
$PYTHON -c "
import cv2, numpy, PIL, requests, face_recognition
print('  opencv:', cv2.__version__)
print('  numpy:', numpy.__version__)
print('  Pillow:', PIL.__version__)
print('  requests:', requests.__version__)
print('  face_recognition:', face_recognition.__version__)
print('')
print('  All packages installed successfully!')
"

echo ""
echo "Creating launcher script..."
LAUNCHER="$SCRIPT_DIR/run.sh"
cat > "$LAUNCHER" << 'EOF'
#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
source "$DIR/venv/bin/activate"
python3 gui_launcher.py "$@"
EOF
chmod +x "$LAUNCHER"

echo ""
echo "========================================"
echo "  Setup complete!"
echo "========================================"
echo ""
echo "To run the app:"
echo "  ./run.sh"
echo ""
echo "Or with options:"
echo "  ./run.sh --class-id <ID> --auth-token <TOKEN> --date YYYY-MM-DD"
echo ""
