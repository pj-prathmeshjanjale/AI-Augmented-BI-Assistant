# ==========================================
# CHART GENERATOR
# ==========================================

from decimal import Decimal

def generate_chart_data(results):
    """
    Convert SQL query results into chart data.
    """
    if not results or not isinstance(results, list) or len(results) < 2:
        return None

    first_row = results[0]
    if not isinstance(first_row, dict):
        return None

    columns = list(first_row.keys())
    if len(columns) < 2:
        return None

    label_column = columns[0]
    value_column = None

    for column in columns[1:]:
        value = first_row.get(column)
        try:
            val_num = float(value)
            value_column = column
            break
        except (ValueError, TypeError):
            continue

    if value_column is None:
        return None

    labels = []
    values = []

    for row in results:
        label = row.get(label_column)
        value = row.get(value_column)

        if label is None:
            continue

        try:
            numeric_val = float(value)
            labels.append(str(label))
            values.append(numeric_val)
        except (ValueError, TypeError):
            continue

    if len(labels) < 2:
        return None

    col_lower = label_column.lower()
    if "payment" in col_lower or "method" in col_lower:
        chart_type = "doughnut"
    elif "month" in col_lower or "date" in col_lower or "year" in col_lower:
        chart_type = "line"
    else:
        chart_type = "bar"

    return {
        "type": chart_type,
        "labels": labels,
        "values": values,
        "label": value_column,
        "datasetLabel": value_column.replace("_", " ").title()
    }