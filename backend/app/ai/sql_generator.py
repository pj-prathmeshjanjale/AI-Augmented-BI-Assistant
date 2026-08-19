from app.ai.schema_context import build_schema_context
from app.ai.groq_client import client


def build_sql_prompt(user_question, session_id: str = None):

    schema_context = build_schema_context(session_id=session_id)

    prompt = f"""
You are an expert Data Analyst & SQL Generator.

Your job is to convert a user's natural language question into a correct SQL SELECT query.

DATABASE SCHEMA AND TABLES:
{schema_context}

USER QUESTION:
{user_question}

RULES:
1. Generate ONLY a valid SELECT query.
2. Use ONLY tables and columns that exist in the provided schema above.
3. If table 'uploaded_data' is present in the schema, query from 'uploaded_data'.
4. Do not invent non-existent table or column names.
5. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or modifying statements.
6. For monthly/date grouping, use DATE_FORMAT(date_column, '%Y-%m') for MySQL or strftime('%Y-%m', date_column) for SQLite. NEVER use PostgreSQL functions like DATE_TRUNC.
7. Return ONLY the raw SQL query with no explanations or markdown tags.
"""

    return prompt


def generate_sql(user_question, history=None, session_id: str = None):

    prompt = build_sql_prompt(user_question, session_id=session_id)

    model_name = "groq/compound"
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Data Analyst. You generate safe and correct SQL SELECT queries for analytics. Return ONLY raw SQL query."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )
    except Exception as e:
        print("Groq API Primary Model Error, using fallback:", e)
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "system",
                    "content": "You generate safe and correct SQL SELECT queries for analytics. Return ONLY raw SQL query."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

    sql = response.choices[0].message.content.strip()

    # Remove Markdown code fences if returned
    if sql.startswith("```sql"):
        sql = sql[6:]
    elif sql.startswith("```SQL"):
        sql = sql[6:]
    elif sql.startswith("```"):
        sql = sql[3:]

    if sql.endswith("```"):
        sql = sql[:-3]

    sql = sql.strip()

    return sql