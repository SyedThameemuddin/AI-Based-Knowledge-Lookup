"""
utils/data_loader.py

Knowledge base ingestion pipeline.
Replaces rag_project/load_data.py — now exposed as a class for API use.

Supported file types: .xlsx, .xls, .csv, .txt
"""

import os
import pickle
import tempfile
import numpy as np
import faiss
import pandas as pd
from typing import Tuple, List, Dict, Any

from sentence_transformers import SentenceTransformer

from settings import config
from utils.rag_engine import rag_engine


class DataLoader:
    """
    Loads files, generates embeddings, builds a FAISS index, and saves it to disk.
    After indexing, it triggers a reload of the global RAGEngine singleton.
    """

    def __init__(self):
        # Lazily reuse rag_engine's already-loaded model to avoid duplicate RAM usage
        self._embed_model = None

    @property
    def embed_model(self) -> SentenceTransformer:
        """Return rag_engine's model if initialized, otherwise load fresh."""
        if rag_engine.embed_model is not None:
            return rag_engine.embed_model
        if self._embed_model is None:
            self._embed_model = SentenceTransformer(config.EMBED_MODEL)
        return self._embed_model

    # ── File Readers ────────────────────────────────────────────
    def _load_excel(self, file_path: str) -> Tuple[List[str], List[str]]:
        df = pd.read_excel(file_path)
        return self._dataframe_to_texts(df)

    def _load_csv(self, file_path: str) -> Tuple[List[str], List[str]]:
        df = pd.read_csv(file_path)
        return self._dataframe_to_texts(df)

    def _load_text(self, file_path: str) -> Tuple[List[str], List[str]]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Split into ~500-char chunks
        chunk_size = 500
        chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
        doc_ids = [f"chunk_{i}" for i in range(len(chunks))]
        return chunks, doc_ids

    def _dataframe_to_texts(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Convert each row of a DataFrame into a descriptive text string."""
        # Try to detect an ID column
        id_col = next(
            (col for col in df.columns if "id" in col.lower()),
            None
        )

        texts, doc_ids = [], []
        for i, row in df.iterrows():
            content = ". ".join([
                f"{col}: {row[col]}"
                for col in df.columns
                if pd.notna(row[col])
            ])
            texts.append(content)
            doc_ids.append(str(row[id_col]) if id_col else f"row_{i}")

        return texts, doc_ids

    def load_file(self, file_path: str) -> Tuple[List[str], List[str]]:
        """Dispatch to the correct reader based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".xlsx", ".xls"):
            return self._load_excel(file_path)
        elif ext == ".csv":
            return self._load_csv(file_path)
        elif ext == ".txt":
            return self._load_text(file_path)
        else:
            raise ValueError(
                f"Unsupported file type: '{ext}'. "
                "Supported formats: .xlsx, .xls, .csv, .txt"
            )

    # ── Indexing Pipeline ───────────────────────────────────────
    def load_and_index(self, file_path: str) -> Dict[str, Any]:
        """
        Full pipeline:
        1. Read file → extract (texts, document_ids)
        2. Generate sentence embeddings
        3. Build FAISS IndexFlatL2
        4. Save index + metadata to disk
        5. Reload the global rag_engine singleton

        Returns a dict with {document_count, status, message}.
        """
        print(f"\n📂 Loading file: {file_path}")
        texts, doc_ids = self.load_file(file_path)
        print(f"   Extracted {len(texts)} documents")

        print("   Generating embeddings...")
        embeddings = self.embed_model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")

        print("   Building FAISS index...")
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        try:
            from groq import Groq
            from settings import config
            # Grab a sample of up to 3 texts to give the LLM context
            sample_texts = "\\n".join(texts[:3])
            prompt = f"Based on the following sample rows from a dataset, suggest exactly 6 diverse and helpful natural language questions a user might ask about this data. Make them short. Output strictly 6 questions separated by newlines, starting each with a relevant single emoji. For example: '📊 What is the total count?'. Do not output anything else.\\n\\nDataset Sample:\\n{sample_texts}"
            
            client = Groq(api_key=config.GROQ_API_KEY)
            resp = client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            suggestions_text = resp.choices[0].message.content.strip()
            suggestions = [s.strip() for s in suggestions_text.split('\\n') if s.strip()]
            # Ensure we have at least 6, fallback if LLM messes up
            if len(suggestions) < 6:
                suggestions.extend(["🔍 What data is available?", "📊 Show a summary", "💡 What are the key insights?", "📋 List the top entries", "❓ What are the anomalies?", "📈 Show the distribution"][:6-len(suggestions)])
        except Exception as e:
            print(f"   ⚠ Could not generate suggestions: {e}")
            suggestions = ["🔍 What data is available?", "📊 Show a summary", "💡 What are the key insights?", "📋 List the top entries", "❓ What are the anomalies?", "📈 Show the distribution"]

        # Ensure output directory exists
        data_dir = os.path.dirname(config.INDEX_PATH) or "data"
        os.makedirs(data_dir, exist_ok=True)

        # Persist to disk
        faiss.write_index(index, config.INDEX_PATH)
        with open(config.METADATA_PATH, "wb") as f:
            pickle.dump({"texts": texts, "document_ids": doc_ids, "suggestions": suggestions}, f)

        print(f"   ✓ Index saved → {config.INDEX_PATH}")

        # Reload singleton so new queries use fresh index
        rag_engine.reload()

        return {
            "document_count": len(texts),
            "status": "success",
            "message": f"Successfully indexed {len(texts)} documents from {os.path.basename(file_path)}"
        }
