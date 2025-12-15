# Quick Start: RAG AI Backend Server

## 🚀 Fastest Way to Start

**Windows:**
1. Double-click: `backend/start_rag_ai_backend.bat`
2. Wait for server to start (you'll see "Running on http://0.0.0.0:8080")
3. Open your frontend page

## ✅ Verify It's Running

Open in browser: `http://localhost:8080/api/health`

You should see: `{"status": "healthy"}`

## 🔧 Manual Start

**PowerShell:**
```powershell
cd backend
python rag_ai_backend.py
```

**Command Prompt:**
```cmd
cd backend
python rag_ai_backend.py
```

## 📋 What You Need

- ✅ Python 3.8+ installed
- ✅ Dependencies installed (`pip install -r backend/requirements.txt`)
- ✅ `.env` file with `GOOGLE_API_KEY` (optional but recommended)

## 🌐 Server Details

- **Port:** 8080 (default)
- **URL:** http://localhost:8080
- **Health Check:** http://localhost:8080/api/health

## 🐛 Troubleshooting

### "Cannot connect to local server"

1. **Check if server is running:**
   - Look for a PowerShell/terminal window with the server running
   - You should see: `Running on http://0.0.0.0:8080`

2. **Start the server:**
   - Double-click `backend/start_rag_ai_backend.bat`
   - Or run: `cd backend && python rag_ai_backend.py`

3. **Check the port:**
   - Server runs on port **8080** by default
   - Make sure nothing else is using port 8080

4. **Test the connection:**
   ```powershell
   curl http://localhost:8080/api/health
   ```

### Port Already in Use

If port 8080 is busy, change it:
```powershell
$env:PORT=8081
python rag_ai_backend.py
```

Then update your frontend to use port 8081.

## 📝 Next Steps

Once the server is running:
1. Open your frontend page
2. Try asking a question
3. Check the browser console for any errors

