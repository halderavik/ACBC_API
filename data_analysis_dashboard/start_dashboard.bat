@echo off
echo 🎯 ACBC Data Analysis Dashboard - Windows Startup
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ app.py not found in current directory
    echo Please run this script from the data_analysis_dashboard folder
    pause
    exit /b 1
)

echo ✅ Dashboard files found

REM Install dependencies if needed
echo 📦 Checking dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Some dependencies may not be installed
    echo Continuing anyway...
)

REM Set default environment variables if not set
if "%DATABASE_URL%"=="" (
    set DATABASE_URL=postgresql+asyncpg://postgres:Password123!@localhost:5432/conjoint
    echo 🔧 Set DATABASE_URL to actual database configuration
)

if "%API_BASE_URL%"=="" (
    set API_BASE_URL=https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com
    echo 🔧 Set API_BASE_URL to default value
)

if "%PORT%"=="" (
    set PORT=5001
    echo 🔧 Set PORT to default value (5001)
)

echo.
echo 🚀 Starting ACBC Data Analysis Dashboard...
echo 🌐 Dashboard will be available at: http://localhost:%PORT%
echo 📊 API endpoints at: http://localhost:%PORT%/api/
echo.
echo 🔄 Starting server... (Press Ctrl+C to stop)
echo ----------------------------------------

REM Start the dashboard
python app.py

echo.
echo 🛑 Dashboard stopped
pause 