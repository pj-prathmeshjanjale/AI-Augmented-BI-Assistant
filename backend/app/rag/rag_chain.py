"""
LangChain RAG Chain for Text-to-SQL Generation.
Combines ChatPromptTemplate, semantic FAISS retrieval, multi-provider LLM, and StrOutputParser via LCEL.
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.rag.retriever import get_retriever
from app.ai.llm_provider import get_llm


SQL_RAG_SYSTEM_TEMPLATE = """You are an expert Data Analyst & SQL Generator in an enterprise Business Intelligence platform.

Your task is to convert a user's natural language question into a safe, syntactically correct SQL SELECT query based strictly on the retrieved schema definitions, join rules, and business KPIs provided below.

RELEVANT BUSINESS CONTEXT & SCHEMA (RETRIEVED VIA FAISS):
{retrieved_context}

RULES & CONSTRAINTS:
1. Generate ONLY a valid SELECT query.
2. Use ONLY tables and columns present in the provided schema context.
3. If table 'uploaded_data' or a specific CSV table is in the schema, query from that table.
4. For monthly or date grouping:
   - For MySQL: use DATE_FORMAT(date_column, '%Y-%m')
   - For SQLite: use strftime('%Y-%m', date_column)
   - NEVER use PostgreSQL functions like DATE_TRUNC.
5. Strictly DO NOT generate destructive or modifying queries (NO INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE).
6. Return ONLY the raw SQL query without explanations, markdown fences, or thinking tags.
"""


def build_rag_prompt_template() -> ChatPromptTemplate:
    """Creates a modern LangChain ChatPromptTemplate with dynamic context and history injection."""
    return ChatPromptTemplate.from_messages([
        ("system", SQL_RAG_SYSTEM_TEMPLATE),
        ("human", "CONVERSATION HISTORY:\n{history}\n\nUSER QUESTION: {question}")
    ])


def clean_sql_output(raw_sql: str) -> str:
    """Sanitizes LLM response, stripping reasoning tags, markdown fences, and formatting artifacts."""
    if not raw_sql or not isinstance(raw_sql, str):
        return ""

    sql = raw_sql.strip()

    # 1. Clean DeepSeek / Qwen reasoning <think> tags
    sql = re.sub(r'<think>.*?</think>', '', sql, flags=re.DOTALL).strip()
    if "<think>" in sql:
        sql = sql.split("<think>")[-1].split(">")[-1].strip()

    # 2. Strip Markdown code fences
    if sql.startswith("```sql"):
        sql = sql[6:]
    elif sql.startswith("```SQL"):
        sql = sql[6:]
    elif sql.startswith("```"):
        sql = sql[3:]

    if sql.endswith("```"):
        sql = sql[:-3]

    sql = sql.strip().rstrip(";")
    return sql


def get_rag_chain():
    """Builds and returns the LangChain LCEL RAG execution chain."""
    prompt = build_rag_prompt_template()
    llm = get_llm()
    parser = StrOutputParser()
    return prompt | llm | parser


def generate_rag_sql(
    question: str,
    history: Optional[List[Dict[str, Any]]] = None,
    session_id: Optional[str] = None,
    include_debug: bool = False
) -> Tuple[str, Dict[str, Any]]:
    """
    Executes the complete LangChain + FAISS RAG Text-to-SQL pipeline.
    Returns generated SQL query and observability/debug metadata.
    """
    start_total = time.perf_counter()

    # 1. Determine active dataset mode for session
    active_mode = "mysql"
    active_table = None
    try:
        from app.main import get_session_active_mode, get_session_active_table
        if session_id:
            active_mode = get_session_active_mode(session_id)
            active_table = get_session_active_table(session_id)
    except Exception:
        pass

    # 2. Semantic Context Retrieval via FAISS
    retriever = get_retriever()
    retrieved_context, retrieved_docs, retrieval_ms = retriever.get_rag_context(
        query=question,
        session_id=session_id,
        active_mode=active_mode,
        active_table=active_table
    )

    # 3. Format History
    history_str = "None"
    if history:
        history_str = "\n".join([
            f"Q: {h.get('question', '')} | SQL: {h.get('sql', '')}"
            for h in history if h.get("sql")
        ]) or "None"

    # 4. Invoke LangChain LCEL Chain
    chain = get_rag_chain()
    start_llm = time.perf_counter()

    try:
        raw_output = chain.invoke({
            "retrieved_context": retrieved_context,
            "history": history_str,
            "question": question
        })
    except Exception as chain_err:
        print(f"[WARN] Primary LangChain chain error ({chain_err}). Attempting fallback LLM invocation...")
        # Fallback to direct client invocation
        from app.ai.groq_client import client
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SQL_RAG_SYSTEM_TEMPLATE.format(retrieved_context=retrieved_context)},
                {"role": "user", "content": f"CONVERSATION HISTORY:\n{history_str}\n\nUSER QUESTION: {question}"}
            ],
            temperature=0
        )
        raw_output = response.choices[0].message.content

    llm_ms = (time.perf_counter() - start_llm) * 1000.0
    sql = clean_sql_output(raw_output)

    total_ms = (time.perf_counter() - start_total) * 1000.0

    debug_info = {
        "pipeline": "LangChain + FAISS RAG",
        "retrieval_time_ms": round(retrieval_ms, 2),
        "llm_time_ms": round(llm_ms, 2),
        "total_time_ms": round(total_ms, 2),
        "retrieved_doc_count": len(retrieved_docs),
        "retrieved_docs": retrieved_docs if include_debug else [d["doc_id"] for d in retrieved_docs]
    }

    return sql, debug_info
