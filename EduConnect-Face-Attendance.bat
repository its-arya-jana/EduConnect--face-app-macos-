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
    echo Installing opencv, numpy, Pillow, requests...
    pip install opencv-python opencv-contrib-python numpy Pillow requests
    echo.
    echo Installing face_recognition (10-15 minutes)...
    pip install face_recognition
    echo.
    echo Installing face_recognition_models...
    pip install git+https://github.com/ageitgey/face_recognition_models
    echo.
    echo Setup complete!
) else (
    call venv\Scripts\activate
)

echo.
echo Launching app...
python gui_launcher.py
if %errorlevel% neq 0 (
    echo.
    echo App exited with error code %errorlevel%
    echo Try deleting the 'venv' folder and running again.
)
pause
