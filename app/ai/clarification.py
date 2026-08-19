# ==========================================
# SMART CLARIFICATION SUGGESTIONS
# ==========================================

def get_clarification(question: str):
    """
    Returns clarification suggestions ONLY if the user question is a single
    vague/ambiguous word (e.g. 'top', 'average', 'highest').
    If the question contains specific attributes, metrics, or entities,
    clarification is skipped so text-to-SQL can execute directly.
    """
    cleaned = question.lower().strip()
    words = cleaned.split()

    # If the user provided a multi-word question (e.g., "average weight by sport", "top five teams")
    # then the question is specific enough - do not block it with clarification!
    if len(words) > 2:
        return None

    # Ambiguous single-word or 2-word queries
    if cleaned in ["highest", "top", "best"]:
        return {
            "message": "What metric or entity would you like to find the highest for?",
            "suggestions": [
                "Top 5 teams by medal",
                "Highest revenue by category",
                "Top 5 products by sales"
            ]
        }

    if cleaned in ["lowest", "least"]:
        return {
            "message": "What metric or entity would you like to find the lowest for?",
            "suggestions": [
                "Lowest revenue by category",
                "Lowest selling product"
            ]
        }

    if cleaned in ["average", "avg"]:
        return {
            "message": "What metric would you like to calculate the average of?",
            "suggestions": [
                "Average weight by sport",
                "Average height by sport",
                "Average order value"
            ]
        }

    if cleaned in ["total", "show me the total", "what is the total"]:
        return {
            "message": "What metric would you like to calculate the total of?",
            "suggestions": [
                "Total revenue",
                "Total medal by team",
                "Total orders"
            ]
        }

    return None