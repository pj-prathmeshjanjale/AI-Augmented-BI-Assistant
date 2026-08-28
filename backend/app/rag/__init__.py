"""
RAG (Retrieval-Augmented Generation) Module for AI-Augmented BI Assistant.
Integrates LangChain and FAISS for semantic schema and business domain retrieval.
"""

from app.rag.documents import get_knowledge_documents
from app.rag.embeddings import get_embedding_model
from app.rag.vector_store import (
    get_or_create_vector_store,
    rebuild_vector_store,
    FAISS_INDEX_DIR
)
from app.rag.retriever import RAGRetriever, get_retriever
from app.rag.rag_chain import generate_rag_sql, get_rag_chain

__all__ = [
    "get_knowledge_documents",
    "get_embedding_model",
    "get_or_create_vector_store",
    "rebuild_vector_store",
    "FAISS_INDEX_DIR",
    "RAGRetriever",
    "get_retriever",
    "generate_rag_sql",
    "get_rag_chain"
]
