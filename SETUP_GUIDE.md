# 🚀 FindX — Complete Setup & Running Guide

## Run the Project from Scratch on Any Machine

---

## 📌 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [Detailed Setup (Step by Step)](#detailed-setup-step-by-step)
4. [Running the Backend](#running-the-backend)
5. [Accessing the Frontend](#accessing-the-frontend)
6. [Testing the API](#testing-the-api)
7. [Uploading Your Own Data](#uploading-your-own-data)
8. [Using the Chat Interface](#using-the-chat-interface)
9. [Using the Dashboard](#using-the-dashboard)
10. [API Documentation](#api-documentation)
11. [Troubleshooting](#troubleshooting)
12. [Setting Up on a New Machine (From ZIP)](#setting-up-on-a-new-machine-from-zip)
13. [Project Configuration](#project-configuration)
14. [Getting Your Own Groq API Key](#getting-your-own-groq-api-key)
15. [Stopping the Server](#stopping-the-server)
16. [Folder Structure Reference](#folder-structure-reference)

---

## Prerequisites

Before running FindX, make sure you have the following installed on your machine:

### Required Software

| Software | Minimum Version | How to Check | Download Link |
|---|---|---|---|
| **Python** | 3.10+ | `python --version` | [python.org/downloads](https://python.org/downloads) |
| **pip** | 21+ | `pip --version` | Comes with Python |
| **Git** (optional) | Any | `git --version` | [git-scm.com](https://git-scm.com/downloads) |

### System Requirements

| Resource | Minimum | Recommended |
|---|---|---|
| **RAM** | 4 GB | 8 GB (embedding model uses ~300 MB) |
| **Disk Space** | 2 GB | 3 GB (for model cache + dependencies) |
| **Internet** | Required | For Groq API calls and first-time model download |
| **OS** | Windows 10/11, macOS, Linux | Any modern OS with Python support |

### Network Requirements

| Service | URL | Required |
|---|---|---|
| Groq API | `api.groq.com` | Yes (for LLM answer generation) |
| HuggingFace Hub | `huggingface.co` | Yes (first run only, to download embedding model) |
| Google Fonts | `fonts.googleapis.com` | Optional (for frontend fonts) |

---

## Quick Start (5 Minutes)

If you want to get FindX running as fast as possible:

### Windows (PowerShell)

```powershell
# Step 1: Navigate to the backend
cd "AI Based Knowlege Look up\backend\src"

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Start the server
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### macOS / Linux (Terminal)

```bash
# Step 1: Navigate to the backend
cd "AI Based Knowlege Look up/backend/src"

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Start the server
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Open in Browser

Once the server starts (you'll see `Application startup complete`):

| Page | URL |
|---|---|
| **Landing Page** | http://localhost:8000/app/ |
| **Login** | Use any email + password (e.g., `demo@findx.io` / `demo1234`) |
| **Chat** | http://localhost:8000/app/chat |
| **Dashboard** | http://localhost:8000/app/dashboard |
| **History** | http://localhost:8000/app/history |
| **API Docs** | http://localhost:8000/docs |

---

## Detailed Setup (Step by Step)

### Step 1: Verify Python Installation

Open your terminal (PowerShell on Windows, Terminal on macOS/Linux) and run:

```bash
python --version
```

You should see something like `Python 3.11.x` or higher. If not, download Python from [python.org](https://python.org/downloads).

**Important (Windows):** During Python installation, check the box that says **"Add Python to PATH"**.

### Step 2: Navigate to the Project

```bash
# If you unzipped the project, navigate to it:
cd "path/to/AI Based Knowlege Look up"

# Example on Windows:
cd "C:\Users\YourName\Downloads\AI Based Knowlege Look up"

# Example on macOS/Linux:
cd ~/Downloads/"AI Based Knowlege Look up"
```

### Step 3: Navigate to the Backend Source

```bash
cd backend/src
```

### Step 4: (Optional) Create a Virtual Environment

A virtual environment keeps this project's dependencies separate from other Python projects:

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

You'll see `(venv)` at the beginning of your terminal prompt when activated.

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required Python packages:
- `fastapi` — Web framework
- `uvicorn` — Web server
- `sentence-transformers` — AI embedding model
- `faiss-cpu` — Vector search engine
- `groq` — AI language model API
- `pandas`, `openpyxl` — Data processing
- `python-dotenv`, `pydantic`, `python-multipart` — Utilities

**Expected time:** 2-5 minutes (depending on internet speed)

**Note:** The first time you run the server, the embedding model (`all-MiniLM-L6-v2`, ~80 MB) will be automatically downloaded from HuggingFace. This is a one-time download.

### Step 6: Verify the .env File

Make sure `backend/src/.env` exists with the following content:

```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.1-8b-instant
EMBED_MODEL=all-MiniLM-L6-v2
INDEX_PATH=data/faiss_index.index
METADATA_PATH=data/metadata.pkl
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

> **⚠️ Important:** The `GROQ_API_KEY` is a free-tier key. If it stops working, you can get your own for free — see [Getting Your Own Groq API Key](#getting-your-own-groq-api-key).

### Step 7: Verify Sample Data

The sample data (`shipments.xlsx`) and pre-built FAISS index are included in `backend/src/data/` and will load automatically on startup.

---

## Running the Backend

### Start the Server

From the `backend/src` directory:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### What You'll See

```
INFO:     Will watch for changes in these directories: ['...backend/src']
INFO:     Started reloader process [14424] using WatchFiles
✓ Data directory ready: .../backend/src/data
✓ FAISS index found — ready to serve queries
  ✓ Embedding model loaded: all-MiniLM-L6-v2
  ✓ Groq client ready — model: llama-3.1-8b-instant
  ✓ FAISS index loaded — 10 documents
✅ RAG Engine initialized
✓ Frontend: http://localhost:8000/app/chat | /app/dashboard
INFO:     Application startup complete.
```

### Server Flags Explained

| Flag | Meaning |
|---|---|
| `app:app` | Module name `:` FastAPI instance name |
| `--host 0.0.0.0` | Listen on all network interfaces |
| `--port 8000` | Server port number |
| `--reload` | Auto-restart when files change (development mode) |

### Alternative: Run with `python app.py`

```bash
python app.py
```

This uses the `if __name__ == "__main__"` block at the bottom of `app.py` with the same settings.

---

## Accessing the Frontend

Once the server is running, open your browser and go to:

### Available Pages

| Page | URL | Description |
|---|---|---|
| **Home / Login** | http://localhost:8000/app/ | Landing page with login form |
| **Chat** | http://localhost:8000/app/chat | AI chatbot interface |
| **Dashboard** | http://localhost:8000/app/dashboard | Knowledge base management |
| **History** | http://localhost:8000/app/history | Complete query history feed |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger documentation |
| **Root Redirect** | http://localhost:8000/ | Redirects to landing page |

### Login

FindX uses a **dummy authentication** system for demonstration:

- **Any email + any password (min 4 chars) will work**
- Demo suggested: Email: `demo@findx.io`, Password: `demo1234`
- Click the "Use Demo Account" button to auto-fill the credentials

After login, you'll be redirected to the chat page.

### Navigation

- **From Chat**: Click "📊 Dashboard" button in the header
- **From Dashboard**: Click "💬 Go to Chat" button or "Chat" in the sidebar
- **Logo**: Always links back to the landing page
- **Logout**: Click the ↩ button in the sidebar footer

---

## Testing the API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. You'll see all 4 endpoints listed
3. Click on any endpoint → "Try it out" → fill in parameters → "Execute"

### Using cURL (Terminal)

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### Query the Knowledge Base
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "What is the status of shipment SHP001?", "top_k": 3}'
```

#### Upload a File
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@path/to/your/data.xlsx"
```

#### Get Query History
```bash
curl http://localhost:8000/api/v1/history
```

### Using PowerShell (Windows)

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"

# Query
$body = @{ user_query = "Which shipments are delayed?"; top_k = 3 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" -Method Post -Body $body -ContentType "application/json"
```

### Using Python

```python
import requests

# Health check
r = requests.get("http://localhost:8000/api/v1/health")
print(r.json())

# Query
r = requests.post("http://localhost:8000/api/v1/query", json={
    "user_query": "Show me all shipments",
    "top_k": 3
})
print(r.json()["data"]["answer"])
```

### Expected Test Results

| Test | Expected Result |
|---|---|
| `GET /health` | `index_loaded: true`, `document_count: 10` |
| `POST /query` "Status of SHP001?" | Answer mentions "In Transit", "FedEx" |
| `POST /query` "Delayed shipments?" | Lists shipments with "Delayed" status |
| `POST /upload` (any .xlsx) | `status: success`, `document_count: N` |
| `GET /history` | Array of recent queries |

---

## Uploading Your Own Data

### Via Dashboard (Recommended)

1. Go to http://localhost:8000/app/dashboard
2. Scroll to the **"Upload Knowledge Base"** section
3. **Drag and drop** your file onto the upload zone, or click to browse
4. Wait for the indexing to complete (~2-30 seconds depending on file size)
5. You'll see a green success message: "✅ Successfully indexed N documents"

### Via Chat Sidebar

1. In the chat page, find **"📤 Upload new file"** in the left sidebar
2. Click it and select your file
3. Wait for the "✅ N docs indexed" confirmation

### Via Chat Input Area

1. Click the **📎** (paperclip) button next to the send button
2. Select your file
3. Wait for indexing

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@/path/to/yourdata.xlsx"
```

### Supported File Formats

| Format | Extension | How It's Processed |
|---|---|---|
| **Excel** | `.xlsx`, `.xls` | Each row → descriptive text sentence |
| **CSV** | `.csv` | Each row → descriptive text sentence |
| **Text** | `.txt` | Split into 500-character chunks |

### Data Format Tips

For best results with Excel/CSV files:
- **Include headers**: Column names become part of the text (e.g., "status: In Transit")
- **Include an ID column**: Any column with "id" in its name will be used as the document identifier
- **Keep data clean**: Remove empty rows and columns
- **One topic per file**: Each file replaces the previous knowledge base

---

## Using the Chat Interface

### Asking Questions

1. Type your question in the text box at the bottom
2. Press **Enter** to send (or click the **➤** button)
3. Wait 2-3 seconds for the AI response
4. View the answer with source citations

### Quick Suggestion Chips

Click any suggestion chip in the center welcome area or sidebar for instant queries:
- 📊 "What data is available?"
- 📦 "Show all shipments"
- ✅ "Delivered items"
- 💰 "Shipment values"
- 🚚 "All carriers"
- 🏆 "Highest value shipment"

### Viewing Sources

Each AI response includes a **"📚 N sources retrieved"** collapsible panel:
- Click it to expand and see the exact data records used
- Each source shows the document ID and a preview of the text

### Adjusting Sources Per Query

In the sidebar, find **"Sources: [3] per query"**:
- Change the number (1-10) to control how many source documents are retrieved
- More sources = more context for the AI, but potentially slower
- Fewer sources = faster responses, but may miss relevant information

### Session Management

- **New Chat**: Click "✦ New Chat" to start a fresh conversation
- **History**: Previous sessions appear in the sidebar under "Recent Sessions"
- **Load Session**: Click any session to reload it
- **Clear History**: Click "🗑 Clear history" to delete all sessions

---

## Using the Dashboard

### Stats Cards

| Card | Shows |
|---|---|
| **Documents Indexed** | Number of data entries in the FAISS index |
| **Queries This Session** | How many queries have been made since server start |
| **Engine Status** | "Active" if the RAG engine is loaded |
| **Embedding Model** | Name of the embedding model in use |

### Knowledge Base Info

Displays detailed information about the current index:
- **Documents**: Total count
- **Embedding Model**: `all-MiniLM-L6-v2`
- **LLM Model**: `llama-3.1-8b-instant`
- **Index Location**: `data/faiss_index.index`
- **Status Badge**: Green "Loaded ✓" or "Not Loaded"

### File Upload

- Drag-and-drop or click the upload zone
- Supports `.xlsx`, `.xls`, `.csv`, `.txt`
- Shows real-time progress and success/error feedback
- Stats auto-refresh after successful upload

### Query History

A table showing recent queries with:
- The original question
- A preview of the AI's answer
- Number of sources retrieved

### API Endpoints Reference

Quick reference cards showing all 4 endpoints with their methods, paths, and descriptions.

---

## API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Summary

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/query` | Ask a question about the knowledge base |
| `POST` | `/api/v1/upload` | Upload a file to index |
| `GET` | `/api/v1/health` | Check system status |
| `GET` | `/api/v1/history` | View recent queries |

### Request/Response Examples

#### Query Request
```json
POST /api/v1/query
Content-Type: application/json

{
  "user_query": "Which shipments are delayed?",
  "top_k": 3
}
```

#### Query Response
```json
{
  "data": {
    "answer": "Based on the provided context, the following shipments are delayed:\n1. SHP003 - Delayed, Carrier: DHL\n...",
    "sources": [
      {
        "text": "shipment_id: SHP003. status: Delayed...",
        "document_id": "SHP003",
        "distance": 0.654
      }
    ],
    "query": "Which shipments are delayed?",
    "document_count": 10
  },
  "message": "Query answered successfully",
  "errors": [],
  "code": 200
}
```

#### Upload Request
```bash
POST /api/v1/upload
Content-Type: multipart/form-data

file: <binary file data>
```

#### Health Response
```json
{
  "data": {
    "status": "ok",
    "rag_engine": {
      "index_loaded": true,
      "document_count": 10,
      "embedding_model": "all-MiniLM-L6-v2",
      "llm_model": "llama-3.1-8b-instant"
    }
  },
  "message": "System healthy",
  "code": 200
}
```

---

## Troubleshooting

### Problem: `pip install` fails

**Symptoms**: Error during `pip install -r requirements.txt`

**Solutions**:
1. Upgrade pip: `python -m pip install --upgrade pip`
2. On Windows, if you see permission errors: `pip install --user -r requirements.txt`
3. If `faiss-cpu` fails on an older system: `pip install faiss-cpu==1.7.4`
4. If you're behind a proxy: `pip install --proxy http://proxy:port -r requirements.txt`

### Problem: `ModuleNotFoundError`

**Symptoms**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Make sure you installed dependencies. If using a virtual environment, make sure it's activated (`source venv/bin/activate` or `venv\Scripts\activate`).

### Problem: Server won't start — port 8000 in use

**Symptoms**: `Address already in use`

**Solutions**:
1. Stop the other process using port 8000
2. Use a different port: `python -m uvicorn app:app --port 8001`
3. On Windows, find and kill the process: `netstat -ano | findstr 8000` then `taskkill /PID <pid> /F`

### Problem: "Knowledge base is not loaded"

**Symptoms**: Query returns error "Knowledge base is not loaded yet"

**Solutions**:
1. Check that `backend/src/data/` contains `faiss_index.index` and `metadata.pkl`
2. Or upload a file via the dashboard
3. Check the terminal for startup errors

### Problem: Groq API error / timeout

**Symptoms**: "Groq API error" or slow responses

**Solutions**:
1. Check your internet connection
2. The free-tier Groq key has rate limits — wait 1-2 minutes
3. Get your own Groq API key (see below)
4. Check `api.groq.com` status

### Problem: Frontend shows "Offline" status

**Symptoms**: The chat header shows "Offline" in red

**Solution**: Make sure the backend is running at `http://localhost:8000`. Check the terminal for errors.

### Problem: CORS errors in browser console

**Symptoms**: `Access-Control-Allow-Origin` errors

**Solution**: Access the frontend via `http://localhost:8000/app/` (not `file://`).

### Problem: Embedding model download is slow

**Symptoms**: First startup takes a very long time

**Solution**: This is normal on first run — the `all-MiniLM-L6-v2` model (~80 MB) is being downloaded from HuggingFace. Subsequent startups will be fast.

---

## Setting Up on a New Machine (From ZIP)

If you received this project as a ZIP file, follow these exact steps:

### Step 1: Extract the ZIP

Extract `AI Based Knowlege Look up.zip` to a folder of your choice.

### Step 2: Open Terminal

Navigate to the extracted folder:
```bash
cd "path/to/AI Based Knowlege Look up"
```

### Step 3: Check Python

```bash
python --version
```
Must be 3.10 or higher. If not installed, download from [python.org](https://python.org/downloads).

### Step 4: Create Virtual Environment (Recommended)

```bash
cd backend/src
python -m venv venv

# Activate:
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Verify .env

Open `backend/src/.env` and verify the `GROQ_API_KEY` is present. If the key has expired, get a new one from [console.groq.com](https://console.groq.com).

### Step 7: Run the Server

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Step 8: Open the App

Open your browser to: **http://localhost:8000/app/**

That's it! The system will automatically:
- Create the `data/` directory
- Load the FAISS index from `backend/src/data/`
- Download the embedding model (first time only)
- Initialize the RAG engine

---

## Getting Your Own Groq API Key

If the included API key has expired or you want your own:

### Step 1: Create an Account

Go to [console.groq.com](https://console.groq.com) and sign up (free).

### Step 2: Generate an API Key

1. Go to **API Keys** in the left sidebar
2. Click **Create API Key**
3. Give it a name (e.g., "FindX")
4. Copy the key (starts with `gsk_`)

### Step 3: Update .env

Open `backend/src/.env` and replace the `GROQ_API_KEY` value:

```env
GROQ_API_KEY=gsk_your_new_key_here
```

### Step 4: Restart the Server

```bash
# Stop the server (Ctrl+C)
# Start it again
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Groq Free Tier Limits

| Limit | Value |
|---|---|
| Requests per minute | 30 |
| Requests per day | 14,400 |
| Tokens per minute | 6,000 |
| Monthly cost | $0 (free) |

---

## Stopping the Server

### Stop the Running Server

Press **Ctrl+C** in the terminal where the server is running.

### Deactivate Virtual Environment

```bash
deactivate
```

---

## Folder Structure Reference

```
AI Based Knowlege Look up/
│
├── 📄 PROJECT_OVERVIEW.md           ← Business overview (non-technical)
├── 📄 TECHNICAL_DOCS.md             ← Technical documentation (for developers)
├── 📄 SETUP_GUIDE.md                ← This file (setup & running guide)
│
├── 📁 backend/
│   └── 📁 src/
│       ├── 📄 app.py                ← Main FastAPI application
│       ├── 📄 settings.py           ← Configuration
│       ├── 📄 requirements.txt      ← Python dependencies
│       ├── 📄 .env                  ← API keys & settings (create from .env.example)
│       ├── 📁 routes/               ← API endpoints
│       ├── 📁 services/             ← Business logic
│       ├── 📁 utils/                ← RAG engine, data loader, helpers
│       ├── 📁 models/               ← Data models (DTOs)
│       ├── 📁 constants/            ← HTTP status codes
│       ├── 📁 migrations/           ← Startup migration
│       └── 📁 data/                 ← FAISS index + sample data
│           ├── 📄 faiss_index.index
│           ├── 📄 metadata.pkl
│           └── 📄 shipments.xlsx
│
├── 📁 frontend/
│   ├── 📄 index.html                ← Landing page + login
│   ├── 📄 chat.html                 ← AI chatbot
│   ├── 📄 dashboard.html            ← Knowledge base management
│   ├── 📁 css/styles.css            ← Design system
│   └── 📁 js/                       ← Auth, chat, dashboard logic
```

---

## Summary: From Zero to Running

```
1. Install Python 3.10+                     (one time)
2. cd backend/src                            (navigate)
3. pip install -r requirements.txt           (one time)
4. python -m uvicorn app:app --port 8000 --reload   (start)
5. Open http://localhost:8000/app/  (browse)
6. Login with any email/password             (use)
7. Ask questions!                            (enjoy)
```

**Total setup time: ~5 minutes (plus dependency download)**

---

*© 2026 FindX — AI Based Knowledge Lookup. Setup Guide.*
