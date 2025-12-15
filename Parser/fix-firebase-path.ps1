# PowerShell script to add npm global bin to PATH permanently
# Run this script as Administrator or manually add to your PATH

Write-Host "Firebase CLI PATH Fixer" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

$npmPath = "$env:APPDATA\npm"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -notlike "*$npmPath*") {
    Write-Host "Adding npm global bin directory to User PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$npmPath", "User")
    Write-Host "[OK] Added $npmPath to User PATH" -ForegroundColor Green
    Write-Host ""
    Write-Host "Please restart your PowerShell session for changes to take effect." -ForegroundColor Yellow
} else {
    Write-Host "[OK] npm path already in User PATH" -ForegroundColor Green
}

# Also add to current session
$env:PATH += ";$npmPath"

Write-Host ""
Write-Host "Testing Firebase CLI..." -ForegroundColor Cyan
$firebaseVersion = firebase --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Firebase CLI is working! Version: $firebaseVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Firebase CLI still not working. Please check installation." -ForegroundColor Red
}

