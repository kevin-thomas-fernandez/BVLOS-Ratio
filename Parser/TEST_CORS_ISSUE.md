# Testing CORS Issue

## The Problem

You're getting a `TypeError` when trying to connect to the Cloud Run API. This is almost certainly a **CORS (Cross-Origin Resource Sharing)** issue.

## Quick Test

Open your browser's Developer Console (F12) and run this:

```javascript
fetch('https://rag-api-145283170665.us-central1.run.app/api/health', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(console.log)
.catch(err => {
  console.error('ERROR:', err);
  console.error('This is likely a CORS error if you see TypeError');
});
```

If you see a CORS error in the console, that confirms the issue.

## Why This Happens

The backend code has been updated with CORS fixes, but **the Cloud Run service hasn't been redeployed yet**. The old version is still running without the CORS headers.

## Solutions

### Option 1: Redeploy Backend (Fixes Web Interface)

```bash
cd backend
gcloud run deploy rag-api --source . --region us-central1 --project part-108-parser --allow-unauthenticated --port 8080
```

This will deploy the updated CORS configuration and fix the web interface.

### Option 2: Use Standalone Python Script (No API Needed)

Skip the API entirely and use the Python script directly:

```bash
cd backend
python extract_population_density.py --waypoints "40.7128,-74.0060" "40.7580,-73.9855" --file landscan-usa-2021-conus-day.tif
```

This works immediately - no API, no CORS, no deployment needed!

### Option 3: Test Locally

Run the backend locally:

```bash
cd backend
python main.py
```

Then access the web interface from `http://localhost:5000` - CORS won't be an issue locally.

## What Changed in the Backend

The CORS configuration was updated to:
- Allow all origins (`*`)
- Add CORS headers to all responses
- Handle OPTIONS preflight requests

But these changes only take effect after redeployment.

## Recommended Action

**For immediate use**: Use the standalone Python script (`backend/extract_population_density.py`)

**For long-term fix**: Redeploy the backend to Cloud Run with the updated CORS settings

