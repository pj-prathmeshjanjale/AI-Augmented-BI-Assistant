"""
Memory-optimised Embedding Factory for RAG Knowledge Vectorization.

On Render free tier (512MB RAM), sentence-transformers + PyTorch uses ~350MB,
exceeding the limit when combined with FastAPI + LangChain.

Replaced with:
  1. Pure-Python TF-IDF embeddings (default) — zero model loading, <5MB RAM
  2. OpenAI-compatible API embeddings — zero local RAM (optional)
  3. HuggingFace — only if explicitly forced via EMBEDDING_PROVIDER=huggingface
"""

import os
import numpy as np
from typing import List, Optional
from langchain_core.embeddings import Embeddings


class LightweightTFIDFEmbeddings(Embeddings):
    """
    Pure-Python TF-IDF embedding model.
    No PyTorch, no transformers, no model download.
    Uses only numpy — extremely memory efficient (~2MB RAM).
    Produces dim-dimensional TF-IDF vectors for FAISS cosine similarity.
    """

    def __init__(self, dim: int = 512):
        self.dim = dim
        self._vocab: dict = {}
        self._idf: np.ndarray = np.array([])
        self._fitted = False

    def _tokenize(self, text: str) -> List[str]:
        import re
        return re.findall(r"[a-z0-9_]+", text.lower())

    def _fit(self, texts: List[str]) -> None:
        from collections import Counter
        import math
        all_tokens = [self._tokenize(t) for t in texts]
        freq = Counter(tok for toks in all_tokens for tok in toks)
        vocab_terms = [w for w, _ in freq.most_common(self.dim)]
        self._vocab = {w: i for i, w in enumerate(vocab_terms)}
        N = len(texts)
        idf = np.zeros(len(self._vocab))
        for toks in all_tokens:
            present = set(toks) & set(self._vocab)
            for tok in present:
                idf[self._vocab[tok]] += 1.0
        self._idf = np.log((N + 1.0) / (idf + 1.0)) + 1.0
        self._fitted = True

    def _embed_one(self, text: str) -> np.ndarray:
        from collections import Counter
        toks = self._tokenize(text)
        freq = Counter(toks)
        vec = np.zeros(len(self._vocab), dtype=np.float32)
        for tok, cnt in freq.items():
            if tok in self._vocab:
                idx = self._vocab[tok]
                tf = 1.0 + np.log(cnt) if cnt > 0 else 0.0
                vec[idx] = tf * self._idf[idx]
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        if len(vec) < self.dim:
            vec = np.pad(vec, (0, self.dim - len(vec)))
        else:
            vec = vec[:self.dim]
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self._fitted:
            self._fit(texts)
        return [self._embed_one(t).tolist() for t in texts]

    def embed_query(self, text: str) -> List[float]:
        if not self._fitted:
            self._fit([text])
        return self._embed_one(text).tolist()


_CACHED_EMBEDDINGS = None


def get_embedding_model(provider: Optional[str] = None):
    """
    Returns an embedding model instance.
    Default: LightweightTFIDFEmbeddings (zero model loading, <5MB RAM).
    Set EMBEDDING_PROVIDER=huggingface to use sentence-transformers locally.
    """
    global _CACHED_EMBEDDINGS
    if _CACHED_EMBEDDINGS is not None:
        return _CACHED_EMBEDDINGS

    selected = (provider or os.getenv("EMBEDDING_PROVIDER", "tfidf")).strip().lower()

    # OpenAI-compatible API embeddings (zero local RAM)
    if selected == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key:
            try:
                from langchain_openai import OpenAIEmbeddings
                print("[INFO] Initializing OpenAI text-embedding-3-small (API-based, zero local RAM)...")
                _CACHED_EMBEDDINGS = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=key)
                return _CACHED_EMBEDDINGS
            except Exception as e:
                print(f"[WARN] OpenAI embeddings failed: {e}. Using TF-IDF fallback.")

    # HuggingFace sentence-transformers (only if explicitly requested)
    if selected == "huggingface":
        print("[WARN] HuggingFace embeddings use ~350MB RAM — may exceed Render free tier limit!")
        try:
            try:
                import torch
                torch.set_num_threads(1)
                os.environ.setdefault("OMP_NUM_THREADS", "1")
                os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
            except Exception:
                pass
            from langchain_huggingface import HuggingFaceEmbeddings
            print("[INFO] Initializing HuggingFace all-MiniLM-L6-v2 embeddings...")
            _CACHED_EMBEDDINGS = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True, "batch_size": 8}
            )
            return _CACHED_EMBEDDINGS
        except Exception as e:
            print(f"[WARN] HuggingFace embeddings failed: {e}. Falling back to TF-IDF.")

    # Default: Lightweight TF-IDF (zero model loading, <5MB RAM)
    print("[INFO] Initializing LightweightTFIDFEmbeddings (zero model loading, <5MB RAM)...")
    _CACHED_EMBEDDINGS = LightweightTFIDFEmbeddings(dim=512)
    return _CACHED_EMBEDDINGS
