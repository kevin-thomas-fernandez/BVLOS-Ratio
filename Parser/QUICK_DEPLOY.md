# 🚀 Quick Deploy Guide - Right Now!

## Your Backend is Ready! ✅
- ✅ `Dockerfile` exists
- ✅ `requirements.txt` exists  
- ✅ `main.py` has CORS fixes
- ✅ All files in place

## Deploy in 5 Steps:

### 1️⃣ In the Cloud Run Console (just opened):
   - Look for **"CREATE SERVICE"** button (if `rag-api` doesn't exist)
   - OR click on **`rag-api`** service → **"EDIT & DEPLOY NEW REVISION"** (if it exists)

### 2️⃣ Configure:
   - **Service name**: `rag-api`
   - **Region**: `us-central1`
   - **Deploy from**: Select **"Source"** → Browse → Select your `backend` folder
   - ✅ **Check**: "Allow unauthenticated invocations"

### 3️⃣ Advanced Settings (click to expand):
   - **Port**: `8080`
   - **Memory**: `2 GiB`
   - **Timeout**: `300` seconds

### 4️⃣ Click **"CREATE"** or **"DEPLOY"**

### 5️⃣ Wait 5-10 minutes for build to complete

---

## 🎯 Alternative: Use Cloud Shell (Has gcloud Pre-installed!)

If the web interface is confusing:

1. **Open Cloud Shell:**
   - Go to: https://console.cloud.google.com/cloudshell?project=part-108-parser
   - Or click the terminal icon (top right of Cloud Console)

2. **Upload backend folder:**
   - Click the three-dot menu (top right of Cloud Shell)
   - Select "Upload file"
   - Upload your entire `backend` folder as a zip file
   - Or use git if you have a repository

3. **Deploy:**
   ```bash
   # After uploading, extract if needed, then:
   cd backend
   gcloud run deploy rag-api \
     --source . \
     --region us-central1 \
     --project part-108-parser \
     --allow-unauthenticated \
     --port 8080 \
     --memory 2Gi \
     --timeout 300
   ```

---

## ✅ After Deployment:

Your service URL will be shown (like `https://rag-api-xxxxx.us-central1.run.app`)

Test it: Open the URL + `/api/health` → Should return `{"status":"healthy"}`

The frontend will automatically use this URL when accessed online!

