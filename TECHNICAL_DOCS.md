# 🔧 FindX — Technical Documentation

## Complete Technical Architecture & Implementation Details

---

## 📌 Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Backend Architecture (FastAPI)](#backend-architecture-fastapi)
4. [RAG Pipeline — Deep Dive](#rag-pipeline--deep-dive)
5. [Frontend Architecture](#frontend-architecture)
6. [API Reference](#api-reference)
7. [Data Flow & Sequence Diagrams](#data-flow--sequence-diagrams)
8. [File Structure & Codebase Map](#file-structure--codebase-map)
9. [Configuration & Environment Variables](#configuration--environment-variables)
10. [Security Considerations](#security-considerations)
11. [Performance Characteristics](#performance-characteristics)
12. [Dependencies & Versions](#dependencies--versions)
13. [Known Issues & Debugging](#known-issues--debugging)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FindX System Architecture                         │
│                                                                                 │
│  ┌──────────────────┐     HTTP/REST      ┌──────────────────────────────────┐  │
│  │    FRONTEND       │ ◄──────────────► │         FASTAPI BACKEND          │  │
│  │                    │                   │                                    │  │
│  │  index.html        │   POST /query     │  app.py (main)                    │  │
│  │  chat.html         │   POST /upload    │    ├── routes/routes.py           │  │
│  │  dashboard.html    │   GET /health     │    ├── services/service.py        │  │
│  │                    │   GET /history    │    ├── utils/rag_engine.py  ──┐   │  │
│  │  css/styles.css    │                   │    ├── utils/data_loader.py   │   │  │
│  │  js/auth.js        │                   │    ├── models/dto_model.py    │   │  │
│  │  js/chat.js        │                   │    └── settings.py           │   │  │
│  │  js/dashboard.js   │                   │                               │   │  │
│  └──────────────────┘                   └──────────────────────────────┘  │  │
│                                                                            │  │
│                                          ┌──────────────────────────────┐  │  │
│                                          │     EXTERNAL SERVICES        │  │  │
│                                          │                              │  │  │
│                                          │  ┌────────────────────────┐  │  │  │
│                                          │  │  FAISS Index (Local)   │◄─┘  │  │
│                                          │  │  data/faiss_index      │     │  │
│                                          │  │  data/metadata.pkl     │     │  │
│                                          │  └────────────────────────┘     │  │
│                                          │                                │  │
│                                          │  ┌────────────────────────┐     │  │
│                                          │  │  Groq API (Cloud)      │     │  │
│                                          │  │  Llama 3.1 8B Instant  │     │  │
│                                          │  │  api.groq.com          │     │  │
│                                          │  └────────────────────────┘     │  │
│                                          │                                │  │
│                                          │  ┌────────────────────────┐     │  │
│                                          │  │  SentenceTransformers  │     │  │
│                                          │  │  all-MiniLM-L6-v2      │     │  │
│                                          │  │  (Local, downloaded)   │     │  │
│                                          │  └────────────────────────┘     │  │
│                                          └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|---|---|---|---|
| **Web Framework** | FastAPI | 0.115+ | REST API server with async support |
| **ASGI Server** | Uvicorn | 0.42+ | Production-grade ASGI server |
| **Vector Database** | FAISS (faiss-cpu) | 1.9+ | Approximate Nearest Neighbor search |
| **Embedding Model** | SentenceTransformers (all-MiniLM-L6-v2) | 3.x | Generates 384-dim embeddings |
| **LLM API** | Groq (groq Python SDK) | 0.18+ | Hosts Llama 3.1 8B for generation |
| **LLM Model** | Llama 3.1 8B Instant | — | Open-source language model by Meta |
| **Data Processing** | Pandas + openpyxl | 2.2+ / 3.1+ | Excel/CSV file parsing |
| **Matrix Operations** | NumPy | 1.26+ | Vector array operations |
| **Validation** | Pydantic | 2.x | Request/response data validation |
| **Config** | python-dotenv | 1.x | Environment variable management |
| **File Upload** | python-multipart | 0.0.18+ | Multipart form handling |
| **Language** | Python | 3.11+ | Backend programming language |

### Frontend

| Component | Technology | Purpose |
|---|---|---|
| **Structure** | HTML5 | Semantic page structure |
| **Styling** | Vanilla CSS | Custom design system (no frameworks) |
| **Logic** | Vanilla JavaScript (ES6+) | Client-side interactions |
| **Fonts** | Google Fonts (Space Grotesk + Inter) | Premium typography |
| **Design** | Glassmorphism + Dark theme | Modern, premium UI aesthetic |

### Infrastructure

| Component | Technology | Purpose |
|---|---|---|
| **Hosting** | Local (localhost:8000) | Development server |
| **Static Files** | FastAPI StaticFiles mount | Serves frontend at /app/ |
| **CORS** | FastAPI CORSMiddleware | Cross-origin request handling |
| **Storage** | Local filesystem (data/) | FAISS index persistence |

---

## Backend Architecture (FastAPI)

### Layered Architecture

The backend follows a strict **3-layer architecture** pattern:

```
  Routes (routes.py)          ← HTTP layer: request/response handling
    ↓
  Services (service.py)       ← Business logic: orchestration
    ↓
  Utils (rag_engine.py,       ← Data layer: FAISS, Groq, file I/O
         data_loader.py)
```

### Layer 1: Routes (`routes/routes.py`)

The `KnowledgeRoutes` class defines 4 API endpoints:

| Endpoint | Method | Purpose | Request Body | Response |
|---|---|---|---|---|
| `/api/v1/query` | POST | Query the knowledge base | `{user_query, top_k}` | `{answer, sources, query, document_count}` |
| `/api/v1/upload` | POST | Upload and index a file | `multipart/form-data (file)` | `{document_count, status, message}` |
| `/api/v1/health` | GET | System health check | None | `{status, rag_engine: {index_loaded, document_count, ...}}` |
| `/api/v1/history` | GET | Recent query history | None | `[{query, answer_preview, source_count}]` |

All responses are wrapped in the standardized `APIResponse` DTO:
```json
{
  "data": { ... },
  "message": "Query answered successfully",
  "errors": [],
  "code": 200
}
```

### Layer 2: Services (`services/service.py`)

The `KnowledgeService` class contains 3 methods:

- **`query_service(user_query, top_k)`** — Validates the engine is ready, calls `rag_engine.query()`, returns the result. Raises `CustomAppException` if the index isn't loaded.
- **`upload_service(file_content, filename)`** — Saves uploaded bytes to a temp file, calls `data_loader.load_and_index()`, cleans up temp file, returns indexing stats.
- **`health_service()`** — Calls `rag_engine.get_stats()` and returns engine status.

### Layer 3: Utils (RAG Engine + Data Loader)

#### `utils/rag_engine.py` — RAGEngine (Singleton)

The core AI component. Initialized once at application startup.

**Initialization (`initialize()`):**
1. Loads `SentenceTransformer('all-MiniLM-L6-v2')` — 22M parameter embedding model
2. Creates Groq client with API key
3. Loads FAISS index from `data/faiss_index.index`
4. Loads metadata (texts + doc_ids) from `data/metadata.pkl`

**Query Flow (`query(user_query, top_k)`):**
1. Embeds the user query → 384-dim float32 vector
2. FAISS `index.search()` → returns `top_k` nearest vectors + distances
3. Retrieves corresponding text chunks from metadata
4. Builds a prompt with context + user question
5. Calls Groq API (`chat.completions.create`) with Llama 3.1
6. Returns `{answer, sources, query, document_count}`

**Prompt Template:**
```
You are a helpful AI assistant. Answer the user's question based ONLY on the following context.
If the answer is not in the context, say "I don't have enough information to answer that."

Context:
[Source 1] (ID: SHP001): shipment_id: SHP001. status: In Transit. carrier: FedEx...
[Source 2] (ID: SHP002): shipment_id: SHP002. status: Delivered. carrier: UPS...
[Source 3] (ID: SHP009): shipment_id: SHP009. status: Delivered. carrier: USPS...

Question: What is the status of shipment SHP001?
```

#### `utils/data_loader.py` — DataLoader

**File Support:**
- `.xlsx/.xls` → `pd.read_excel()` → DataFrame → row-level text conversion
- `.csv` → `pd.read_csv()` → DataFrame → row-level text conversion
- `.txt` → Split into 500-character chunks

**Row-to-Text Conversion:**
Each DataFrame row is converted into a descriptive sentence:
```
"shipment_id: SHP001. status: In Transit. carrier: FedEx. origin: New York. destination: Los Angeles. delivery_date: 2024-01-15. weight: 15.5. value: 1200.0. remarks: Electronics shipment"
```

**Indexing Pipeline (`load_and_index(file_path)`):**
1. Parse file → extract `(texts[], doc_ids[])`
2. `embed_model.encode(texts)` → numpy array of shape `(N, 384)`
3. Build `faiss.IndexFlatL2(384)` → `index.add(embeddings)`
4. Save: `faiss.write_index(index, 'data/faiss_index.index')`
5. Save: `pickle.dump({texts, doc_ids}, 'data/metadata.pkl')`
6. Call `rag_engine.reload()` to refresh the singleton

### Application Lifecycle (`app.py`)

```python
@asynccontextmanager
async def lifespan(app):
    # STARTUP:
    Migration().run_startup_migration()  # Create data/ dir, copy FAISS from rag_project/
    rag_engine.initialize()               # Load embedding model + FAISS + Groq
    yield
    # SHUTDOWN: (nothing to tear down)
```

### Middleware & Exception Handling

- **CORS**: All origins allowed (`allow_origins=["*"]`) for development
- **Custom exceptions**: `CustomAppException` → wrapped in `APIResponse` with error code
- **Validation errors**: Pydantic `RequestValidationError` → formatted error array
- **Static files**: Frontend served at `/app/` via `StaticFiles(directory=, html=True)`

### Data Models (`models/dto_model.py`)

```python
class QueryRequest(BaseModel):
    user_query: str        # The natural language question
    top_k: int = 3         # Number of source documents to retrieve (1-10)

class APIResponse:
    data: Any              # Response payload
    message: str           # Human-readable message
    errors: List[Error]    # Error details (if any)
    code: int              # HTTP status code

class Error:
    code: str              # Error code (e.g., "INTERNAL_SERVER_ERROR")
    message: str           # Error description
    error_code_id: str     # Unique error identifier (e.g., "KB_RAG_001")
```

---

## RAG Pipeline — Deep Dive

### What is RAG?

**RAG (Retrieval-Augmented Generation)** is a technique that enhances an LLM's ability to answer questions by first retrieving relevant information from an external knowledge base, then using that information as context for the LLM's response.

```
                    RAG Pipeline in FindX
                    
User Question: "Which shipments are delayed?"
         │
         ▼
┌─────────────────────────┐
│  1. EMBED QUESTION       │  SentenceTransformer encodes the question
│  "Which shipments..."    │  → [0.023, -0.114, 0.892, ..., 0.045]
│  → 384-dim vector        │     (384 floating-point numbers)
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  2. SEARCH FAISS INDEX   │  FAISS L2 distance search
│  Compare question vector │  Finds 3 nearest vectors in the index
│  against all data vectors│  (milliseconds, even with millions of vectors)
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  3. RETRIEVE CONTEXT     │  Pull the original text for the 3 nearest vectors
│  Source 1: SHP003...     │  These are the most semantically similar records
│  Source 2: SHP007...     │  to the user's question
│  Source 3: SHP005...     │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  4. LLM GENERATION       │  Groq API → Llama 3.1 8B
│  Prompt:                 │  System: "Answer ONLY from context"
│  Context + Question      │  → Generates a grounded, formatted answer
│  → Clear, sourced answer │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  5. RESPONSE              │
│  Answer: "The following   │  Returned to the user with:
│  shipments are delayed:   │  - The answer text
│  1. SHP003 - ..."        │  - Source citations (text + doc_id + distance)
│  Sources: [3 retrieved]  │  - Document count
└─────────────────────────┘
```

### Embedding Model: all-MiniLM-L6-v2

| Property | Value |
|---|---|
| Architecture | Transformer (6 layers, 12 heads) |
| Parameters | 22.7 million |
| Output Dimensions | 384 |
| Max Sequence Length | 256 tokens |
| Training | Trained on 1 billion sentence pairs |
| Size on Disk | ~80 MB |
| Inference Speed | ~4ms per sentence (CPU) |

### FAISS Index: IndexFlatL2

| Property | Value |
|---|---|
| Index Type | Flat (exact search, no approximation) |
| Distance Metric | L2 (Euclidean distance) |
| Dimensions | 384 |
| Search Complexity | O(n) per query |
| Scalability | Handles up to ~1M vectors efficiently on CPU |

### LLM: Llama 3.1 8B Instant (via Groq)

| Property | Value |
|---|---|
| Model | meta-llama/llama-3.1-8b-instant |
| Parameters | 8 billion |
| Context Window | 128K tokens |
| Inference Provider | Groq (ultra-low latency) |
| Response Time | ~1-2 seconds |
| Cost | Free tier (limited rate) |
| Temperature | 0.3 (low randomness for factual answers) |
| Max Tokens | 1024 per response |

---

## Frontend Architecture

### Design System

The frontend uses a **custom CSS design system** built from scratch (no Tailwind, no Bootstrap):

- **Color Palette**: HSL-based dark theme with violet, cyan, pink, and emerald accents
- **Typography**: Space Grotesk (headings) + Inter (body) from Google Fonts
- **Effects**: Glassmorphism (backdrop-filter: blur), gradient borders, floating orbs
- **Animations**: fade-in-up, slide-in, typing dots, pulse rings, gradient shifts
- **Components**: Glass cards, badges, buttons (primary/secondary/ghost), form inputs

### JavaScript Architecture

| File | Responsibility |
|---|---|
| `auth.js` | Login/logout via localStorage, dummy auth, user profile population |
| `chat.js` | Chat logic: API calls, message rendering, sessions, typing indicator |
| `dashboard.js` | Stats loading, file upload with drag-drop, history table, toast notifications |

### State Management
- **User state**: `localStorage('findx_user')` — JSON object with name, email, initials, role
- **Chat sessions**: `localStorage('findx_sessions')` — Array of session objects with messages
- **No server-side sessions**: All state is client-side (browser-local)

### API Communication
All API calls use `fetch()` to `http://localhost:8000/api/v1/`:
- Queries: `POST /query` with JSON body
- Uploads: `POST /upload` with FormData
- Stats: `GET /health` and `GET /history`

---

## API Reference

### POST `/api/v1/query`

**Request:**
```json
{
  "user_query": "Which shipments are delayed?",
  "top_k": 3
}
```

**Success Response (200):**
```json
{
  "data": {
    "answer": "Based on the provided context, the following shipments are delayed:\n1. SHP003 - Status: Delayed...",
    "sources": [
      {
        "text": "shipment_id: SHP003. status: Delayed. carrier: DHL...",
        "document_id": "SHP003",
        "distance": 0.6543
      },
      {
        "text": "shipment_id: SHP007. status: Pending. carrier: FedEx...",
        "document_id": "SHP007",
        "distance": 0.8921
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

**Error Response (400 — No Index):**
```json
{
  "data": null,
  "message": null,
  "errors": [{
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Knowledge base is not loaded yet. Please upload a file via POST /api/v1/upload first.",
    "error_code_id": "KB_RAG_001"
  }],
  "code": 400
}
```

### POST `/api/v1/upload`

**Request:** `Content-Type: multipart/form-data`
```
file: [binary file data] (shipments.xlsx)
```

**Success Response (200):**
```json
{
  "data": {
    "document_count": 10,
    "status": "success",
    "message": "Successfully indexed 10 documents from shipments.xlsx"
  },
  "message": "Successfully indexed 10 documents from shipments.xlsx",
  "errors": [],
  "code": 200
}
```

### GET `/api/v1/health`

**Response (200):**
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
  "errors": [],
  "code": 200
}
```

### GET `/api/v1/history`

**Response (200):**
```json
{
  "data": [
    {
      "query": "Which shipments are delayed?",
      "answer_preview": "Based on the provided context, the following shipments are delayed: 1. SHP003...",
      "source_count": 3
    }
  ],
  "message": "Query history retrieved",
  "errors": [],
  "code": 200
}
```

---

## File Structure & Codebase Map

```
AI Based Knowlege Look up/
│
├── PROJECT_OVERVIEW.md          ← Business overview (this document)
├── TECHNICAL_DOCS.md            ← Technical documentation (you are here)
├── SETUP_GUIDE.md               ← Setup & running instructions
│
├── backend/
│   └── src/
│       ├── app.py               ← FastAPI main application (lifespan, CORS, routes, static files)
│       ├── settings.py          ← Configuration loader (reads .env)
│       ├── requirements.txt     ← Python dependencies
│       ├── .env                 ← Environment variables (API keys, paths)
│       │
│       ├── routes/
│       │   └── routes.py        ← API endpoints (query, upload, health, history)
│       │
│       ├── services/
│       │   └── service.py       ← Business logic (query, upload, health orchestration)
│       │
│       ├── utils/
│       │   ├── rag_engine.py    ← RAG singleton (FAISS + Groq + SentenceTransformers)
│       │   ├── data_loader.py   ← File ingestion pipeline (Excel/CSV/TXT → FAISS)
│       │   ├── helpers.py       ← Error logging utility
│       │   ├── logging_decorator.py ← Route logging decorator
│       │   └── exceptions/
│       │       ├── custom_exception.py  ← Custom exception class
│       │       └── error_codes.py       ← Error code registry
│       │
│       ├── models/
│       │   └── dto_model.py     ← Pydantic models (QueryRequest, APIResponse, Error)
│       │
│       ├── constants/
│       │   └── http_status.py   ← HTTP status code constants
│       │
│       ├── migrations/
│       │   └── create_tables.py ← Startup migration (creates data/, copies FAISS files)
│       │
│       └── data/                ← Runtime data directory (auto-created)
│           ├── faiss_index.index  ← FAISS binary index file
│           └── metadata.pkl       ← Pickled metadata (texts + document IDs)
│
├── frontend/
│   ├── index.html               ← Landing page + login
│   ├── chat.html                ← AI chatbot interface
│   ├── dashboard.html           ← Knowledge base management
│   │
│   ├── css/
│   │   └── styles.css           ← Complete design system (~600 lines)
│   │
│   └── js/
│       ├── auth.js              ← Authentication logic
│       ├── chat.js              ← Chat API integration + session management
│       └── dashboard.js         ← Dashboard stats, upload, history
│
└── rag_project/                 ← Original prototype (kept for reference)
    ├── load_data.py             ← Original data loading script
    ├── rag_query.py             ← Original query script
    ├── shipments.xlsx           ← Sample dataset (10 shipment records)
    ├── faiss_index.index        ← Pre-built FAISS index
    └── metadata.pkl             ← Pre-built metadata
```

---

## Configuration & Environment Variables

### `.env` File

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

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | API key for Groq cloud (free tier) | Required |
| `MODEL_NAME` | LLM model identifier | `llama-3.1-8b-instant` |
| `EMBED_MODEL` | SentenceTransformer model name | `all-MiniLM-L6-v2` |
| `INDEX_PATH` | Path to FAISS index file | `data/faiss_index.index` |
| `METADATA_PATH` | Path to metadata pickle file | `data/metadata.pkl` |
| `PORT` | Server port | `8000` |
| `HOST` | Server host | `0.0.0.0` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## Security Considerations

| Area | Current State | Production Recommendation |
|---|---|---|
| **Authentication** | Dummy (localStorage) | OAuth2 / JWT with proper backend validation |
| **API Key** | Hardcoded in .env | Use secret management (Vault, AWS Secrets) |
| **CORS** | All origins (`*`) | Restrict to specific domains |
| **File Upload** | No size/type validation beyond extension | Add virus scanning, size limits, content validation |
| **Data Storage** | Local filesystem | Encrypted at rest, access-controlled |
| **HTTPS** | Not configured (HTTP only) | TLS certificate required for production |
| **Rate Limiting** | None | Add rate limiting to prevent API abuse |

---

## Performance Characteristics

| Operation | Time | Details |
|---|---|---|
| **Embedding model load** | ~3-5 seconds | One-time at startup (all-MiniLM-L6-v2) |
| **Query embedding** | ~4 ms | Per query, CPU inference |
| **FAISS search** | <1 ms | IndexFlatL2 with 10 vectors |
| **Groq LLM generation** | ~1-2 seconds | Network round-trip to Groq API |
| **Total query time** | ~2-3 seconds | End-to-end |
| **File indexing (100 rows)** | ~2-5 seconds | Embed + build index + save |
| **File indexing (10,000 rows)** | ~30-60 seconds | Dominated by embedding time |
| **Memory usage** | ~300-500 MB | Embedding model + FAISS index |

---

## Dependencies & Versions

### Python Dependencies (`requirements.txt`)

```
fastapi              # Web framework
uvicorn[standard]    # ASGI server with hot-reload
python-dotenv        # .env file loader
groq                 # Groq API SDK
sentence-transformers # Embedding model
faiss-cpu            # Vector search engine
numpy                # Array operations
pandas               # Data manipulation
openpyxl             # Excel file reader
python-multipart     # File upload handling
pydantic             # Data validation
```

### Frontend Dependencies
- None (vanilla HTML/CSS/JS, no npm required)
- Google Fonts loaded via CDN: `Space Grotesk` + `Inter`

---

## Known Issues & Debugging

### Common Issues

| Issue | Cause | Solution |
|---|---|---|
| "Knowledge base is not loaded" | No FAISS index found at startup | Upload a file via dashboard, or ensure `rag_project/` has `faiss_index.index` |
| Groq API timeout | Rate limit exceeded on free tier | Wait 1-2 minutes, or upgrade Groq plan |
| `ModuleNotFoundError` | Missing Python dependency | Run `pip install -r requirements.txt` |
| Frontend shows "Offline" | Backend not running | Start with `python -m uvicorn app:app --reload` |
| CORS error in browser | Frontend opened as file:// | Use http://localhost:8000/app/ instead |
| Slow first query | Embedding model loading | Normal — first query takes ~5s, subsequent queries are ~2s |

### Debug Logging

The backend prints detailed logs with emoji indicators:
- `📂 Loading file: ...` — File ingestion started
- `🔍 Query service: '...'` — Query received
- `✅ Query completed successfully` — Success
- `❌ ERROR in: ...` — Error with full traceback

### Swagger UI

Interactive API testing is available at `http://localhost:8000/docs` — try any endpoint directly in the browser.

---

*© 2026 FindX — AI Based Knowledge Lookup. Technical Documentation.*
