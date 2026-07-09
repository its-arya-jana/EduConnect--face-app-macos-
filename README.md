# EduConnect Face Recognition App

Desktop face recognition attendance system for **EduConnect** web portal. Teachers launch this app from their computer to mark student attendance using a webcam.

## Features

- Face detection and recognition using `face_recognition` (dlib)
- Liveness detection (blink detection to prevent photo spoofing)
- Real-time scanner with student roster overlay
- Auto-syncs attendance to EduConnect web portal
- Works offline — syncs when connected

## Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Webcam** (built-in or USB)
- **EduConnect teacher account** with active classes
- **macOS** or **Linux** or **Windows 10/11**

> **Note:** `dlib` / `face_recognition` compilation can take 5–15 minutes during first install.

---

## Setup

### macOS

```bash
# 1. Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install cmake (required for dlib)
brew install cmake

# 3. Run setup script
bash setup.sh
```

### Linux (Ubuntu/Debian)

```bash
# 1. Install system packages
sudo apt update
sudo apt install -y python3-pip python3-tk cmake build-essential

# 2. Run setup script
bash setup.sh
```

### Windows

```cmd
REM Simply double-click setup.bat
REM Or run from Command Prompt:
setup.bat
```

> On Windows, you may need **Visual Studio Build Tools** for dlib compilation. Download from: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022 (select "Desktop development with C++").

---

## Usage

### One-click launch (recommended)

**macOS:** Double-click `EduConnect-Face-Attendance.app` (looks like a real Mac app).

If macOS blocks it with "not verified" warning:
> **Right-click** the app → **Open** → click **Open** in the dialog.
> This is only needed once — after that, normal double-click works.

Or use Terminal once to remove the warning permanently:
```bash
xattr -d com.apple.quarantine EduConnect-Face-Attendance.app
```

**Windows:** Double-click `EduConnect-Face-Attendance.bat`.

The first time you run it, it automatically installs everything (Python packages, dependencies) — takes 5–15 minutes. After that, it launches instantly.

### Launch from Terminal

```bash
# macOS / Linux
./EduConnect-Face-Attendance.command

# or directly with python:
python gui_launcher.py
```

### From EduConnect Portal (recommended)

1. Log in to EduConnect as a **Teacher**
2. Go to **Attendance** section
3. Select a **Subject** and **Date**
4. Click **Mark Attendance**
5. The app opens with the class pre-loaded
6. Students look at the camera and blink to verify attendance
7. Attendance syncs to the portal in real time

### First-time setup in the app

1. **Training tab** — Select a student → click **Capture 30 Photos** → click **Train Model**
2. Repeat for all students in the class
3. Go to **Scanner tab** → click **START SCANNER** to begin face recognition

---

## How it works

- **No configuration needed.** The app automatically detects your EduConnect server (production at `educonnect.onrender.com` or local at `localhost:5002`).
- **Just log in** with your existing EduConnect teacher email and password.
- The app detects the server URL on startup and saves it for next time.

---

## Project Structure

```
EduConnect-Face-App/
├── EduConnect-Face-Attendance.command  # macOS launcher (double-click)
├── EduConnect-Face-Attendance.bat      # Windows launcher (double-click)
├── gui_launcher.py                     # Entry point
├── department_attendance_app.py        # Main Tkinter GUI
├── face_recognizer.py                  # Face detection / recognition
├── database.py                         # Local SQLite operations
├── student_mapper.py                   # Face ID ↔ EduConnect ID mapping
├── educonnect_config.json              # Auto-detected; no manual edits needed
├── student_mapping.json                # Auto-generated ID mappings
├── requirements.txt                    # Python dependencies
├── setup.sh                            # Terminal setup (alternative to launcher)
└── dataset/                            # Face sample images (auto-created)
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `dlib` fails to install | Install cmake / VS Build Tools first; ensure Python 3.10+ |
| Camera not detected | Grant camera permission in System Settings / Privacy |
| Face not recognized | Capture 30+ photos from different angles; retrain model |
| App can't connect to server | Check `base_url` in `educonnect_config.json` |
| `tkinter` not found (Linux) | `sudo apt install python3-tk` |

---

## License

MIT License — see [EduConnect](https://github.com/its-arya-jana/EduConnect) main repository.
