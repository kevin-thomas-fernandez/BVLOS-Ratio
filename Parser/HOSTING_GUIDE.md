# BVLOS RATIO - Complete Hosting Guide

## Overview

This guide explains how to host and run the **BVLOS RATIO** application offline with:
- ✅ **AI-powered RAG system** (Google Gemini API)
- ✅ **Population density extraction** (GeoTIFF processing)
- ✅ **Full backend API** (Flask server)

---

## 🚀 Quick Start (Local Hosting)

### Option 1: One-Click Start (Windows)

1. **Double-click** `backend/start_local_server.bat`
2. Wait for the server to start
3. Open your browser to: `http://localhost:8080`

### Option 2: Manual Start

#### Step 1: Navigate to Backend Directory

**Windows PowerShell:**
```powershell
cd "C:\This Matters 2025\AI\Experiments\Aerospace\Parser\backend"
```

**Windows CMD:**
```cmd
cd "C:\This Matters 2025\AI\Experiments\Aerospace\Parser\backend"
```

**Linux/Mac:**
```bash
cd backend
```

#### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with `rasterio`, you may need to install GDAL first:
- **Windows:** Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
- **Linux:** `sudo apt-get install gdal-bin libgdal-dev`
- **Mac:** `brew install gdal`

#### Step 4: Set Environment Variables (Optional but Recommended)

**Windows PowerShell:**
```powershell
$env:GOOGLE_API_KEY="your-api-key-here"
```

**Windows CMD:**
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**Or create a `.env` file** in the `backend` directory:
```
GOOGLE_API_KEY=your-api-key-here
```

#### Step 5: Start the Server

```bash
python main.py
```

You should see:
```
 * Running on http://0.0.0.0:8080
```

#### Step 6: Access the Application

Open your browser and navigate to:
- **Main Application:** `http://localhost:8080`
- **API Health Check:** `http://localhost:8080/api/health`
- **Population Extractor:** `http://localhost:8080/population_density_extractor.html` (if frontend is served)

---

## 📋 Prerequisites

### Required Software

1. **Python 3.8+** (3.11 recommended)
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Required Python Packages** (installed via `requirements.txt`):
   - Flask (web framework)
   - Flask-CORS (CORS support)
   - Google Generative AI (for AI responses)
   - Sentence Transformers (for embeddings)
   - Rasterio (for GeoTIFF processing)
   - NumPy (for numerical operations)
   - ChromaDB (for SORA data storage)
   - Firebase Admin SDK (optional, for cloud features)

### Required Data Files

1. **Parsed Rules JSON:**
   - Location: `backend/parsed_rules.json` or `parsed_rules.json` (root)
   - Contains FAA Part 108 regulations

2. **Population Data GeoTIFF Files:**
   - Location: `backend/population_data/` or `Population/`
   - Required files:
     - `landscan-usa-2021-conus-day.tif`
     - `landscan-usa-2021-conus-night.tif`
     - `landscan-global-2024.tif`
     - `JRC-CENSUS_2021_100m.tif`

3. **SORA Data** (optional, for SORA RAG):
   - Location: `SORA DATA/`
   - Includes embeddings, metadata, and ChromaDB database

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GOOGLE_API_KEY` | No* | Google Gemini API key for AI responses | None (fallback mode) |
| `PORT` | No | Server port | 8080 |
| `EMBEDDING_MODEL` | No | Sentence transformer model | `all-MiniLM-L6-v2` |
| `GEMINI_MODEL` | No | Gemini model version | `gemini-2.5-flash` |

*Required for AI features. Without it, the app runs in fallback mode with direct rule excerpts.

### Getting a Google Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and set it as `GOOGLE_API_KEY` environment variable

---

## 🌐 Hosting Options

### 1. Local Development (Offline)

**Best for:** Development, testing, offline use

**Steps:**
```bash
cd backend
python main.py
```

**Access:** `http://localhost:8080`

**Pros:**
- ✅ Fully offline after initial setup
- ✅ No cloud costs
- ✅ Fast local processing
- ✅ Full control

**Cons:**
- ❌ Only accessible on your machine
- ❌ Requires local setup

---

### 2. Local Network Hosting

**Best for:** Sharing with team on same network

**Steps:**
1. Find your local IP address:
   - **Windows:** `ipconfig` (look for IPv4 Address)
   - **Linux/Mac:** `ifconfig` or `ip addr`

2. Modify `main.py` to bind to your IP:
   ```python
   app.run(host='0.0.0.0', port=8080)  # Already configured
   ```

3. Start server:
   ```bash
   python main.py
   ```

4. Access from other devices:
   ```
   http://YOUR_IP_ADDRESS:8080
   ```

**Example:** `http://192.168.1.100:8080`

---

### 3. Docker Hosting (Recommended for Production)

**Best for:** Consistent deployment, production use

**Steps:**

1. **Build Docker image:**
   ```bash
   cd backend
   docker build -t bvlos-ratio .
   ```

2. **Run container:**
   ```bash
   docker run -d \
     -p 8080:8080 \
     -e GOOGLE_API_KEY="your-key-here" \
     -v "$(pwd)/population_data:/app/population_data" \
     -v "$(pwd)/parsed_rules.json:/app/parsed_rules.json" \
     bvlos-ratio
   ```

3. **Access:** `http://localhost:8080`

**Note:** Make sure GeoTIFF files are in `backend/population_data/` before building.

---

