@echo off
REM ACBC Data Analysis Dashboard Startup Script for Windows
REM This script activates the virtual environment and starts the dashboard

echo 🚀 Starting ACBC Data Analysis Dashboard...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run this script again.
    pause
    exit /b 1
)

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\Scripts\hypercorn.exe" (
    echo ❌ Hypercorn not found! Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install requirements!
        pause
        exit /b 1
    )
)

REM Check if app.py exists
if not exist "app.py" (
    echo ❌ app.py not found!
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo ✅ Dependencies checked
echo ✅ app.py found
echo.
echo 🌐 Starting dashboard on http://localhost:5001
echo 📊 Data Analysis Dashboard will be available at: http://localhost:5001
echo ⏹️  Press Ctrl+C to stop the server
echo.

REM Start the dashboard with Hypercorn
hypercorn app:app --bind 0.0.0.0:5001 --reload

echo.
echo 🛑 Dashboard stopped
pause 