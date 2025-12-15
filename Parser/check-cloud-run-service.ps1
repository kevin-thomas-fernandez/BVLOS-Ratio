# Check Cloud Run Service Configuration
# This script helps diagnose the 404 error for /api/extractPopulationDensity

Write-Host "Checking Cloud Run service configuration..." -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
$gcloudInstalled = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudInstalled) {
    Write-Host "ERROR: gcloud CLI is not installed." -ForegroundColor Red
    Write-Host "Install it from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Check your Cloud Run services in the Google Cloud Console:" -ForegroundColor Yellow
    Write-Host "https://console.cloud.google.com/run?project=part-108-parser" -ForegroundColor Cyan
    exit 1
}

# Check if Firebase CLI is installed
$firebaseInstalled = Get-Command firebase -ErrorAction SilentlyContinue
if (-not $firebaseInstalled) {
    Write-Host "WARNING: Firebase CLI is not installed." -ForegroundColor Yellow
    Write-Host "Install it with: npm install -g firebase-tools" -ForegroundColor Yellow
    Write-Host ""
}

# Project and service info
$projectId = "part-108-parser"
$region = "us-central1"
$serviceName = "rag-api"

Write-Host "Project: $projectId" -ForegroundColor Green
Write-Host "Region: $region" -ForegroundColor Green
Write-Host "Expected Service Name: $serviceName" -ForegroundColor Green
Write-Host ""

# Check if logged in to gcloud
Write-Host "Checking gcloud authentication..." -ForegroundColor Cyan
$gcloudAuth = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($LASTEXITCODE -ne 0 -or -not $gcloudAuth) {
    Write-Host "ERROR: Not logged in to gcloud. Run: gcloud auth login" -ForegroundColor Red
    exit 1
}
Write-Host "Logged in as: $gcloudAuth" -ForegroundColor Green
Write-Host ""

# List Cloud Run services
Write-Host "Listing Cloud Run services in $region..." -ForegroundColor Cyan
$services = gcloud run services list --project=$projectId --region=$region --format="json" 2>&1 | ConvertFrom-Json

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to list Cloud Run services." -ForegroundColor Red
    Write-Host "Make sure you have the Cloud Run API enabled and proper permissions." -ForegroundColor Yellow
    exit 1
}

if ($services.Count -eq 0) {
    Write-Host "WARNING: No Cloud Run services found in $region" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You need to deploy the backend service. Run:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Cyan
    Write-Host "  gcloud run deploy rag-api --source . --region us-central1 --project part-108-parser --allow-unauthenticated --port 8080" -ForegroundColor Cyan
    exit 1
}

Write-Host "Found $($services.Count) service(s):" -ForegroundColor Green
foreach ($service in $services) {
    Write-Host "  - $($service.metadata.name) (URL: $($service.status.url))" -ForegroundColor Cyan
}

Write-Host ""

# Check if rag-api exists
$ragApiService = $services | Where-Object { $_.metadata.name -eq $serviceName }

if (-not $ragApiService) {
    Write-Host "ERROR: Service '$serviceName' not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available services:" -ForegroundColor Yellow
    foreach ($service in $services) {
        Write-Host "  - $($service.metadata.name)" -ForegroundColor Cyan
    }
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "1. Deploy a new service named 'rag-api':" -ForegroundColor Cyan
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   gcloud run deploy rag-api --source . --region us-central1 --project part-108-parser --allow-unauthenticated --port 8080" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Update firebase.json to use an existing service name" -ForegroundColor Cyan
    exit 1
}

Write-Host "SUCCESS: Service '$serviceName' found!" -ForegroundColor Green
Write-Host "  URL: $($ragApiService.status.url)" -ForegroundColor Cyan
Write-Host ""

# Check firebase.json configuration
Write-Host "Checking firebase.json configuration..." -ForegroundColor Cyan
$firebaseJson = Get-Content firebase.json -Raw | ConvertFrom-Json

if ($firebaseJson.hosting.rewrites) {
    $apiRewrite = $firebaseJson.hosting.rewrites | Where-Object { $_.source -eq "/api/**" }
    if ($apiRewrite) {
        Write-Host "Firebase Hosting rewrite configured:" -ForegroundColor Green
        Write-Host "  Source: $($apiRewrite.source)" -ForegroundColor Cyan
        Write-Host "  Service ID: $($apiRewrite.run.serviceId)" -ForegroundColor Cyan
        Write-Host "  Region: $($apiRewrite.run.region)" -ForegroundColor Cyan
        
        if ($apiRewrite.run.serviceId -ne $serviceName) {
            Write-Host ""
            Write-Host "WARNING: Service ID in firebase.json doesn't match!" -ForegroundColor Yellow
            Write-Host "  firebase.json has: $($apiRewrite.run.serviceId)" -ForegroundColor Yellow
            Write-Host "  Actual service: $serviceName" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Update firebase.json to use: $serviceName" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "Configuration looks correct!" -ForegroundColor Green
            Write-Host ""
            Write-Host "If you're still getting 404 errors, try:" -ForegroundColor Yellow
            Write-Host "1. Redeploy Firebase Hosting: firebase deploy --only hosting" -ForegroundColor Cyan
            Write-Host "2. Verify the Cloud Run service is accessible: curl $($ragApiService.status.url)/api/health" -ForegroundColor Cyan
        }
    }
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