### 4. Cloud Hosting (Google Cloud Run)

**Best for:** Public access, scalable hosting

**Prerequisites:**
- Google Cloud account
- `gcloud` CLI installed
- Project created

**Steps:**

1. **Build and deploy:**
   ```bash
   cd backend
   gcloud run deploy bvlos-ratio \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --set-env-vars GOOGLE_API_KEY=your-key-here \
     --memory 2Gi \
     --cpu 2
   ```

2. **Access:** URL provided after deployment

**Note:** Cloud Run requires Dockerfile (already included).

---

## 🧪 Testing the Setup

### 1. Test API Health

```bash
curl http://localhost:8080/api/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Test AI Query Endpoint

```bash
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are weight limits for drones?"}'
```

### 3. Test Population Density Extraction

```bash
curl -X POST http://localhost:8080/api/extractPopulationDensity \
  -H "Content-Type: application/json" \
  -d '{
    "waypoints": [
      {"lat": 40.7128, "lon": -74.0060},
      {"lat": 40.7580, "lon": -73.9855}
    ],
    "geotiffFile": "landscan-usa-2021-conus-day.tif"
  }'
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "rasterio" installation fails

**Solution:**
- **Windows:** Install GDAL from https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
- **Linux:** `sudo apt-get install gdal-bin libgdal-dev`
- **Mac:** `brew install gdal`

Then:
```bash
pip install rasterio
```

### Issue: Port 8080 already in use

**Solution:**
Change the port in `main.py`:
```python
port = int(os.environ.get('PORT', '8081'))  # Change 8080 to 8081
```

Or set environment variable:
```bash
export PORT=8081  # Linux/Mac
set PORT=8081     # Windows CMD
$env:PORT=8081    # Windows PowerShell
```

### Issue: GeoTIFF files not found

**Solution:**
1. Ensure GeoTIFF files are in one of these locations:
   - `backend/population_data/`
   - `Population/`
   - Root directory

2. Check file names match exactly (case-sensitive)

### Issue: AI responses not working

**Solution:**
1. Check `GOOGLE_API_KEY` is set:
   ```bash
   echo $GOOGLE_API_KEY  # Linux/Mac
   echo %GOOGLE_API_KEY% # Windows CMD
   ```

2. Verify API key is valid at: https://makersuite.google.com/app/apikey

3. Check server logs for API errors

### Issue: "Firebase initialization failed"

**Solution:**
This is normal if you're running offline. The app will use local `parsed_rules.json` instead. To disable Firebase warnings, comment out Firebase initialization in `main.py`.

### Issue: UnicodeDecodeError when starting server

**Error:** `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0`

**Solution:**
This happens when your `.env` file has incorrect encoding (often UTF-16 instead of UTF-8). Fix it:

**Windows PowerShell:**
```powershell
cd backend
$content = Get-Content .env -Raw
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("$PWD\.env", $content.Trim(), $utf8NoBom)
```

**Or recreate the file:**
```powershell
Remove-Item backend\.env
"GOOGLE_API_KEY=your-api-key-here" | Out-File -FilePath backend\.env -Encoding utf8 -NoNewline
```

See `backend/FIX_ENV_ENCODING.md` for detailed instructions.

---

## 📊 Performance Tips

1. **First Run:** The first query may be slow as embeddings are generated. Subsequent queries are fast.

2. **Memory:** For large GeoTIFF files, ensure at least 4GB RAM available.

3. **CPU:** Population extraction is CPU-intensive. Consider using smaller GeoTIFF files for faster processing.

4. **Caching:** Embeddings are cached automatically. First query takes longer.

---

## 🔒 Security Notes

1. **API Keys:** Never commit API keys to version control
2. **Local Hosting:** Only accessible on your machine (good for security)
3. **Network Hosting:** Consider firewall rules if exposing to network
4. **Production:** Use HTTPS and authentication for production deployments

---

## 📝 API Endpoints

### Main Endpoints

- `GET /api/health` - Health check
- `GET /api/rules` - Get all rules (optional: `?category=flight_operations`)
- `GET /api/search?q=query` - Search rules
- `POST /api/query` - AI-powered query (requires `{"query": "..."}`)
- `POST /api/extractPopulationDensity` - Extract population density
- `GET /api/categories` - Get all categories
- `GET /api/sora/search?q=query` - Search SORA data

### Example Frontend Integration

```javascript
// Query AI
fetch('http://localhost:8080/api/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'What are weight limits?'})
})
.then(r => r.json())
.then(data => console.log(data.response));

// Extract population density
fetch('http://localhost:8080/api/extractPopulationDensity', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    waypoints: [
      {lat: 40.7128, lon: -74.0060},
      {lat: 40.7580, lon: -73.9855}
    ],
    geotiffFile: 'landscan-usa-2021-conus-day.tif'
  })
})
.then(r => r.json())
.then(data => console.log(data.data.populationDensity));
```

---

## 🎯 Next Steps

1. **Customize:** Modify `backend/config.py` for your needs
2. **Add Data:** Add more GeoTIFF files or update regulations
3. **Frontend:** Connect your frontend to `http://localhost:8080/api/*`
4. **Deploy:** Choose hosting option based on your needs

---

## 📞 Support

For issues:
1. Check server logs for error messages
2. Verify all prerequisites are installed
3. Test individual endpoints with curl/Postman
4. Check file paths and permissions

---

**Made with ❤️ for the drone community**

