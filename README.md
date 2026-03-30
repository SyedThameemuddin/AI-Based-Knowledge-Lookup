# 🔍 FindX — AI Based Knowledge Lookup

> **Upload your data. Ask questions. Get instant, accurate answers — grounded in your actual data.**

FindX is an AI-powered chatbot that lets you upload Excel, CSV, or text files and query them using **natural language**. Powered by a RAG (Retrieval-Augmented Generation) pipeline using FAISS vector search and Groq's Llama 3.1 LLM.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Semantic Search** | Understands meaning, not just keywords |
| 🤖 **Agentic Data Manipulation** | Chat out loud to automatically rewrite, add, or delete data rows using a LangChain agent! |
| ⚡ **Instant Answers** | Responses in under 2 seconds via Groq |
| 📁 **Multi-Format** | Supports `.xlsx`, `.csv`, `.txt` uploads |
| 🎯 **No Hallucinations** | Answers only from your data, with source citations |
| 🔄 **Live Re-Indexing** | Upload new files anytime — no restart needed |
| 🌊 **Streaming Responses** | Typewriter effect with real-time AI output |
| 📋 **Response Metadata** | Response time, source count, model info, copy button |
| 💬 **Chat History** | Saved sessions in browser |
| 📊 **Dashboard** | Stats, upload zone, query history |
| 🔓 **100% Open Source** | FAISS + Llama 3.1 + FastAPI |

---

## 🚀 Quick Start

```bash
cd backend/src
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000/app/** → Login → Ask questions!

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Backend** | FastAPI (Python) |
| **Vector DB** | FAISS (by Meta) |
| **Embedding** | SentenceTransformers (`all-MiniLM-L6-v2`) |
| **LLM** | Llama 3.1 8B via Groq API |
| **Frontend** | HTML/CSS/JS (Dark glassmorphism theme) |
| **Data** | Pandas + openpyxl |

---

## 📖 Documentation

| Document | Description |
|---|---|
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Full business overview — for everyone |
| [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) | Complete technical architecture — for developers |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Step-by-step setup & running guide — for any machine |
| [PITCH_GUIDE.md](PITCH_GUIDE.md) | Presentation & business pitch guide |
| [openapi.yaml](backend/src/openapi.yaml) | OpenAPI 3.0.3 API specification |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/query` | Ask a question |
| `POST` | `/api/v1/upload` | Upload a file to index |
| `GET` | `/api/v1/health` | System health check |
| `GET` | `/api/v1/history` | Recent query history |

**Frontend Pages:**
- `http://localhost:8000/app/` (Landing)
- `http://localhost:8000/app/chat` (Chat interface)
- `http://localhost:8000/app/dashboard` (Stats & Upload)
- `http://localhost:8000/app/history` (Detailed query feed)

---

## 📁 Project Structure

```
AI Based Knowledge Lookup/
├── backend/src/          # FastAPI backend (RAG engine, API routes, sample data)
│   ├── data/             # Sample datasets (shipments.xlsx, customer_reviews.csv)
│   └── openapi.yaml      # OpenAPI 3.0.3 specification
├── frontend/             # Web UI (landing, chat, dashboard)
├── PROJECT_OVERVIEW.md   # Business documentation
├── TECHNICAL_DOCS.md     # Technical documentation
├── SETUP_GUIDE.md        # Setup & running guide
└── PITCH_GUIDE.md        # Presentation & pitch guide
```

---

## ⚙️ Configuration

1. Get a free API key from [console.groq.com](https://console.groq.com)
2. Create `backend/src/.env` (see `.env.example`)
3. Run the server

---

## 📜 License

College Project © 2026

---

*Built with ❤️ using FastAPI, FAISS, and Llama 3.1*
