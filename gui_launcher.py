#!/usr/bin/env python3
import sys
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
except ImportError:
    missing.append("face_recognition")

if missing:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Missing Packages",
        "Missing Python packages:\n" + "\n".join(f"  - {m}" for m in missing) +
        "\n\nDelete the 'venv' folder and run the app again."
    )
    root.destroy()
    sys.exit(1)

import argparse
import tkinter as tk
from department_attendance_app import App

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--class-id')
    parser.add_argument('--auth-token')
    parser.add_argument('--date')
    args = parser.parse_args()

    root = tk.Tk()
    try:
        app = App(root, token=args.auth_token, class_id=args.class_id, date=args.date)
        root.mainloop()
    except Exception as e:
        from tkinter import messagebox
        root.withdraw()
        tb = traceback.format_exc()
        messagebox.showerror(
            "App Error",
            f"{e}\n\nFull details:\n{tb[:2000]}"
        )
        root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main()
