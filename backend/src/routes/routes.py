"""
routes/routes.py

API Route definitions for the AI Knowledge Lookup backend.
Follows the same class-based Router pattern as the example backend.

Endpoints:
  POST /api/v1/query   — ask a question against the knowledge base
  POST /api/v1/upload  — upload a file to re-index the knowledge base
  GET  /api/v1/health  — system health check
  GET  /api/v1/history — retrieve in-memory query history (last 50)
"""

from fastapi import APIRouter, Body, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse

from models.dto_model import QueryRequest, APIResponse
from services.service import KnowledgeService
from utils.exceptions.custom_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode, ErrorCodeStatus
from constants.http_status import HttpStatusCode
from utils.logging_decorator import logging_decorator
from utils.helpers import KnowledgeHelper


# In-memory query history (last 50 queries, cleared on server restart)
_query_history: list = []


class KnowledgeRoutes:

    def __init__(self):
        self.service = KnowledgeService()
        self.helper = KnowledgeHelper()

        self.router = APIRouter(prefix="/api/v1", tags=["Knowledge Lookup"])

        self.router.add_api_route("/query",   self.query_route,   methods=["POST"])
        self.router.add_api_route("/upload",  self.upload_route,  methods=["POST"])
        self.router.add_api_route("/health",  self.health_route,  methods=["GET"])
        self.router.add_api_route("/history", self.history_route, methods=["GET"])
        self.router.add_api_route("/download", self.download_route, methods=["GET"])

    # ── POST /query ──────────────────────────────────────────────
    @logging_decorator
    def query_route(self, request: QueryRequest = Body(...)):
        try:
            resp = self.service.query_service(
                user_query=request.user_query,
                top_k=request.top_k
            )

            from datetime import datetime
            _query_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": request.user_query,
                "answer": resp["answer"],
                "answer_preview": (
                    resp["answer"][:120] + "..."
                    if len(resp["answer"]) > 120
                    else resp["answer"]
                ),
                "source_count": len(resp.get("sources", []))
            })
            if len(_query_history) > 50:
                _query_history.pop(0)

            api_resp = APIResponse(
                data=resp,
                message="Query answered successfully",
                code=HttpStatusCode.OK
            )
            return JSONResponse(content=api_resp.to_dict())

        except CustomAppException as ce:
            self.helper.error_logger("query_route", __file__, str(ce))
            api_response = ce.to_api_response()
            return JSONResponse(
                content=api_response.to_dict(),
                status_code=ce.status_code
            )

        except Exception as e:
            self.helper.error_logger("query_route", __file__, str(e))
            raise CustomAppException(
                message=f"Router error: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus.get(
                    ErrorCode.INTERNAL_SERVER_ERROR, "KB_ROUTE_001"
                )
            )

    # ── POST /upload ─────────────────────────────────────────────
    def upload_route(self, file: UploadFile = File(...)):
        try:
            content = file.file.read()
            resp = self.service.upload_service(content, file.filename)

            api_resp = APIResponse(
                data=resp,
                message=resp["message"],
                code=HttpStatusCode.OK
            )
            return JSONResponse(content=api_resp.to_dict())

        except CustomAppException as ce:
            self.helper.error_logger("upload_route", __file__, str(ce))
            api_response = ce.to_api_response()
            return JSONResponse(
                content=api_response.to_dict(),
                status_code=ce.status_code
            )

        except Exception as e:
            self.helper.error_logger("upload_route", __file__, str(e))
            raise CustomAppException(
                message=f"Upload error: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus.get(
                    ErrorCode.INTERNAL_SERVER_ERROR, "KB_ROUTE_002"
                )
            )

    # ── GET /health ──────────────────────────────────────────────
    def health_route(self):
        try:
            resp = self.service.health_service()
            api_resp = APIResponse(
                data=resp,
                message="System healthy",
                code=HttpStatusCode.OK
            )
            return JSONResponse(content=api_resp.to_dict())

        except Exception as e:
            return JSONResponse(
                content={"status": "error", "message": str(e)},
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
            )

    # ── GET /history ─────────────────────────────────────────────
    def history_route(self):
        try:
            api_resp = APIResponse(
                data=list(reversed(_query_history)),  # newest first
                message="Query history retrieved",
                code=HttpStatusCode.OK
            )
            return JSONResponse(content=api_resp.to_dict())

        except Exception as e:
            return JSONResponse(
                content={"status": "error", "message": str(e)},
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
            )

    # ── GET /download ────────────────────────────────────────────
    def download_route(self):
        try:
            from utils.rag_engine import rag_engine
            import os
            
            if not rag_engine.dataset_path or not os.path.exists(rag_engine.dataset_path):
                return JSONResponse(
                    content={"status": "error", "message": "No dataset currently loaded to download."},
                    status_code=404
                )
                
            filename = os.path.basename(rag_engine.dataset_path)
            return FileResponse(
                path=rag_engine.dataset_path, 
                filename=filename, 
                media_type="application/octet-stream"
            )
        except Exception as e:
            return JSONResponse(
                content={"status": "error", "message": str(e)},
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
            )