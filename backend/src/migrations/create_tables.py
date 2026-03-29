"""
migrations/create_tables.py

Startup migration for the RAG backend.
Ensures the data/ directory exists with the required files.
"""

import os


class Migration:

    def __init__(self):
        self.data_dir = "data"

    def run_startup_migration(self):
        """
        Called once at FastAPI startup.
        Ensures data/ directory exists.
        """
        os.makedirs(self.data_dir, exist_ok=True)
        print(f"✓ Data directory ready: {os.path.abspath(self.data_dir)}")

        # Check if FAISS index files exist
        index_path = os.path.join(self.data_dir, "faiss_index.index")
        meta_path  = os.path.join(self.data_dir, "metadata.pkl")

        if os.path.exists(index_path) and os.path.exists(meta_path):
            print(f"✓ FAISS index found — ready to serve queries")
        else:
            print(f"⚠ No FAISS index found — upload a file via POST /api/v1/upload to get started")


if __name__ == "__main__":
    migration = Migration()
    migration.run_startup_migration()