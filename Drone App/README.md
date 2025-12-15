# Drone Regulations Assistant - RAG-based AI Application

An intelligent web application that uses Retrieval-Augmented Generation (RAG) with Google Gemini API to answer questions about FAA drone regulations.

## 🚀 Features

- **AI-Powered Responses**: Uses Google Gemini API for intelligent, context-aware answers
- **Semantic Search**: Leverages sentence transformers for accurate information retrieval
- **Beautiful UI/UX**: Modern, responsive design with smooth animations
- **Real-time Chat**: Interactive chat interface for natural conversations
- **Comprehensive Database**: Complete FAA drone regulations (Part 108)
- **Category Filtering**: Browse regulations by category
- **Example Queries**: Quick-start with pre-defined questions

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API Key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

## 🛠️ Installation

1. **Clone or navigate to the project directory**
```bash
cd RAG_Drone
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Google Gemini API Key**

Create a `.env` file in the project root or set environment variable:

**Option 1: Using .env file**
```bash
echo GOOGLE_API_KEY=AIzaSyBEZYhCh_Xp-d4ztL_0vTUIpuoSU-3TuoQ > .env
```

**Option 2: Set environment variable**
```bash
# Windows (PowerShell)
$env:GOOGLE_API_KEY="AIzaSyBEZYhCh_Xp-d4ztL_0vTUIpuoSU-3TuoQ"

# Windows (Command Prompt)
set GOOGLE_API_KEY=AIzaSyBEZYhCh_Xp-d4ztL_0vTUIpuoSU-3TuoQ

# macOS/Linux
export GOOGLE_API_KEY=AIzaSyBEZYhCh_Xp-d4ztL_0vTUIpuoSU-3TuoQ
```

## 🚀 Running the Application

1. **Start the Flask server**
```bash
python app.py
```

2. **Open your browser** and navigate to:
```
http://localhost:5000
```

## 💡 Usage

### Ask Questions
Simply type your question about drone regulations in the chat interface. Examples:
- "What are the requirements for operating a drone beyond visual line of sight?"
- "What are the weight restrictions for package delivery drones?"
- "What training is required for flight coordinators?"

### Use Example Queries
Click on any of the pre-defined example queries in the sidebar for quick answers.

### Browse Categories
Explore regulations by category such as:
- Flight Operations
- Registration
- Maintenance
- And more...

## 🏗️ Project Structure

```
RAG_Drone/
├── app.py                 # Flask backend with RAG implementation
├── parsed_rules.json      # Drone regulations database
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── style.css         # Styles
│   └── script.js         # Frontend JavaScript
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY` - Your Google Gemini API key (required for AI responses)

### Fallback Mode

If Google Gemini API is not configured, the app will run in fallback mode, providing direct excerpts from the regulations without AI enhancement.

## 🎨 Features in Detail

### RAG (Retrieval-Augmented Generation)

1. **Embedding Generation**: Uses `sentence-transformers` to create semantic embeddings of all regulations
2. **Semantic Search**: Finds the most relevant regulations using cosine similarity
3. **Context-Aware Responses**: Passes relevant regulations to Gemini for accurate, contextual answers

### User Interface

- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Dark Mode Compatible**: Easy on the eyes
- **Smooth Animations**: Polished user experience
- **Real-time Feedback**: Typing indicators and instant responses

## 🛡️ Security Notes

- Never commit your API keys to version control
- Use environment variables for sensitive data
- The `.env` file is gitignored by default

## 📊 Performance

- **Fast Search**: Semantic search returns results in milliseconds
- **Efficient Embeddings**: Pre-computed embeddings for quick retrieval
- **Optimized UI**: Lightweight frontend with minimal dependencies

## 🐛 Troubleshooting

### API Key Issues
If you see "Google Gemini API key not configured" in responses:
1. Verify your API key is set correctly
2. Restart the Flask server after setting the environment variable
3. Check API key validity at Google AI Studio

### Port Already in Use
If port 5000 is already in use:
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Dependencies Installation Errors
```bash
# Upgrade pip first
pip install --upgrade pip

# Then install dependencies
pip install -r requirements.txt
```

## 🔄 Updates

The application can be updated with new regulations by replacing the `parsed_rules.json` file. The embeddings will be automatically regenerated on the next startup.

## 📝 License

This project is provided as-is for educational and informational purposes.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📧 Support

For issues and questions, please create an issue in the repository.

---

**Made with ❤️ for the drone community**
