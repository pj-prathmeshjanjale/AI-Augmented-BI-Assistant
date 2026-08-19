from app.database.connection import get_connection
from app.database.schema_loader import get_database_schema
from app.ai.schema_context import build_schema_context
from app.ai.groq_client import client
from app.ai.sql_generator import generate_sql
from app.ai.sql_validator import validate_sql
from app.database.query_executor import execute_query
from app.ai.result_formatter import format_results
from app.ai.answer_generator import generate_business_answer


def test_all():

    print("\n========================================")
    print("       AI BI ASSISTANT FULL TEST")
    print("========================================\n")

    # 1. Database Connection
    print("[1/8] Testing database connection...")

    connection = get_connection()

    if connection:
        print("      ✅ Database connection successful")
        connection.close()
    else:
        raise Exception("Database connection failed")

    # 2. Schema Loader
    print("\n[2/8] Testing schema loader...")

    schema = get_database_schema()

    if schema:
        print("      ✅ Schema loaded successfully")
        print(f"      Tables found: {len(schema)}")
    else:
        raise Exception("Schema loading failed")

    # 3. Schema Context
    print("\n[3/8] Testing schema context...")

    schema_context = build_schema_context()

    if schema_context:
        print("      ✅ Schema context created")
    else:
        raise Exception("Schema context failed")

    # 4. Groq Connection
    print("\n[4/8] Testing Groq connection...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": "Reply with OK only."
            }
        ],
        temperature=0
    )

    groq_response = response.choices[0].message.content.strip()

    if groq_response:
        print("      ✅ Groq connection successful")
        print(f"      Response: {groq_response}")
    else:
        raise Exception("Groq connection failed")

    # 5. SQL Generation
    print("\n[5/8] Testing SQL generation...")

    question = "Which region generates the highest revenue?"

    sql = generate_sql(question)

    if sql:
        print("      ✅ SQL generated successfully")
        print("\n      Generated SQL:")
        print("      " + sql.replace("\n", "\n      "))
    else:
        raise Exception("SQL generation failed")

    # 6. SQL Validation
    print("\n[6/8] Testing SQL validator...")

    is_safe, message = validate_sql(sql)

    print(f"      Validation: {is_safe}")
    print(f"      Message: {message}")

    if not is_safe:
        raise Exception("Generated SQL failed safety validation")

    print("      ✅ SQL validation successful")

    # 7. Query Execution + Formatting
    print("\n[7/8] Testing query execution...")

    results = execute_query(sql)

    if results:
        print("      ✅ Query executed successfully")

        formatted_results = format_results(results)

        print("\n      Formatted Results:")
        for row in formatted_results:
            print(f"      {row}")
    else:
        raise Exception("Query returned no results")

    # 8. Business Answer
    print("\n[8/8] Testing business answer generation...")

    answer = generate_business_answer(
        question,
        formatted_results
    )

    if answer:
        print("      ✅ Business answer generated")

        print("\n      Business Answer:")
        print(f"      {answer}")
    else:
        raise Exception("Business answer generation failed")

    print("\n========================================")
    print("       🎉 ALL TESTS PASSED")
    print("========================================")
    print("\nYour AI BI Assistant backend is working correctly.")
    print("Ready to move to the FastAPI/UI stage.\n")


if __name__ == "__main__":
    test_all()