# BVLOS Ratio

A web-based application to help recreational users navigate FAA Part 108 NPRM documentation with category filtering, search functionality, and related regulations lookup.

## Features

- **Category Filtering**: Browse rules by category (Flight Operations, Registration & Compliance, No-Fly Zones & Airspace, Equipment & Technical)
- **Search**: Search rules by keyword
- **Rule Definitions**: One-line summaries and short paragraphs for each rule
- **Related Regulations**: Find related regulations from FAA official sources and web search
- **Single Source of Truth**: Both frontend and backend consume the same `/api/rules` data; no duplicate JSON copies

> **Note:** The previous retrieval-augmented question answering (RAG) feature has been removed to simplify the stack and eliminate heavy ML dependencies. The application now focuses on browsing, filtering, and searching the regulations directly.

## Setup

### Prerequisites

- Python 3.11+
- Firebase CLI
- Firebase project created

### Installation

1. Install Firebase CLI:
```bash
npm install -g firebase-tools
```

2. Login to Firebase:
```bash
firebase login
```

3. Initialize Firebase project:
```bash
firebase init
```

**Select these features:**
- ✓ Firestore (for rule data)
- ✓ Functions (for Python backend)
- ✓ Hosting (for frontend)
- ✓ Storage (for PDF files)

See `FIREBASE_SETUP.md` for detailed step-by-step instructions.

4. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Configuration

1. Update `.firebaserc` with your Firebase project ID
2. Set environment variables:
   - **`GOOGLE_API_KEY`** (recommended): Google Gemini API key for enhanced AI responses. Get one at https://makersuite.google.com/app/apikey
   - **`GOOGLE_SEARCH_API_KEY`** (optional): Google Search API key
   - **`GOOGLE_SEARCH_ENGINE_ID`** (optional): Google Custom Search Engine ID

**Setting environment variables:**

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

**For Cloud Run deployment**, set environment variables when deploying:
```bash
gcloud run deploy rag-api --source . --region us-central1 --project part-108-parser --allow-unauthenticated --port 8080 --set-env-vars GOOGLE_API_KEY=your-api-key-here
```

### Loading Documentation

1. Upload Part 108 NPRM file to Firebase Storage:
   - Place PDF file in Firebase Storage under `part108/` path
   - Or use Firebase Console to upload

2. Parse and load rules to Firestore:
```bash
python backend/load_rules.py
```

### PDF to JSON Export

Run the new extractor to convert the project PDFs into JSON structures that match the schema described above:

```bash
# Part 108 NPRM → parsed_rules_full.json
python backend/parse_pdf.py \
  --input "Part 108 NPRM.pdf" \
  --output parsed_rules_full.json \
  --schema part108_nprm \
  --format json

# Ground risk analysis → ground_risk_full.json
python backend/parse_pdf.py \
  --input "NPRM - GroundRisk - Kevin - V2.pdf" \
  --output ground_risk_full.json \
  --schema ground_risk_kevin_v2 \
  --format json
```

Use the `--dry-run` flag to validate the configuration without writing files. After generating JSON, you can spot-check the structure with Python:

```bash
python - <<'PY'
import json
from pathlib import Path

for path in ("parsed_rules_full.json", "ground_risk_full.json"):
    if not Path(path).exists():
        continue
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    print(path, "sections:", list(data.get("sections", {}).keys()))
PY
```

To generate JSONL prompt/completion datasets suitable for training:

```bash
python backend/parse_pdf.py \
  --input "Part 108 NPRM.pdf" \
  --output part108_dataset.jsonl \
  --schema part108_nprm \
  --format jsonl

python backend/parse_pdf.py \
  --input "NPRM - GroundRisk - Kevin - V2.pdf" \
  --output ground_risk_dataset.jsonl \
  --schema ground_risk_kevin_v2 \
  --format jsonl
```

Each JSONL line contains `prompt`, `completion`, and optional `metadata` describing the section path and page references used to build the pair. Use `--dry-run` to preview counts and sample output without writing files.

### Training Dataset API

The backend exposes the generated JSONL files via `/api/training-data`. Examples:

```bash
# Metadata plus first five prompt/completion pairs
curl "http://localhost:5000/api/training-data?dataset=part108&limit=5"

# Metadata only (set limit=0 and include_pairs=false)
curl "http://localhost:5000/api/training-data?dataset=ground_risk&limit=0&include_pairs=false"
```

Response payload:

- `dataset`: dataset key (`part108` or `ground_risk`)
- `total_pairs`: number of prompt/completion pairs available
- `returned_pairs`: number of pairs included in `pairs`
- `source_path`: relative path to the JSONL file
- `available_datasets`: datasets detected on disk
- `pairs`: optional array of prompt/completion items (omitted when `include_pairs=false`)

### Quick Test (Local)

1. Load sample data:
```bash
cd backend
python init_sample_data.py
```

2. Run backend:
```bash
python main.py
# Runs on http://localhost:5000
```

3. In another terminal, serve frontend (bind to IPv4 so `localhost` hits it):
```bash
cd frontend
python -m http.server 8000 --bind 127.0.0.1
```

> Tip (Windows): `py -3 -m http.server 8000 --bind 127.0.0.1` works as well if `python` isn’t on PATH.

The frontend automatically detects when it is running on `localhost:8000` and proxies requests to `http://localhost:5000/api`, so no manual code edits are required. For other custom deployments you can override the API endpoint by defining `window.API_BASE` before loading `static/js/app.js`.

4. Open http://localhost:8000 in browser


### Deployment

1. Deploy to Firebase:
```bash
firebase deploy
```

This will deploy:
- Frontend to Firebase Hosting
- Backend functions to Cloud Functions
- Storage and Firestore rules

## Project Structure

```
.
├── frontend/
│   ├── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── backend/
│   ├── main.py
│   ├── rules_parser.py
│   ├── faa_integration.py
│   └── requirements.txt
├── firebase.json
├── .firebaserc
├── storage.rules
└── firestore.rules
```

## API Endpoints

- `GET /api/rules?category={category}` - Get rules filtered by category
- `GET /api/search?q={query}` - Search rules by keyword
- `GET /api/related?topic={topic}` - Get related regulations
- `GET /api/categories` - Get all categories
- `GET /api/health` - Health check

## License

MIT

