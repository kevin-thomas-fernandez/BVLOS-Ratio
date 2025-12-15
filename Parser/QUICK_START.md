# BVLOS RATIO - Quick Start Guide

## 🚀 Fastest Way to Get Started

### Windows Users

1. **Double-click:** `backend/start_backend_server.bat`
2. **Open browser:** `http://localhost:8080`
3. **Done!** ✅

### Linux/Mac Users

1. **Run:** `cd backend && bash start_backend_server.sh`
2. **Open browser:** `http://localhost:8080`
3. **Done!** ✅

---

## 📋 What You Need

### Required
- ✅ Python 3.8+ installed
- ✅ `parsed_rules.json` file
- ✅ GeoTIFF files (for population extraction)

### Optional (but recommended)
- 🔑 Google Gemini API Key (for AI features)
- 🐳 Docker (for containerized deployment)

---

## 🔑 Setting Up Google API Key

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

**Get your API key:** https://makersuite.google.com/app/apikey

---

## 🌐 Access Points

Once the server is running:

- **Main API:** `http://localhost:8080/api/health`
- **AI Query:** `http://localhost:8080/api/query`
- **Population Extract:** `http://localhost:8080/api/extractPopulationDensity`

---

## 🧪 Quick Test

**Test the server:**
```bash
curl http://localhost:8080/api/health
```

**Test AI query:**
```bash
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are weight limits?"}'
```

---

## 📚 Full Documentation

See `HOSTING_GUIDE.md` for:
- Detailed setup instructions
- Troubleshooting
- Deployment options
- API documentation

---

## ⚡ Common Issues

**Port 8080 in use?**
- Change port: `set PORT=8081` (Windows) or `export PORT=8081` (Linux/Mac)

**Module not found?**
- Run: `pip install -r backend/requirements.txt`

**GeoTIFF files not found?**
- Place files in `backend/population_data/` or `Population/`

---

**Need help?** Check `HOSTING_GUIDE.md` for detailed troubleshooting.

