@echo off
REM ========================================
REM  EduConnect Face App - Windows Setup
REM ========================================
echo.
echo ========================================
echo   EduConnect Face Recognition - Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found.
    echo Download Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo Using Python:
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing Python packages (this may take a while)...
echo Step 1/3: numpy, opencv, Pillow, requests...
pip install opencv-python opencv-contrib-python numpy Pillow requests

echo.
echo Step 2/3: Installing face_recognition (includes dlib compile)...
echo This may take 10-15 minutes...
pip install face_recognition

REM Create run.bat launcher
echo.
echo Creating launcher script...
echo @echo off > run.bat
echo cd /d "%%~dp0" >> run.bat
echo call venv\Scripts\activate >> run.bat
echo python gui_launcher.py %%* >> run.bat
echo pause >> run.bat

echo.
echo ========================================
echo   Setup complete!
echo ========================================
echo.
echo To run the app:
echo   double-click run.bat
echo.
echo Or with options:
echo   run.bat --class-id ^<ID^> --auth-token ^<TOKEN^> --date YYYY-MM-DD
echo.
pause
