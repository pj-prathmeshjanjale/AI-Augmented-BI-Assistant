"""
RAG Telemetry and Observability Module.
Captures performance metrics, retrieved documents, relevance scores, and execution telemetry.
"""

import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RAGTelemetry(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    question: str
    active_mode: str
    retrieval_time_ms: float
    llm_time_ms: float
    total_time_ms: float
    retrieved_documents: List[Dict[str, Any]]
    generated_sql: str
    validation_status: str
    execution_success: bool
    rows_returned: int = 0
    error_message: Optional[str] = None


# Recent in-memory telemetry buffer for developer/debug inspection
_TELEMETRY_LOG: List[RAGTelemetry] = []


def record_rag_telemetry(
    question: str,
    active_mode: str,
    retrieval_ms: float,
    llm_ms: float,
    total_ms: float,
    retrieved_docs: List[Dict[str, Any]],
    generated_sql: str,
    validation_status: str,
    execution_success: bool,
    rows_returned: int = 0,
    error_message: Optional[str] = None
) -> RAGTelemetry:
    """Records a single RAG execution event in memory."""
    record = RAGTelemetry(
        question=question,
        active_mode=active_mode,
        retrieval_time_ms=round(retrieval_ms, 2),
        llm_time_ms=round(llm_ms, 2),
        total_time_ms=round(total_ms, 2),
        retrieved_documents=retrieved_docs,
        generated_sql=generated_sql,
        validation_status=validation_status,
        execution_success=execution_success,
        rows_returned=rows_returned,
        error_message=error_message
    )

    _TELEMETRY_LOG.append(record)
    if len(_TELEMETRY_LOG) > 50:
        _TELEMETRY_LOG.pop(0)

    return record


def get_recent_telemetry(limit: int = 10) -> List[Dict[str, Any]]:
    """Returns recent RAG telemetry records."""
    return [rec.dict() for rec in _TELEMETRY_LOG[-limit:]]
