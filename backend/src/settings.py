from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    port: int
    host: str
    log_level: str

    # Groq LLM
    GROQ_API_KEY: str
    MODEL_NAME: str

    # Embedding model
    EMBED_MODEL: str

    # FAISS index paths (relative to where app.py is run from)
    INDEX_PATH: str
    METADATA_PATH: str


def get_config():
    return Config(
        port=int(os.getenv("PORT", "8000")),
        host=os.getenv("HOST", "0.0.0.0"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),

        GROQ_API_KEY=os.getenv("GROQ_API_KEY", ""),
        MODEL_NAME=os.getenv("MODEL_NAME", "llama-3.1-8b-instant"),

        EMBED_MODEL=os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"),

        INDEX_PATH=os.getenv("INDEX_PATH", "data/faiss_index.index"),
        METADATA_PATH=os.getenv("METADATA_PATH", "data/metadata.pkl"),
    )


config = get_config()