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
    echo Installing face_recognition (includes dlib, face_recognition_models^)...
    echo This may take 5-15 minutes -- dlib is compiling from source.
    pip install face_recognition
    echo.
    echo Installing additional packages...
    pip install opencv-python opencv-contrib-python numpy Pillow pymongo bcrypt
    echo.
    echo Patching face_recognition_models for Python 3.14+...
    python patch_models.py 2>nul
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
)
pause
