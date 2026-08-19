from app.ai.sql_generator import generate_sql
from app.ai.sql_validator import validate_sql
from app.database.query_executor import execute_query
from app.ai.result_formatter import format_results
from app.ai.answer_generator import generate_business_answer


print("\n======================================")
print("       AI BI ASSISTANT")
print("======================================")
print("Ask your business questions.")
print("Type 'exit' to stop.\n")


while True:

    # Get question from user
    question = input("Ask your business question: ")

    # Exit program
    if question.lower() == "exit":
        print("\nAI BI Assistant stopped.")
        break

    # Ignore empty questions
    if not question.strip():
        print("Please enter a question.\n")
        continue

    try:

        # STEP 1: Generate SQL using Groq
        sql = generate_sql(question)

        print("\nGenerated SQL:")
        print(sql)

        # STEP 2: Validate SQL
        is_safe, message = validate_sql(sql)

        print("\nValidation:")
        print(is_safe)
        print(message)

        # STEP 3: Execute only safe SQL
        if is_safe:

            results = execute_query(sql)

            print("\nQuery Results:")

            if results:

                # STEP 4: Format database results
                formatted_results = format_results(results)

                print("\nFormatted Results:")

                for row in formatted_results:
                    print(row)

                # STEP 5: Generate human-readable answer
                answer = generate_business_answer(
                    question,
                    formatted_results
                )

                print("\nBusiness Answer:")
                print(answer)

            else:
                print("No results found.")

        else:

            print("\nSQL execution blocked because the query is unsafe.")

    except Exception as e:

        print("\nError:")
        print(e)

    print("\n--------------------------------------\n")