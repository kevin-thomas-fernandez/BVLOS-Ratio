# Firebase Status Checker
Write-Host "Firebase Status Check" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

$env:PATH += ";$env:APPDATA\npm"

# Check if Firebase CLI is available
$firebaseCheck = firebase --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Firebase CLI is installed (version $firebaseCheck)" -ForegroundColor Green
} else {
    Write-Host "✗ Firebase CLI not found. Install with: npm install -g firebase-tools" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check login status
Write-Host "Login Status:" -ForegroundColor Yellow
$loginInfo = firebase login:list 2>&1
Write-Host $loginInfo

Write-Host ""
Write-Host "Available Projects:" -ForegroundColor Yellow
firebase projects:list

Write-Host ""
Write-Host "Current Project Configuration:" -ForegroundColor Yellow
if (Test-Path ".firebaserc") {
    $config = Get-Content ".firebaserc" | ConvertFrom-Json
    $defaultProject = $config.projects.default
    Write-Host "  Default project: $defaultProject" -ForegroundColor White
    
    # Try to check if it's accessible
    Write-Host ""
    Write-Host "Checking if '$defaultProject' is accessible..." -ForegroundColor Yellow
    $useResult = firebase use $defaultProject 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Project '$defaultProject' is accessible" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Project '$defaultProject' is NOT accessible" -ForegroundColor Red
        Write-Host ""
        Write-Host "Options:" -ForegroundColor Cyan
        Write-Host "  1. Create the project at: https://console.firebase.google.com/" -ForegroundColor White
        Write-Host "  2. Or switch to an existing project: firebase use <project-id>" -ForegroundColor White
        Write-Host "  3. Or logout and login with a different account: firebase logout && firebase login" -ForegroundColor White
    }
} else {
    Write-Host "  No .firebaserc file found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  firebase login          - Login to Firebase" -ForegroundColor White
Write-Host "  firebase logout         - Logout from Firebase" -ForegroundColor White
Write-Host "  firebase login:list     - Show current login" -ForegroundColor White
Write-Host "  firebase projects:list  - List all projects" -ForegroundColor White
Write-Host "  firebase use <project>  - Switch to a project" -ForegroundColor White

