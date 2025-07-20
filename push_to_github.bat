@echo off
echo 🚀 Pushing changes to GitHub and Heroku...

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Error: backend directory not found. Please run this script from the ACBC project root.
    pause
    exit /b 1
)

echo 📋 Checking git status...
git status

echo 📦 Adding all changes...
git add .

echo 💾 Committing changes...
git commit -m "Fix 500 error on BYO config endpoint - v1.4.3"

echo 🔗 Checking GitHub remote...
git remote -v | findstr "github.com/halderavik/ACBC_API.git" >nul
if errorlevel 1 (
    echo ➕ Adding GitHub remote...
    git remote add origin https://github.com/halderavik/ACBC_API.git
) else (
    echo ✅ GitHub remote already exists
)

echo 📤 Pushing to GitHub...
git push -u origin main

echo 📤 Pushing to Heroku...
git push heroku main

echo ✅ All changes pushed successfully!
echo 🌐 GitHub: https://github.com/halderavik/ACBC_API.git
echo 🚀 Heroku: https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com

pause 