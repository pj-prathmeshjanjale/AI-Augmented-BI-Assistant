"""
FAISS Vector Store Persistence, Creation, and Index Management.
Provides persistent storage, sub-millisecond loading, and manual rebuild commands.
"""

import os
import sys
from typing import Optional
from langchain_community.vectorstores import FAISS

from app.rag.documents import get_knowledge_documents
from app.rag.embeddings import get_embedding_model


FAISS_INDEX_DIR = os.path.join(os.path.dirname(__file__), "faiss_index")
_CACHED_VECTOR_STORE = None


def get_or_create_vector_store(force_rebuild: bool = False) -> FAISS:
    """
    Retrieves the persistent FAISS vector store.
    If the index exists on disk and force_rebuild is False, loads directly from disk.
    Otherwise, builds a new FAISS index from knowledge documents and persists it.
    """
    global _CACHED_VECTOR_STORE
    if _CACHED_VECTOR_STORE is not None and not force_rebuild:
        return _CACHED_VECTOR_STORE

    index_file = os.path.join(FAISS_INDEX_DIR, "index.faiss")
    embeddings = get_embedding_model()

    if not force_rebuild and os.path.exists(index_file):
        print(f"[INFO] Loading existing FAISS index from: {FAISS_INDEX_DIR}")
        try:
            vector_store = FAISS.load_local(
                FAISS_INDEX_DIR,
                embeddings,
                allow_dangerous_deserialization=True
            )
            _CACHED_VECTOR_STORE = vector_store
            return vector_store
        except Exception as load_err:
            print(f"[WARN] Failed to load existing index ({load_err}). Rebuilding from scratch...")

    # Build fresh vector index
    print(f"[INFO] Building fresh FAISS vector index...")
    docs = get_knowledge_documents()
    print(f"[INFO] Indexing {len(docs)} curated domain knowledge documents...")

    vector_store = FAISS.from_documents(docs, embeddings)
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    vector_store.save_local(FAISS_INDEX_DIR)
    print(f"[SUCCESS] Persisted FAISS vector index to: {FAISS_INDEX_DIR}")

    _CACHED_VECTOR_STORE = vector_store
    return vector_store


def rebuild_vector_store() -> FAISS:
    """Explicitly triggers a complete rebuild and persistence of the FAISS vector index."""
    return get_or_create_vector_store(force_rebuild=True)


if __name__ == "__main__":
    force = "--rebuild" in sys.argv or "-r" in sys.argv
    print("=" * 60)
    print("  FAISS VECTOR STORE MANAGEMENT CLI")
    print("=" * 60)
    vs = get_or_create_vector_store(force_rebuild=force)
    print(f"[SUCCESS] Vector store ready with {vs.index.ntotal} vectors.")
