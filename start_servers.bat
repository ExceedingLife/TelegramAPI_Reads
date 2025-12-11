@echo off
echo ============================================================
echo Starting Telegram Channel API Servers
echo ============================================================
echo.

REM Check if executables exist
if not exist "dist\TelegramAPI_Server.exe" (
    echo ERROR: TelegramAPI_Server.exe not found in dist folder
    echo Please build the executables first by running build.bat
    pause
    exit /b 1
)

if not exist "dist\TelegramAPI_Frontend.exe" (
    echo ERROR: TelegramAPI_Frontend.exe not found in dist folder
    echo Please build the executables first by running build.bat
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create a .env file with your Telegram credentials.
    echo See env.example for reference.
    echo.
    pause
)

echo Starting API Server on port 8000...
start "Telegram API Server" dist\TelegramAPI_Server.exe

timeout /t 3 /nobreak >nul

echo Starting Frontend Server on port 8001...
start "Telegram Frontend Server" dist\TelegramAPI_Frontend.exe

timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo Servers started!
echo.
echo API Server:    http://localhost:8000
echo Frontend:      http://localhost:8001
echo.
echo Press any key to open the frontend in your browser...
pause >nul

start http://localhost:8001

echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.


