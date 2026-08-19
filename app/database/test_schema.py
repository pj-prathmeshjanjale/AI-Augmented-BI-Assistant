from schema_loader import get_database_schema


schema = get_database_schema()

for table, columns in schema.items():
    print(f"\nTable: {table}")

    for column in columns:
        print(f"  {column['column']} ({column['type']})")