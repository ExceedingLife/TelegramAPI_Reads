@echo off
echo ============================================================
echo Telegram Channel API - Executable Builder
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Install PyInstaller if not already installed
echo Checking for PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Run the build script
echo.
echo Starting build process...
python build_executables.py

echo.
echo Build process completed!
echo.
pause


