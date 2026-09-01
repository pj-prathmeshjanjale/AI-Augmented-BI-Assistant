from decimal import Decimal
from typing import Any, List, Dict


def format_results(results: Any) -> List[Dict[str, Any]]:
    """Safely formats database query result rows into JSON-serializable dictionaries."""
    if not results or results == "No results found." or not isinstance(results, list):
        return []

    output = []
    for row in results:
        if not isinstance(row, dict):
            continue

        formatted_row = {}
        for key, value in row.items():
            if isinstance(value, Decimal):
                value = float(value)
            formatted_row[key] = value

        output.append(formatted_row)

    return output