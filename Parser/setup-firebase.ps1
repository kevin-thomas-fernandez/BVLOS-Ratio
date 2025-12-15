# Firebase Setup Script
# This script fixes PATH issues and helps configure Firebase

Write-Host "Firebase Setup Script" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

# 1. Fix PATH for current session
$npmPath = "$env:APPDATA\npm"
if ($env:PATH -notlike "*$npmPath*") {
    $env:PATH += ";$npmPath"
    Write-Host "✓ Added npm to PATH for this session" -ForegroundColor Green
}

# 2. Check Firebase CLI
Write-Host "Checking Firebase CLI..." -ForegroundColor Yellow
try {
    $version = firebase --version 2>&1
    Write-Host "✓ Firebase CLI is available (version $version)" -ForegroundColor Green
} catch {
    Write-Host "✗ Firebase CLI not found. Install with: npm install -g firebase-tools" -ForegroundColor Red
    exit 1
}

# 3. Check login status
Write-Host ""
Write-Host "Checking Firebase login..." -ForegroundColor Yellow
$loginCheck = firebase login:list 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Logged in to Firebase" -ForegroundColor Green
    Write-Host $loginCheck
} else {
    Write-Host "⚠ Not logged in. Run: firebase login" -ForegroundColor Yellow
}

# 4. List available projects
Write-Host ""
Write-Host "Available Firebase projects:" -ForegroundColor Yellow
firebase projects:list

Write-Host ""
Write-Host "To fix PATH permanently:" -ForegroundColor Cyan
Write-Host "1. Open System Properties > Environment Variables" -ForegroundColor White
Write-Host "2. Edit the User 'Path' variable" -ForegroundColor White
Write-Host "3. Add: $npmPath" -ForegroundColor White
Write-Host ""
Write-Host "Or run as Administrator: .\fix-firebase-path.ps1" -ForegroundColor Cyan

