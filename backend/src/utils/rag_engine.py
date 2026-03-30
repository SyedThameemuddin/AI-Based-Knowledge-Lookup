"""
utils/rag_engine.py

Core RAG (Retrieval-Augmented Generation) engine.
Replaces the agent/ folder from the example backend.

Responsibilities:
  - Load FAISS vector index + metadata from disk
  - Embed user queries with SentenceTransformer
  - Retrieve top-K most relevant document chunks via FAISS
  - Generate natural-language answers using Groq LLM (Llama 3.1)
  - Expose a singleton `rag_engine` for import across the project
"""

import os
import pickle
import faiss
import numpy as np
from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer
from groq import Groq

from settings import config


class RAGEngine:
    """Singleton RAG pipeline: FAISS retrieval + Groq LLM generation."""

    _instance = None

    def __init__(self):
        self.index = None
        self.texts: List[str] = []
        self.document_ids: List[str] = []
        self.suggestions: List[str] = ["🔍 What data is available?", "📦 Show all items", "✅ Successful operations", "💰 Total values", "🚚 View categories", "🏆 Top records"]
        self.embed_model = None
        self.groq_client = None
        self._loaded = False

    # ── Singleton ───────────────────────────────────────────────
    @classmethod
    def get_instance(cls) -> "RAGEngine":
        if cls._instance is None:
            cls._instance = RAGEngine()
        return cls._instance

    # ── Lifecycle ───────────────────────────────────────────────
    def initialize(self):
        """
        Called once at FastAPI startup (lifespan).
        Loads the embedding model, Groq client, and existing FAISS index.
        """
        print("\n🚀 Initializing RAG Engine...")

        # Sentence embedding model (384-dim, runs locally, no API key needed)
        print("  Loading embedding model...")
        self.embed_model = SentenceTransformer(config.EMBED_MODEL)
        print(f"  ✓ Embedding model loaded: {config.EMBED_MODEL}")

        # Groq client — free, open-source LLM API
        self.groq_client = Groq(api_key=config.GROQ_API_KEY)
        print(f"  ✓ Groq client ready — model: {config.MODEL_NAME}")

        # Load any pre-existing FAISS index
        self.load_index()

        print("✅ RAG Engine initialized\n")

    def load_index(self):
        """Load FAISS index and metadata from disk (if they exist)."""
        index_path = config.INDEX_PATH
        metadata_path = config.METADATA_PATH

        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, "rb") as f:
                    metadata = pickle.load(f)

                self.texts = metadata.get("texts", [])
                self.document_ids = metadata.get(
                    "document_ids",
                    metadata.get("shipment_ids", [f"doc_{i}" for i in range(len(self.texts))])
                )
                self.suggestions = metadata.get("suggestions", self.suggestions)
                self._loaded = True
                print(f"  ✓ FAISS index loaded — {len(self.texts)} documents")
            except Exception as e:
                print(f"  ⚠ Could not load existing index: {e}")
                self._loaded = False
        else:
            print("  ℹ No existing index found. Upload a knowledge base file to begin.")
            self._loaded = False

    def reload(self):
        """Reload index from disk after a new upload."""
        print("\n🔄 Reloading FAISS index...")
        self.load_index()

    # ── Core RAG Methods ────────────────────────────────────────
    def is_ready(self) -> bool:
        """Returns True if the engine has an index loaded with documents."""
        return self._loaded and self.index is not None and len(self.texts) > 0

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Embed query and retrieve top-K relevant document chunks from FAISS.
        Returns list of {text, document_id, distance} dicts.
        """
        if not self.is_ready():
            raise ValueError(
                "Knowledge base not loaded. Please upload a file via POST /api/v1/upload first."
            )

        query_embedding = self.embed_model.encode([query]).astype("float32")
        k = min(top_k, len(self.texts))
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0:
                results.append({
                    "text": self.texts[idx],
                    "document_id": (
                        self.document_ids[idx]
                        if idx < len(self.document_ids)
                        else f"doc_{idx}"
                    ),
                    "distance": round(float(distances[0][i]), 4)
                })
        return results

    def generate_answer(self, query: str, context_chunks: List[Dict]) -> str:
        """
        Generate a natural-language answer using Groq LLM (Llama 3.1).
        Context is injected into the prompt as retrieval results.
        """
        context = "\n\n".join(
            [f"[Source {i + 1}]: {c['text']}" for i, c in enumerate(context_chunks)]
        )

        prompt = f"""You are an intelligent AI knowledge lookup assistant.
Answer the user's question using ONLY the context provided below.
If the context does not contain enough information, clearly state that.

Context:
{context}

Question: {query}

Instructions:
- Be concise and accurate
- Reference specific data points from the context when relevant
- Format the answer in a readable way
- Do not fabricate information not present in the context
"""

        response = self.groq_client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content

    def query(self, user_query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Full RAG pipeline: search → generate.
        Returns {answer, sources, query, document_count}.
        """
        results = self.search(user_query, top_k)
        answer = self.generate_answer(user_query, results)

        return {
            "answer": answer,
            "sources": results,
            "query": user_query,
            "document_count": len(self.texts)
        }

    def get_stats(self) -> Dict[str, Any]:
        """Return engine statistics for the health endpoint."""
        return {
            "index_loaded": self._loaded,
            "document_count": len(self.texts),
            "embedding_model": config.EMBED_MODEL,
            "llm_model": config.MODEL_NAME,
            "suggestions": self.suggestions[:6]
        }


# ── Global singleton (imported by other modules) ────────────────
rag_engine = RAGEngine.get_instance()
