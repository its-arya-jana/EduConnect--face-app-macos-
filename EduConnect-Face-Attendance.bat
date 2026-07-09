@echo off
cd /d "%~dp0"

:: Check that Python is a real install, not the Microsoft Store stub
where python 2>nul | findstr /i /v "WindowsApps" >nul
if %errorlevel% neq 0 (
    where py 2>nul >nul
    if %errorlevel% neq 0 (
        echo ============================================
        echo   Python not found
        echo ============================================
        echo.
        echo You have the Microsoft Store Python stub, which
        echo won't work for this app.
        echo.
        echo Solution:
        echo   1. Download Python from python.org:
        echo      https://www.python.org/downloads/
        echo.
        echo   2. During install, check "Add Python to PATH"
        echo.
        echo   3. Or disable the Store alias:
        echo      Settings ^> Apps ^> Advanced app settings
        echo      ^> App execution aliases
        echo      Turn OFF "python.exe" and "python3.exe"
        echo.
        pause
        exit /b 1
    )
    set PYTHON_CMD=py -3
    goto :found
)

set PYTHON_CMD=python

:found
echo Python:
%PYTHON_CMD% --version

if not exist "venv\Scripts\activate.bat" (
    echo ============================================
    echo   First-Time Setup
    echo ============================================
    echo.
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv venv

    if not exist "venv\Scripts\activate.bat" (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )

    call venv\Scripts\activate.bat

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
    call venv\Scripts\activate.bat
)

echo.
echo Launching app...
python gui_launcher.py
if %errorlevel% neq 0 (
    echo.
    echo App exited with error code %errorlevel%
)
pause
