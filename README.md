# EduConnect Face Recognition App

Desktop face recognition attendance system for **EduConnect**. Teachers take attendance using a webcam — records sync directly to **MongoDB Atlas** (no web server needed).

## Features

- Face detection and recognition using `face_recognition` (dlib)
- Real-time scanner with student roster overlay
- Syncs attendance directly to MongoDB Atlas
- Works completely offline except for database sync

## Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Webcam** (built-in or USB)
- **EduConnect teacher account** with active classes
- **macOS** or **Linux** or **Windows 10/11**

> **Note:** `dlib` / `face_recognition` compilation takes 5–15 minutes during first install.

---

## Installation & Usage

### macOS

Double-click **`EduConnect-Face-Attendance.app`**.

If macOS blocks it: **Right-click → Open → click Open**. Or run once:
```bash
xattr -d com.apple.quarantine EduConnect-Face-Attendance.app
```

### macOS (Terminal alternative)

```bash
./EduConnect-Face-Attendance.command
```

### Windows

Double-click **`EduConnect-Face-Attendance.bat`**.

> On Windows you may need **Visual Studio Build Tools** for dlib: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

### First launch

1. The app auto-installs everything into a virtual environment (takes 5–15 minutes).
2. Enter your **EduConnect teacher email** and **password**.
3. The app connects directly to MongoDB Atlas — no server or proxy needed.
4. Select a subject, go to **Scanner tab**, click **START SCANNER**.

### From EduConnect Portal

1. Log in as a **Teacher** on EduConnect.
2. Go to **Attendance → Mark Attendance**.
3. Select a **Subject** and **Date**, click the face icon.
4. The app opens with the class pre-loaded.

---

## How it works

- **Direct MongoDB connection** — no web server, no Cloudflare, no cold-start wait.
- Login validates against the `users` collection (bcrypt).
- Class roster fetched from the `classes` collection.
- Attendance upserted into the `attendances` collection.
- All data lives in your existing EduConnect MongoDB Atlas cluster.

---

## Project Structure

```
EduConnect-Face-App/
├── EduConnect-Face-Attendance.app      # macOS app bundle (double-click)
├── EduConnect-Face-Attendance.command  # macOS launcher (Terminal)
├── EduConnect-Face-Attendance.bat      # Windows launcher (double-click)
├── gui_launcher.py                     # Entry point
├── department_attendance_app.py        # Main Tkinter GUI (MongoDB + face scan)
├── face_recognizer.py                  # Face detection / recognition
├── database.py                         # Local SQLite operations
├── student_mapper.py                   # Face ID ↔ MongoDB ID mapping
├── patch_models.py                     # Fixes face_recognition_models for Python 3.14+
├── requirements.txt                    # Python dependencies
├── setup.sh                            # Terminal setup (alternative to launcher)
├── educonnect_config.json              # Saves email only
├── student_mapping.json                # Auto-generated ID mappings
└── dataset/                            # Face sample images (auto-created)
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `dlib` fails to install | Install cmake / VS Build Tools first; ensure Python 3.10+ |
| Camera not detected | Grant camera permission in System Settings / Privacy |
| Face not recognized | Capture 30+ photos from different angles; retrain model |
| "Cannot connect to database" | Check your internet connection |
| `tkinter` not found (Linux) | `sudo apt install python3-tk` |

---

## License

MIT License — see [EduConnect](https://github.com/its-arya-jana/EduConnect).
