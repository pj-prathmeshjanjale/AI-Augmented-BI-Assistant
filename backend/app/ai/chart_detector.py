# ==========================================
# CHART DETECTOR
# ==========================================

def should_generate_chart(question: str) -> bool:
    """
    Determines if a question benefits from a visual chart.
    """
    question = question.lower().strip()

    # Single entity questions that don't need charts
    single_value_phrases = ["what is the total revenue", "how many customers", "count of orders"]
    for phrase in single_value_phrases:
        if question == phrase:
            return False

    return True