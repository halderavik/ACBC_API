#!/usr/bin/env pwsh
# PowerShell script to push changes to GitHub and Heroku

Write-Host "🚀 Pushing changes to GitHub and Heroku..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: backend directory not found. Please run this script from the ACBC project root." -ForegroundColor Red
    exit 1
}

# Check git status
Write-Host "📋 Checking git status..." -ForegroundColor Yellow
git status

# Add all changes
Write-Host "📦 Adding all changes..." -ForegroundColor Yellow
git add .

# Commit changes
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m "Fix 500 error on BYO config endpoint - v1.4.3

- Removed problematic catch-all route that was interfering with API endpoints
- Kept POST support for /health endpoint to handle monitoring requests
- FastAPI's built-in 404 handling is sufficient for unmatched endpoints
- This should resolve the 500 Internal Server Error on /api/byo-config
- Updated API documentation and test scripts"

# Check if GitHub remote exists
Write-Host "🔗 Checking GitHub remote..." -ForegroundColor Yellow
$remotes = git remote -v
if ($remotes -match "github.com/halderavik/ACBC_API.git") {
    Write-Host "✅ GitHub remote already exists" -ForegroundColor Green
} else {
    Write-Host "➕ Adding GitHub remote..." -ForegroundColor Yellow
    git remote add origin https://github.com/halderavik/ACBC_API.git
}

# Push to GitHub
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

# Push to Heroku
Write-Host "📤 Pushing to Heroku..." -ForegroundColor Yellow
git push heroku main

Write-Host "✅ All changes pushed successfully!" -ForegroundColor Green
Write-Host "🌐 GitHub: https://github.com/halderavik/ACBC_API.git" -ForegroundColor Cyan
Write-Host "🚀 Heroku: https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com" -ForegroundColor Cyan 