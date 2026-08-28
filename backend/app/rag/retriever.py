"""
Semantic Context Retriever for RAG Text-to-SQL Pipeline.
Performs similarity search against FAISS and formats relevant schema and business rules.
"""

import time
from typing import List, Dict, Any, Tuple, Optional
from langchain_core.documents import Document

from app.rag.vector_store import get_or_create_vector_store


class RAGRetriever:
    """
    Semantic Retriever wrapping the FAISS vector database.
    Provides top-k similarity search, relevance scoring, and query-tailored context compilation.
    """

    def __init__(self, top_k: int = 4, score_threshold: Optional[float] = None):
        self.top_k = top_k
        self.score_threshold = score_threshold
        self._vector_store = None

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = get_or_create_vector_store()
        return self._vector_store

    def retrieve(self, query: str, k: Optional[int] = None) -> Tuple[List[Document], List[float], float]:
        """
        Retrieves top-k relevant knowledge documents for a given natural language query.
        Returns tuple of (documents, scores, retrieval_time_ms).
        """
        target_k = k or self.top_k
        start_time = time.perf_counter()

        try:
            # Search with similarity scores
            results_with_scores = self.vector_store.similarity_search_with_score(query, k=target_k)
            docs = [item[0] for item in results_with_scores]
            # FAISS L2 distance: lower is closer. Convert to relevance score or keep raw distance
            scores = [float(item[1]) for item in results_with_scores]
        except Exception as err:
            print(f"[WARN] Similarity search error ({err}), falling back to standard search...")
            docs = self.vector_store.similarity_search(query, k=target_k)
            scores = [0.0] * len(docs)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return docs, scores, elapsed_ms

    def get_rag_context(
        self,
        query: str,
        session_id: Optional[str] = None,
        active_mode: str = "mysql",
        active_table: Optional[str] = None,
        k: Optional[int] = None
    ) -> Tuple[str, List[Dict[str, Any]], float]:
        """
        Compiles relevant domain context for the LLM prompt.
        Handles both default relational MySQL/SQLite database mode and uploaded CSV mode.
        """
        docs, scores, elapsed_ms = self.retrieve(query, k=k)

        retrieved_metadata = []
        for doc, score in zip(docs, scores):
            retrieved_metadata.append({
                "doc_id": doc.metadata.get("doc_id", "unknown"),
                "doc_type": doc.metadata.get("doc_type", "general"),
                "table": doc.metadata.get("table", "unknown"),
                "topic": doc.metadata.get("topic", "general"),
                "source": doc.metadata.get("source", "knowledge_base"),
                "similarity_score": round(score, 4),
                "snippet": doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
            })

        # =========================================================================
        # CSV DATASET MODE
        # =========================================================================
        if active_mode == "csv":
            from app.database.schema_loader import get_database_schema
            schema = get_database_schema(session_id=session_id)
            target_tbl = active_table or "uploaded_data"

            cols = schema.get(target_tbl, [])
            col_lines = "\n".join([f"- `{c['column']}` ({c['type']})" for c in cols]) if cols else "- (Dynamic columns)"

            # Filter retrieved docs to only general business calculations & SQL templates
            general_patterns = [
                d.page_content for d in docs
                if d.metadata.get("doc_type") in ["kpi_rule", "business_term", "sql_example"]
            ]
            patterns_text = "\n\n".join(general_patterns) if general_patterns else "Query from active uploaded CSV table."

            context = (
                f"ACTIVE DATASET: Uploaded CSV Dataset (`{target_tbl}`)\n"
                f"ACTIVE TABLE COLUMNS:\n{col_lines}\n\n"
                f"GENERAL ANALYTICAL RULES & PATTERNS:\n{patterns_text}\n"
            )
            return context, retrieved_metadata, elapsed_ms

        # =========================================================================
        # DEFAULT MYSQL / SQLITE 10-TABLE MODE
        # =========================================================================
        # Organize retrieved chunks logically
        schemas = []
        joins = []
        kpis = []
        patterns = []

        for doc in docs:
            dtype = doc.metadata.get("doc_type", "")
            if dtype == "table_schema":
                schemas.append(doc.page_content)
            elif dtype == "relationship":
                joins.append(doc.page_content)
            elif dtype == "kpi_rule":
                kpis.append(doc.page_content)
            else:
                patterns.append(doc.page_content)

        context_parts = ["DATABASE: business_db\n"]

        if schemas:
            context_parts.append("### RELEVANT TABLE SCHEMAS (RETRIEVED VIA FAISS):\n" + "\n\n".join(schemas))
        if joins:
            context_parts.append("\n### RELEVANT JOIN PATHS & CONSTRAINTS (RETRIEVED VIA FAISS):\n" + "\n\n".join(joins))
        if kpis:
            context_parts.append("\n### RELEVANT KPI METRIC FORMULAS (RETRIEVED VIA FAISS):\n" + "\n\n".join(kpis))
        if patterns:
            context_parts.append("\n### RELEVANT SQL PATTERNS & TERMINOLOGY:\n" + "\n\n".join(patterns))

        context = "\n".join(context_parts)
        return context, retrieved_metadata, elapsed_ms


# Global singleton instance
_RETRIEVER_INSTANCE = None


def get_retriever(top_k: int = 4) -> RAGRetriever:
    """Returns singleton RAGRetriever instance."""
    global _RETRIEVER_INSTANCE
    if _RETRIEVER_INSTANCE is None:
        _RETRIEVER_INSTANCE = RAGRetriever(top_k=top_k)
    return _RETRIEVER_INSTANCE
