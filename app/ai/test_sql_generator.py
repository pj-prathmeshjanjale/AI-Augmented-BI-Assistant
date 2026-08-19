from app.ai.sql_generator import generate_sql


question = "Which category has the highest revenue?"

sql = generate_sql(question)

print("\nGenerated SQL:\n")
print(sql)