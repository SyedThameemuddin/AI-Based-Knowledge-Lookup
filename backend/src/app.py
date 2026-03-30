import uvicorn
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from routes.routes import KnowledgeRoutes
from models.dto_model import APIResponse, Error
from utils.exceptions.custom_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode, ErrorCodeStatus
from constants.http_status import HttpStatusCode
from migrations.create_tables import Migration
from utils.rag_engine import rag_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────
    # 1. Ensure data/ directory exists & bootstrap existing FAISS files
    migration = Migration()
    migration.run_startup_migration()

    # 2. Initialize the RAG engine (loads embedding model + Groq client + index)
    rag_engine.initialize()

    yield
    # ── Shutdown (nothing to tear down) ──────────────────────────


app = FastAPI(
    title="AI Based Knowledge Lookup API",
    description=(
        "Intelligent RAG pipeline for knowledge retrieval. "
        "Upload any Excel/CSV/TXT file and query it using natural language — "
        "powered by FAISS vector search + Groq LLM (Llama 3.1, open-source)."
    ),
    version="1.0.0",
    lifespan=lifespan
)


# ── CORS Middleware ───────────────────────────────────────────────
# Allow all origins so the frontend (opened as a local file) can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)


# ── Routes ────────────────────────────────────────────────────────
router = KnowledgeRoutes()
app.include_router(router.router)

# ── Serve Frontend ───────────────────────────────────────────────
# Frontend is at ../../frontend relative to src/
_frontend_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)

# Clean URL routes — no .html extension exposed
@app.get("/")
async def root_redirect():
    return FileResponse(os.path.join(_frontend_dir, "index.html"))

@app.get("/app")
@app.get("/app/")
async def app_home():
    return FileResponse(os.path.join(_frontend_dir, "index.html"))

@app.get("/app/chat")
async def app_chat():
    return FileResponse(os.path.join(_frontend_dir, "chat.html"))

@app.get("/app/dashboard")
async def app_dashboard():
    return FileResponse(os.path.join(_frontend_dir, "dashboard.html"))

@app.get("/app/history")
async def app_history():
    return FileResponse(os.path.join(_frontend_dir, "history.html"))

# Static assets (CSS, JS, images) still served via mount
if os.path.isdir(_frontend_dir):
    app.mount("/app", StaticFiles(directory=_frontend_dir, html=False), name="frontend")
    print(f"✓ Frontend: http://localhost:8000/app/chat | /app/dashboard | /app/history")


# ── Global Exception Handlers ─────────────────────────────────────
@app.exception_handler(CustomAppException)
async def custom_exception_handler(request: Request, exc: CustomAppException):
    api_response = exc.to_api_response()
    return JSONResponse(
        status_code=exc.status_code,
        content=api_response.to_dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append(Error(
            code=ErrorCode.VALIDATION_ERROR,
            message=f"{error['loc'][-1]}: {error['msg']}",
            error_code_id="KB_VAL_004"
        ))
    api_response = APIResponse(
        data=None,
        errors=errors,
        code=HttpStatusCode.UNPROCESSABLE_ENTITY
    )
    return JSONResponse(
        status_code=HttpStatusCode.UNPROCESSABLE_ENTITY,
        content=api_response.to_dict()
    )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )