"""
Embedding Model Factory for RAG Knowledge Vectorization.
Supports HuggingFace all-MiniLM-L6-v2 by default (no external API keys needed)
with optional OpenAI embeddings if configured.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Global cached embedding instance
_CACHED_EMBEDDINGS = None


def get_embedding_model(provider: Optional[str] = None):
    """
    Returns an embedding model instance.
    Defaults to HuggingFace 'sentence-transformers/all-MiniLM-L6-v2' (100% local & free).
    Falls back to OpenAI embeddings if provider is explicitly set to 'openai' and key is present.
    """
    global _CACHED_EMBEDDINGS
    if _CACHED_EMBEDDINGS is not None:
        return _CACHED_EMBEDDINGS

    selected_provider = (provider or os.getenv("EMBEDDING_PROVIDER", "huggingface")).strip().lower()

    if selected_provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("[INFO] OPENAI_API_KEY missing for embeddings, falling back to local HuggingFace all-MiniLM-L6-v2.")
        else:
            try:
                from langchain_openai import OpenAIEmbeddings
                print("[INFO] Initializing OpenAI text-embedding-3-small embeddings...")
                _CACHED_EMBEDDINGS = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_key)
                return _CACHED_EMBEDDINGS
            except Exception as e:
                print(f"[WARN] OpenAIEmbeddings init error: {e}. Falling back to HuggingFace.")

    # Default: HuggingFace all-MiniLM-L6-v2
    print("[INFO] Initializing local HuggingFace all-MiniLM-L6-v2 embeddings...")
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        _CACHED_EMBEDDINGS = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        return _CACHED_EMBEDDINGS
    except Exception as e:
        print(f"[WARN] langchain-huggingface failed: {e}. Trying fallback from langchain-community...")
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            _CACHED_EMBEDDINGS = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
            return _CACHED_EMBEDDINGS
        except Exception as e2:
            raise RuntimeError(f"Failed to initialize HuggingFace embeddings: {e2}")
