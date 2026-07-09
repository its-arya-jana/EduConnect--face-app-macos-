@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion

:: Find a working Python (avoid Microsoft Store redirect)
:: The MS Store stub returns exit 0 for --version but can't run code.
:: Using `-c "import sys"` reliably detects real Python.
set PYTHON_CMD=
py -3 -c "import sys" >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
) else (
    python -c "import sys" >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
    ) else (
        echo ============================================
        echo   Python not found
        echo ============================================
        echo.
        echo Download Python from python.org (NOT the Microsoft Store):
        echo   https://www.python.org/downloads/
        echo.
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        echo If Python IS installed, disable the Microsoft Store alias:
        echo   Settings ^> Apps ^> Advanced app settings ^> App execution aliases
        echo   Turn OFF "python.exe" and "python3.exe"
        echo.
        pause
        exit /b 1
    )
)

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
        echo Try running the command prompt as Administrator.
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
