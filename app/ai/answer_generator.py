from app.ai.groq_client import client


def generate_business_answer(question, results):

    if not results or results == "No results found.":
        return "No relevant data found in the dataset for this question. Please try refining your question or filtering criteria."

    prompt = f"""
You are an Executive Business Intelligence Analyst.

Your job is to provide a clean, professional executive summary based ONLY on the data results provided below.

USER QUESTION:
{question}

DATA RESULTS:
{results}

FORMAT RULES:
1. Write a professional 1-2 sentence executive overview answering the question directly.
2. If there are key rankings or comparisons in the results, present them in 3-5 clean bullet points using markdown (- item).
3. Use formatted numbers (e.g. 15,000 or $1,250,000) where appropriate.
4. Do NOT mention SQL, code, databases, Python, Groq, or technical mechanics.
5. Keep the language corporate, executive-ready, polished, and direct.
"""

    model_name = "openai/gpt-oss-20b"
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an Executive Business Intelligence Analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )
    except Exception as e:
        print("Groq API Answer Model Error, using fallback:", e)
        response = client.chat.completions.create(
            model="groq/compound",
            messages=[
                {
                    "role": "system",
                    "content": "You are an Executive Business Intelligence Analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

    return response.choices[0].message.content.strip()