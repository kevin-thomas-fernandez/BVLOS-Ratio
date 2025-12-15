# 🚁 RAG Drone Regulations Web App - Complete Setup Guide

## Project Overview

**What is this app?**
A Retrieval-Augmented Generation (RAG) web application that answers questions about FAA drone regulations using AI and semantic search.

**Key Features:**
- 💬 **Chat Interface** - Ask questions about drone regulations
- 🤖 **AI-Powered Responses** - Uses Google Gemini API to synthesize answers
- 📚 **126 FAA Regulations** - Complete database of Part 108 regulations
- 🔍 **Smart Search** - Finds relevant regulations even with different wording
- 🎨 **Beautiful UI** - Modern, responsive design with dark theme
- ⚡ **Lightweight** - No heavy ML libraries, runs fast
- 📱 **Mobile-Friendly** - Works on phones, tablets, and desktops

**How it works:**
1. You ask a question (e.g., "Can I fly a drone near an airport?")
2. App searches through 126 FAA drone regulations
3. Finds the 5 most relevant regulations
4. Sends them to Google Gemini AI
5. Gemini synthesizes an intelligent answer based on the regulations
6. If no API key: Shows relevant regulations directly (fallback mode)

---

## 📋 Prerequisites

- **Python 3.8+** (Windows, Mac, or Linux)
- **Internet connection** (for Google Gemini API)
- **Google account** (for free API key)

---

## 🚀 Step-by-Step Setup

### Step 1: Get Your Google Gemini API Key

1. Visit: **https://aistudio.google.com/app/apikey**
2. Click **"Create API Key"**
3. Select **"Create API key in new project"**
4. Copy the API key (it will look like: `AIza...`)

### Step 2: Configure the .env File

**Option A: Using the .env File (Recommended)**

1. Open `.env.example` in the project folder
2. Paste your API key between the quotes:
   ```
   GOOGLE_API_KEY="AIza_YourActualKeyHere"
   ```
3. Save the file
4. **Rename it** from `.env.example` to `.env`
   - On Windows: Right-click → Rename
   - Or in PowerShell:
     ```powershell
     Rename-Item -Path ".env.example" -NewName ".env"
     ```

**Option B: Without .env File (App still works)**
- Skip the .env file, app will run in fallback mode
- It will show regulations but won't use AI for synthesis

---

## ▶️ How to Run the App

### On Windows (PowerShell)

```powershell
# 1. Navigate to the project folder
cd c:\Users\shubh\Downloads\RAG_Drone

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Run the app
python app.py
```

**Expected output:**
```
Loaded 126 drone rules
Creating embeddings for drone rules...
Created 126 embeddings
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### On Mac/Linux

```bash
cd /path/to/RAG_Drone
source venv/bin/activate
python app.py
```

---

## 🌐 Accessing the App

Once running, open your browser and go to:
```
http://localhost:5000
```

**What you'll see:**
- Header with drone icon and stats
- Sidebar with example queries and categories
- Chat area where you can ask questions
- Input field at the bottom to type your question

---

## 💬 Using the App

### Ask a Question

1. **Type your question** in the input field:
   - "What are the rules for flying a drone commercially?"
   - "Can I fly a drone over people?"
   - "What is the maximum altitude for drones?"
   - "Do I need a license to fly a drone?"

2. **Press Enter** or click the **Send button**

3. **Get your answer:**
   - **With API Key:** AI-synthesized answer based on relevant regulations
   - **Without API Key:** Top 3 relevant regulations with excerpts

4. **See relevant rules** below each response showing which regulations were used

### Example Queries

- "What are the requirements to fly a drone for delivery?"
- "Can commercial drones fly at night?"
- "What's the maximum altitude I can fly?"
- "Do I need insurance for commercial drone operations?"
- "What are the rules for flying drones near airports?"

---

## 🔧 Project Structure

```
RAG_Drone/
├── app.py                    # Main Flask application (backend)
├── requirements.txt          # Python dependencies
├── parsed_rules.json         # 126 FAA drone regulations database
├── .env.example             # Configuration template (rename to .env)
├── venv/                    # Virtual environment
├── templates/
│   └── index.html           # Web page (frontend)
└── static/
    ├── style.css            # Beautiful styling
    └── script.js            # Chat functionality
```

---

## 📦 Dependencies

The app uses minimal, lightweight dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.0 | Web framework |
| google-generativeai | 0.8.5 | Google Gemini AI |
| numpy | 1.24.3 | Math calculations |
| werkzeug | 3.0.1 | WSGI utilities |

**Total size:** ~500MB (mostly just Flask and dependencies)
**No heavy ML libraries:** No PyTorch, TensorFlow, or CUDA needed

---

## 🎯 Features Explained

### RAG System (Retrieval-Augmented Generation)
- **Retrieval:** Searches 126 regulations using keyword similarity
- **Augmentation:** Feeds the relevant regulations to AI
- **Generation:** AI creates an answer based on the regulations

### Semantic Search
- Uses word frequency analysis to match questions with regulations
- Finds relevant regulations even with different wording
- Top 5 most relevant regulations are always retrieved

### Fallback Mode
- Works **without** Google API key
- Shows the most relevant regulations directly
- Useful for testing or when API is unavailable

---

## 🛠️ Troubleshooting

### Issue: "API key not valid" Error
**Solution:**
1. Check your API key doesn't have extra spaces
2. Make sure you got it from: https://aistudio.google.com/app/apikey
3. Verify the .env file is in the project root folder

### Issue: "Port 5000 already in use"
**Solution:**
```powershell
# Kill the process using port 5000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force

# Or use a different port in app.py:
# Change the last line from app.run(debug=True) to:
# app.run(debug=True, port=5001)
```

### Issue: App won't start
**Solution:**
```powershell
# Reinstall dependencies
.\venv\Scripts\pip install -r requirements.txt

# Then try running again
python app.py
```

### Issue: Responses are slow
**Solution:**
- First query takes ~5 seconds (Gemini model loading)
- Subsequent queries are much faster
- This is normal for AI APIs

---

## 🔐 Security Notes

- **API Key:** Keep it private, don't share it
- **.env file:** Never commit this to GitHub (added to .gitignore)
- **Local only:** App runs on localhost by default (not accessible from internet)

---

## 📊 API Endpoints

If you want to integrate this with other apps:

```
GET  /                           # Main page
POST /api/query                  # Send a question
     { "query": "your question" }
     Returns: { "response": "...", "relevant_rules": [...] }

GET  /api/rules                  # Get all regulations
     Returns: Array of 126 regulations

GET  /api/categories             # Get regulation categories
     Returns: Array of categories
```

---

## 🎓 Learning Resources

- **Flask:** https://flask.palletsprojects.com/
- **Google Gemini API:** https://ai.google.dev/
- **RAG Concept:** https://en.wikipedia.org/wiki/Retrieval-augmented_generation

---

## ✅ Next Steps

1. ✅ Get API key from Google
2. ✅ Copy to .env file
3. ✅ Run the app
4. ✅ Ask questions!

**Need help?**
- Check the error messages in the terminal
- Verify your API key is correct
- Try the fallback mode without API key

---

## 📝 License

This project is built for educational purposes. The drone regulations are from the FAA and are public domain.

---

**Enjoy exploring drone regulations! 🚁✈️**
