# ==========================================
# DUAL-MODE INTENT ROUTER ENGINE
# ==========================================

from app.ai.groq_client import client


def classify_intent_and_answer(question: str) -> tuple[str, str | None]:
    """
    Classifies user question into:
    1. 'conversational': General chat, greetings, programming, general knowledge.
       - Answered directly by Groq AI without database execution.
    2. 'data_query': Structured data questions requiring Text-to-SQL execution.

    Returns tuple: (intent_type, general_ai_answer)
    """
    q_lower = question.lower().strip()

    # 1. Immediate match for standard greetings
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "namaste", "who are you", "what is your name", "help"]
    if q_lower in greetings:
        return "conversational", (
            "Hello! 👋 I am your Enterprise AI Business Intelligence Assistant powered by Groq AI.\n\n"
            "• Ask me general questions or chat naturally.\n"
            "• Ask business data questions about your active dataset (e.g. sales, orders, revenue, products, customers, or uploaded CSV metrics)!"
        )

    # 2. Keyword override for business & data analytics questions
    data_keywords = [
        "product", "products", "sale", "sales", "revenue", "order", "orders", 
        "customer", "customers", "employee", "employees", "region", "regions", 
        "trend", "monthly", "total", "top", "average", "count", "medal", "medals", 
        "sport", "sports", "gdp", "country", "team", "price", "unit", "sum", "min", "max"
    ]
    if any(k in q_lower for k in data_keywords):
        return "data_query", None

    # 2. Fast LLM Classification Prompt
    prompt = f"""
Classify the user's input into exactly one category:

CATEGORIES:
- CONVERSATIONAL: General greetings, casual small talk, programming questions, general knowledge, jokes, or non-data questions (e.g. "hello", "how to write a python loop", "who is the president", "explain gravity", "what is AI").
- DATA_QUERY: Questions asking for business metrics, sales, products, customers, counts, totals, averages, rankings, trends, sports medals, or structured data analysis against a database/dataset.

USER INPUT: "{question}"

REPLY WITH EXACTLY ONE WORD: CONVERSATIONAL or DATA_QUERY.
"""

    try:
        response = client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        intent = response.choices[0].message.content.strip().upper()

        if "CONVERSATIONAL" in intent:
            # Generate intelligent general AI answer from Groq
            gen_response = client.chat.completions.create(
                model="groq/compound",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful, intelligent AI Assistant & Business Intelligence Expert. Answer the user's question clearly, politely, and directly."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.7
            )
            ai_text = gen_response.choices[0].message.content.strip()
            return "conversational", ai_text

    except Exception as e:
        print("Intent Router Exception:", e)

    # Default to data_query
    return "data_query", None
