# ==========================================
# SMART CLARIFICATION & EXECUTIVE GUIDANCE
# ==========================================

def get_clarification(question: str):
    """
    Returns structured executive clarification and clickable suggestions
    if the user query is a single ambiguous word or short phrase (e.g. 'compare', 'top', 'average').
    """
    cleaned = question.lower().strip().replace("?", "").replace("!", "")
    words = cleaned.split()

    # If the user provided a specific multi-word query (e.g., "compare North and South region"), proceed to SQL
    if len(words) > 2 and not any(phrase == cleaned for phrase in ["compare last 2 months", "show me summary"]):
        return None

    # 1. Comparative queries ("compare", "vs", "versus", "difference")
    if cleaned in ["compare", "comparison", "vs", "versus", "difference", "compare between"]:
        return {
            "message": (
                "### 📊 Comparative Analysis Request\n\n"
                "To perform a comparative business intelligence breakdown, please specify the dimensions, regions, categories, or time periods to compare.\n\n"
                "**Recommended Comparative Inquiries:**\n"
                "- **Regional Analysis**: *Compare revenue between North and South region*\n"
                "- **Category Performance**: *Compare revenue between top 2 categories*\n"
                "- **Period-over-Period**: *Compare last 2 month revenue*\n"
                "- **Product Volume**: *Compare unit sales between top 5 products*"
            ),
            "suggestions": [
                "Compare revenue between North and South region",
                "Compare revenue between top 2 categories",
                "Compare last 2 month revenue"
            ]
        }

    # 2. Ranking queries ("highest", "top", "best")
    if cleaned in ["highest", "top", "best", "leaders", "most"]:
        return {
            "message": (
                "### 🏆 Top-N Ranking Request\n\n"
                "Please specify which metric or business dimension you would like to rank.\n\n"
                "- **By Revenue**: *Top 5 customers with highest total order spending*\n"
                "- **By Volume**: *Which product category has the highest unit sales?*\n"
                "- **By Territory**: *Which region generated the highest revenue?*"
            ),
            "suggestions": [
                "Top 5 customers with highest total order spending",
                "Which product category has the highest revenue?",
                "Which region generated the highest revenue?"
            ]
        }

    # 3. Lowest queries ("lowest", "least", "bottom")
    if cleaned in ["lowest", "least", "bottom", "worst"]:
        return {
            "message": (
                "### 📉 Bottom-N Analysis Request\n\n"
                "Please specify which dimension to analyze for lowest volume or revenue.\n\n"
                "- **By Category**: *Which product category has the lowest revenue?*\n"
                "- **By Stock**: *Show products with lowest stock quantities*\n"
                "- **By Territory**: *Which region generated the lowest sales?*"
            ),
            "suggestions": [
                "Which product category has the lowest revenue?",
                "Show products with lowest stock quantity",
                "Which region generated the lowest revenue?"
            ]
        }

    # 4. Average queries ("average", "avg", "mean")
    if cleaned in ["average", "avg", "mean"]:
        return {
            "message": (
                "### 📐 Average Metric Request\n\n"
                "Which key performance indicator would you like to compute an average for?\n\n"
                "- **Order Value**: *What is the average order value (AOV)?*\n"
                "- **Customer Spend**: *What is the average spending per customer?*\n"
                "- **Product Price**: *What is the average unit price across categories?*"
            ),
            "suggestions": [
                "What is the average order value (AOV)?",
                "What is the average spending per customer?",
                "What is the average product unit price?"
            ]
        }

    # 5. Total queries ("total", "sum", "overall")
    if cleaned in ["total", "sum", "overall", "all"]:
        return {
            "message": (
                "### 📈 Aggregate Metric Request\n\n"
                "Which business metric would you like to aggregate?\n\n"
                "- **Gross Revenue**: *What is the total revenue across all orders?*\n"
                "- **Order Volume**: *What is the total number of orders placed?*\n"
                "- **Active Customers**: *What is the total number of registered customers?*"
            ),
            "suggestions": [
                "What is the total revenue across all orders?",
                "What is the total number of orders placed?",
                "What is the total customer count?"
            ]
        }

    # 6. Summary & Overview queries ("summary", "overview", "dashboard", "kpi", "metrics")
    if cleaned in ["summary", "overview", "dashboard", "kpi", "kpis", "metrics", "status"]:
        return {
            "message": (
                "### 📋 Executive Business Summary\n\n"
                "Select a high-level KPI dashboard inquiry to explore the active dataset:\n\n"
                "- **Sales Overview**: *What is the total revenue across all orders?*\n"
                "- **Recent Momentum**: *what is the calculations of previous month*\n"
                "- **Geographic Distribution**: *Which region generated the highest revenue?*"
            ),
            "suggestions": [
                "What is the total revenue across all orders?",
                "what is the calculations of previous month",
                "Which region generated the highest revenue?"
            ]
        }

    return None