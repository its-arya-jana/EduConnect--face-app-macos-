@echo off
cd /d "%~dp0"

if not exist venv\Scripts\activate.bat (
    echo ============================================
    echo   EduConnect Face Attendance - First-Time Setup
    echo ============================================
    echo.
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Upgrading pip...
    python -m pip install --upgrade pip
    echo.
    echo Installing dependencies (this may take 10-15 minutes)...
    pip install opencv-python opencv-contrib-python numpy Pillow requests face_recognition
    echo.
    echo Setup complete! Launching app...
) else (
    call venv\Scripts\activate
)

python gui_launcher.py
if %errorlevel% neq 0 (
    echo.
    echo Error: Something went wrong. Try deleting the 'venv' folder and double-clicking this file again.
    pause
)
pause
