import re


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "GRANT",
    "REVOKE",
]


def validate_sql(sql):

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    # Remove markdown code fences if the LLM returned them
    sql = sql.strip()

    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)

    sql = sql.strip()

    # Query must start with SELECT or WITH
    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
        return False, "Only SELECT or WITH queries are allowed."

    # Check for dangerous SQL commands
    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{keyword}\b"

        if re.search(pattern, sql, re.IGNORECASE):
            return False, f"Forbidden SQL keyword detected: {keyword}"

    return True, "SQL query is safe."