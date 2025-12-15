# How to Run the Population Density Extractor Offline

## Quick Start

### Step 1: Open PowerShell/Terminal
- Press `Win + X` and select "Windows PowerShell" or "Terminal"
- Or search for "PowerShell" in the Start menu

### Step 2: Navigate to the Backend Folder
```powershell
cd "C:\This Matters 2025\AI\Experiments\Aerospace\Parser\backend"
```

### Step 3: Install Dependencies (if not already installed)
```powershell
pip install flask flask-cors rasterio numpy
```

### Step 4: Start the Local Server
```powershell
python local_population_server.py
```

You should see:
```
============================================================
Local Population Density Server
============================================================
Server running on: http://localhost:5000
Access the web interface at: http://localhost:5000/population_density_extractor.html
============================================================

Press Ctrl+C to stop the server
```

### Step 5: Open the Web Interface
- **Option A**: Open your browser and go to: `http://localhost:5000/population_density_extractor.html`
- **Option B**: Open the HTML file directly: `frontend/population_density_extractor.html` (it will auto-detect localhost)

### Step 6: Keep the Terminal Open
- **IMPORTANT**: Keep the PowerShell window open while using the tool
- The server runs in that window
- Press `Ctrl+C` to stop the server when you're done

---

## Troubleshooting

### If you get "python is not recognized":
1. Install Python from https://www.python.org/downloads/
2. Make sure to check "Add Python to PATH" during installation
3. Restart your terminal

### If you get "Module not found" errors:
```powershell
pip install flask flask-cors rasterio numpy
```

### If port 5000 is already in use:
The server will show an error. You can either:
- Close the other program using port 5000
- Or modify `local_population_server.py` to use a different port (change `port=5000` to another number like `port=5001`)

### If the browser shows "Cannot connect":
1. Make sure the server is running (check the PowerShell window)
2. Make sure you're using `http://localhost:5000` (not `https://`)
3. Try refreshing the page

---

## Alternative: Using Command Prompt (CMD)

If PowerShell doesn't work, you can use CMD:

1. Press `Win + R`, type `cmd`, press Enter
2. Navigate to backend:
   ```
   cd "C:\This Matters 2025\AI\Experiments\Aerospace\Parser\backend"
   ```
3. Install dependencies:
   ```
   pip install flask flask-cors rasterio numpy
   ```
4. Start server:
   ```
   python local_population_server.py
   ```

---

## What the Server Does

The local server:
- Runs on your computer (no internet needed after setup)
- Processes population density requests
- Serves the web interface
- No CORS issues since everything runs locally

