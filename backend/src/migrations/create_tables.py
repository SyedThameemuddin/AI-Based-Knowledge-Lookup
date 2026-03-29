"""
migrations/create_tables.py

Simplified startup migration for the RAG backend.
No database required — just ensures the data/ directory exists
and bootstraps the FAISS index from the original rag_project/ if available.
"""

import os
import shutil


class Migration:

    def __init__(self):
        # data/ directory is always relative to where app.py is run (src/)
        self.data_dir = "data"

        # Resolve absolute path to rag_project/ (3 levels up from migrations/)
        migrations_dir = os.path.dirname(os.path.abspath(__file__))  # .../src/migrations
        src_dir        = os.path.dirname(migrations_dir)              # .../src
        backend_dir    = os.path.dirname(src_dir)                     # .../backend
        project_dir    = os.path.dirname(backend_dir)                 # .../AI Based Knowlege Look up

        self.rag_project_dir = os.path.join(project_dir, "rag_project")

    def run_startup_migration(self):
        """
        Called once at FastAPI startup.
        1. Creates data/ directory
        2. Copies existing FAISS index from rag_project/ if data/ is empty
        """
        # 1. Ensure data/ directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        print(f"✓ Data directory ready: {os.path.abspath(self.data_dir)}")

        # 2. Bootstrap FAISS index from rag_project/ (if not already copied)
        dst_index    = os.path.join(self.data_dir, "faiss_index.index")
        dst_metadata = os.path.join(self.data_dir, "metadata.pkl")

        src_index    = os.path.join(self.rag_project_dir, "faiss_index.index")
        src_metadata = os.path.join(self.rag_project_dir, "metadata.pkl")

        if not os.path.exists(dst_index) and os.path.exists(src_index):
            shutil.copy2(src_index, dst_index)
            print(f"✓ Bootstrapped FAISS index from rag_project/")

        if not os.path.exists(dst_metadata) and os.path.exists(src_metadata):
            shutil.copy2(src_metadata, dst_metadata)
            print(f"✓ Bootstrapped metadata from rag_project/")


if __name__ == "__main__":
    migration = Migration()
    migration.run_startup_migration()