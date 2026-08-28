import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.schema_loader import get_database_schema
from app.ai.schema_context import build_schema_context
from app.ai.groq_client import client
from app.ai.sql_generator import generate_sql
from app.ai.sql_validator import validate_sql
from app.main import smart_execute_query
from app.ai.result_formatter import format_results
from app.ai.answer_generator import generate_business_answer
from app.rag.rag_chain import generate_rag_sql


def test_all():

    print("\n========================================")
    print("       AI BI ASSISTANT FULL TEST")
    print("========================================\n")

    # 1. Database Connection & Execution Engine
    print("[1/8] Testing database connection & execution engine...")
    try:
        results = smart_execute_query("SELECT 1 AS status")
        if results:
            print("      [PASSED] Database execution engine operational.")
        else:
            raise Exception("Execution engine returned empty.")
    except Exception as e:
        raise Exception(f"Database connection failed: {e}")

    # 2. Schema Loader
    print("\n[2/8] Testing schema loader...")
    schema = get_database_schema()
    if schema:
        print("      [PASSED] Schema loaded successfully.")
        print(f"      Tables found: {len(schema)}")
    else:
        raise Exception("Schema loading failed")

    # 3. Schema Context
    print("\n[3/8] Testing schema context...")
    schema_context = build_schema_context()
    if schema_context:
        print("      [PASSED] Schema context created.")
    else:
        raise Exception("Schema context failed")

    # 4. Groq Connection
    print("\n[4/8] Testing Groq connection...")
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "Reply with OK only."}],
        temperature=0
    )
    groq_response = response.choices[0].message.content.strip()
    if groq_response:
        print(f"      [PASSED] Groq connection successful (Response: {groq_response[:20]}).")
    else:
        raise Exception("Groq connection failed")

    # 5. LangChain + FAISS RAG SQL Generation
    print("\n[5/8] Testing LangChain + FAISS RAG SQL generation...")
    question = "Which region generates the highest revenue?"
    sql, debug_info = generate_rag_sql(question, include_debug=True)

    if sql:
        print("      [PASSED] SQL generated successfully via LangChain + FAISS.")
        print(f"      Retrieved Chunks: {debug_info.get('retrieved_docs', [])}")
        print("      Generated SQL:")
        print("      " + sql.replace("\n", "\n      "))
    else:
        raise Exception("SQL generation failed")

    # 6. SQL Validation & Guardrails
    print("\n[6/8] Testing SQL validator & guardrails...")
    is_safe, message = validate_sql(sql)
    print(f"      Validation: {is_safe} | Message: {message}")

    if not is_safe:
        raise Exception("Generated SQL failed safety validation")
    print("      [PASSED] SQL validation successful.")

    # 7. Query Execution + Formatting
    print("\n[7/8] Testing query execution & result formatting...")
    results = smart_execute_query(sql)

    if results and isinstance(results, list):
        print(f"      [PASSED] Query executed successfully ({len(results)} rows returned).")
        formatted_results = format_results(results)
        print("      Formatted Results:")
        for row in formatted_results[:3]:
            print(f"      {row}")
    else:
        raise Exception("Query returned no results")

    # 8. Business Answer Generation
    print("\n[8/8] Testing executive business answer generation...")
    answer = generate_business_answer(question, formatted_results)

    if answer:
        print("      [PASSED] Executive answer generated.")
        print("\n      Executive Answer:")
        print(f"      {answer}")
    else:
        raise Exception("Business answer generation failed")

    print("\n========================================")
    print("       ALL PIPELINE TESTS PASSED!")
    print("========================================\n")


if __name__ == "__main__":
    test_all()