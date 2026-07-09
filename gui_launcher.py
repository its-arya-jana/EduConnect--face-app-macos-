#!/usr/bin/env python3
import sys
import os
import argparse
import traceback

missing = []
try:
    import cv2
except ImportError:
    missing.append("opencv-python (cv2)")
try:
    import PIL
except ImportError:
    missing.append("Pillow")
try:
    import requests
except ImportError:
    missing.append("requests")
try:
    import face_recognition
    fr_models_ok = True
    try:
        face_recognition.face_locations(face_recognition.load_image_file.__doc__)
    except Exception:
        fr_models_ok = False
except ImportError:
    missing.append("face_recognition")
    fr_models_ok = False

if missing:
    msg = "Missing packages:\n" + "\n".join(f"  - {m}" for m in missing)
    msg += "\n\nDelete the 'venv' folder and run the app again."
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Setup Error", msg)
    root.destroy()
    sys.exit(1)

if not fr_models_ok:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "face_recognition_models missing",
        "The face recognition model data is missing.\n\n"
        "Please run this command in Terminal:\n"
        "  pip install git+https://github.com/ageitgey/face_recognition_models\n\n"
        "Or re-download the app from GitHub and try again."
    )
    root.destroy()
    sys.exit(1)

import tkinter as tk
from department_attendance_app import App

def main():
    parser = argparse.ArgumentParser(description='Launch Face Recognition Attendance System GUI')
    parser.add_argument('--class-id', help='EduConnect class ID')
    parser.add_argument('--auth-token', help='Authentication token for EduConnect API')
    parser.add_argument('--date', help='Attendance date (YYYY-MM-DD)')

    args = parser.parse_args()

    root = tk.Tk()
    try:
        app = App(root, token=args.auth_token, class_id=args.class_id, date=args.date)
        root.mainloop()
    except Exception:
        from tkinter import messagebox
        root.withdraw()
        messagebox.showerror("Error", traceback.format_exc())
        root.destroy()

if __name__ == "__main__":
    main()
