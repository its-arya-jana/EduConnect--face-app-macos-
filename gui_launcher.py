#!/usr/bin/env python3
import sys
import os
import argparse
import tkinter as tk
from department_attendance_app import App

def main():
    parser = argparse.ArgumentParser(description='Launch Face Recognition Attendance System GUI')
    parser.add_argument('--class-id', help='EduConnect class ID')
    parser.add_argument('--auth-token', help='Authentication token for EduConnect API')
    parser.add_argument('--date', help='Attendance date (YYYY-MM-DD)')

    args = parser.parse_args()

    root = tk.Tk()
    app = App(root, token=args.auth_token, class_id=args.class_id, date=args.date)
    root.mainloop()

if __name__ == "__main__":
    main()