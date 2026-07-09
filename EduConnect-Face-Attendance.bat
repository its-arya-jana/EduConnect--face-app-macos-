@echo off
cd /d "%~dp0"

where python 2>nul | findstr /i /v "WindowsApps" >nul
if %errorlevel% neq 0 (
    where py 2>nul >nul
    if %errorlevel% neq 0 (
        echo ============================================
        echo   Python not found
        echo ============================================
        echo.
        echo Download Python from python.org:
        echo   https://www.python.org/downloads/
        echo.
        echo Check "Add Python to PATH" during install.
        echo.
        pause
        exit /b 1
    )
    set PY_CMD=py -3
) else (
    set PY_CMD=python
)

echo Python:
%PY_CMD% --version

if not exist "venv\Scripts\activate.bat" (
    echo ============================================
    echo   First-Time Setup
    echo ============================================
    echo.
    echo Creating virtual environment...
    %PY_CMD% -m venv venv

    if not exist "venv\Scripts\activate.bat" (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )

    call venv\Scripts\activate.bat

    echo Upgrading pip...
    python -m pip install --upgrade pip

    echo.
    echo Installing face_recognition (compiling dlib - 5 to 15 min)...
    pip install face_recognition

    echo.
    echo Installing additional packages...
    pip install opencv-python opencv-contrib-python numpy Pillow pymongo bcrypt

    echo.
    python patch_models.py 2>nul

    echo Setup complete!
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Launching app...
python gui_launcher.py

pause
