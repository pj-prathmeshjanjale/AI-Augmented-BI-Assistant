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

    # Fast heuristic checks for conversational queries
    conversational_starters = [
        "what is ai", "what is machine learning", "what is rag", "what is langchain", 
        "how does", "how to", "explain", "tell me about", "who is", "why is", "define",
        "write a python", "write code", "help me"
    ]
    if any(q_lower.startswith(s) or q_lower == s for s in conversational_starters):
        return _generate_executive_conversational_answer(question)

    # Fast LLM Classification Prompt
    prompt = f"""Classify the user's input into exactly one category:
- CONVERSATIONAL: General greetings, concepts, programming, definitions, general knowledge, or conversational chat (e.g. "what is AI", "how to optimize queries", "explain RAG", "who founded Google").
- DATA_QUERY: Questions asking for business metrics, sales, revenue, orders, customers, products, tables, columns, rankings, totals, or data analysis.

USER INPUT: "{question}"

REPLY WITH EXACTLY ONE WORD: CONVERSATIONAL or DATA_QUERY.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=20,
            timeout=8.0
        )
        raw_intent = response.choices[0].message.content
        import re
        clean_intent = re.sub(r'<think>.*?</think>', '', raw_intent, flags=re.DOTALL).strip().upper()

        if "CONVERSATIONAL" in clean_intent:
            return _generate_executive_conversational_answer(question)

    except Exception as e:
        print("[WARN] Intent Router Exception:", e)

    # Default to data_query
    return "data_query", None


def _generate_executive_conversational_answer(question: str) -> tuple[str, str]:
    """Generates a structured, concise executive AI response."""
    import re
    try:
        gen_response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an Executive AI Business Intelligence & Strategy Advisor. "
                        "When answering general or conceptual questions:\n"
                        "1. Start with a crisp, 1-2 sentence Executive Overview.\n"
                        "2. Present key insights, benefits, or mechanisms in 3-4 concise bullet points.\n"
                        "3. Keep the response executive-ready, polished, structured, and under 200 words without excessive filler."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.3
        )
        ai_text = gen_response.choices[0].message.content
        ai_text = re.sub(r'<think>.*?</think>', '', ai_text, flags=re.DOTALL).strip()
        return "conversational", ai_text
    except Exception as err:
        print("[WARN] Conversational generation error:", err)
        return "conversational", f"I am your AI BI Assistant. Please ask a business question about orders, revenue, products, customers, or uploaded datasets!"
