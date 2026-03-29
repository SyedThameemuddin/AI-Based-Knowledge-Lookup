# 🔍 FindX — AI Based Knowledge Lookup

> **Upload your data. Ask questions. Get instant, accurate answers — grounded in your actual data.**

FindX is an AI-powered chatbot that lets you upload Excel, CSV, or text files and query them using **natural language**. Powered by a RAG (Retrieval-Augmented Generation) pipeline using FAISS vector search and Groq's Llama 3.1 LLM.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Semantic Search** | Understands meaning, not just keywords |
| ⚡ **Instant Answers** | Responses in under 2 seconds via Groq |
| 📁 **Multi-Format** | Supports `.xlsx`, `.csv`, `.txt` uploads |
| 🎯 **No Hallucinations** | Answers only from your data, with source citations |
| 🔄 **Live Re-Indexing** | Upload new files anytime — no restart needed |
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

Open **http://localhost:8000/app/index.html** → Login → Ask questions!

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

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/query` | Ask a question |
| `POST` | `/api/v1/upload` | Upload a file to index |
| `GET` | `/api/v1/health` | System health check |
| `GET` | `/api/v1/history` | Recent query history |

Interactive API docs: `http://localhost:8000/docs`

---

## 📁 Project Structure

```
AI Based Knowledge Lookup/
├── backend/src/          # FastAPI backend (RAG engine, API routes, sample data)
├── frontend/             # Web UI (landing, chat, dashboard)
├── PROJECT_OVERVIEW.md   # Business documentation
├── TECHNICAL_DOCS.md     # Technical documentation
└── SETUP_GUIDE.md        # Setup & running guide
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
