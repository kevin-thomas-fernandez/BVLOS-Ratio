# Quick Firebase Login Helper
# This script adds Firebase to PATH and runs login

$env:PATH += ";$env:APPDATA\npm"

Write-Host "Firebase Login Helper" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

# Check if Firebase is available
$firebaseCheck = firebase --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Firebase CLI is ready (version $firebaseCheck)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting login process..." -ForegroundColor Yellow
    Write-Host "A browser window will open for authentication." -ForegroundColor Cyan
    Write-Host ""
    
    # Start the login process
    firebase login
    
    Write-Host ""
    Write-Host "Login process completed. Verifying..." -ForegroundColor Yellow
    Write-Host ""
    firebase login:list
    Write-Host ""
    Write-Host "Available projects:" -ForegroundColor Yellow
    firebase projects:list
} else {
    Write-Host "✗ Firebase CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "  npm install -g firebase-tools" -ForegroundColor White
}

