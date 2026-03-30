"""
services/service.py

Business logic layer for the AI Knowledge Lookup API.
Replaces the old CoffeeShopService + LangGraph agent with RAG-based logic.

Calls:
  - utils.rag_engine.RAGEngine  → for knowledge base queries
  - utils.data_loader.DataLoader → for file ingestion/indexing
"""

import traceback

from utils.rag_engine import rag_engine
from utils.data_loader import DataLoader
from utils.exceptions.custom_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode, ErrorCodeStatus
from constants.http_status import HttpStatusCode
from utils.helpers import KnowledgeHelper


class KnowledgeService:

    def __init__(self):
        self.helper = KnowledgeHelper()
        self.data_loader = DataLoader()

    # ── Query ────────────────────────────────────────────────────
    def query_service(self, user_query: str, top_k: int = 3):
        """
        Run user query through the RAG pipeline.
        Returns {answer, sources, query, document_count}.
        """
        try:
            print(f"\n🔍 Query service: '{user_query}' (top_k={top_k})")

            # Let RAGEngine handle whether it has data or not, so conversational greetings still work

            result = rag_engine.query(user_query, top_k)
            print("✅ Query completed successfully")
            return result

        except CustomAppException:
            raise

        except Exception as e:
            print("\n========== ACTUAL ERROR ==========")
            traceback.print_exc()
            print("==================================\n")

            self.helper.error_logger("query_service", __file__, str(e))

            raise CustomAppException(
                message=f"Query service error: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus.get(
                    ErrorCode.INTERNAL_SERVER_ERROR, "KB_RAG_002"
                )
            )

    # ── Upload ───────────────────────────────────────────────────
    def upload_service(self, file_content: bytes, filename: str):
        """
        Accept raw file bytes, write to a temp file, index it, return stats.
        Returns {document_count, status, message}.
        """
        import os
        import tempfile

        try:
            print(f"\n📤 Upload service: '{filename}'")

            suffix = os.path.splitext(filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name

            try:
                result = self.data_loader.load_and_index(tmp_path)
            finally:
                os.unlink(tmp_path)

            print(f"✅ Upload completed — {result['document_count']} documents indexed")
            return result

        except CustomAppException:
            raise

        except Exception as e:
            print("\n========== ACTUAL ERROR ==========")
            traceback.print_exc()
            print("==================================\n")

            self.helper.error_logger("upload_service", __file__, str(e))

            raise CustomAppException(
                message=f"Upload service error: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus.get(
                    ErrorCode.INTERNAL_SERVER_ERROR, "KB_RAG_003"
                )
            )

    # ── Health ───────────────────────────────────────────────────
    def health_service(self):
        """Return current engine stats for health check endpoint."""
        stats = rag_engine.get_stats()
        return {
            "status": "ok",
            "rag_engine": stats
        }