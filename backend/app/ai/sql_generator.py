"""
Text-to-SQL Generator Module.
Integrates LangChain + FAISS RAG for semantic context retrieval and SQL synthesis.
"""

from typing import Optional, List, Dict, Any
from app.rag.rag_chain import generate_rag_sql, build_rag_prompt_template
from app.ai.schema_context import build_schema_context


def build_sql_prompt(user_question: str, session_id: Optional[str] = None) -> str:
    """Builds a prompt string with schema context (retained for backward compatibility)."""
    schema_context = build_schema_context(session_id=session_id)
    prompt = f"""
You are an expert Data Analyst & SQL Generator.

DATABASE SCHEMA AND TABLES:
{schema_context}

USER QUESTION:
{user_question}

Generate ONLY a valid read-only SELECT query.
"""
    return prompt


def generate_sql(
    user_question: str,
    history: Optional[List[Dict[str, Any]]] = None,
    session_id: Optional[str] = None,
    include_debug: bool = False
):
    """
    Main Text-to-SQL entry point.
    Executes LangChain + FAISS semantic retrieval pipeline.
    """
    sql, debug_info = generate_rag_sql(
        question=user_question,
        history=history,
        session_id=session_id,
        include_debug=include_debug
    )
    return sql