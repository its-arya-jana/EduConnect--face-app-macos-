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
    echo Installing packages...
    pip install opencv-python opencv-contrib-python numpy Pillow curl_cffi
    pip install face_recognition
    echo.
    echo Installing face_recognition_models...
    pip install https://github.com/ageitgey/face_recognition_models/archive/refs/heads/master.zip
    echo.
    echo Patching models for Python compatibility...
    python patch_models.py
    if %errorlevel% neq 0 (
        echo Patch failed.
        pause
        exit /b 1
    )
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
