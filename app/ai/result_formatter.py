from decimal import Decimal


def format_results(results):

    if not results:
        return "No results found."

    output = []

    for row in results:

        formatted_row = {}

        for key, value in row.items():

            if isinstance(value, Decimal):
                value = float(value)

            formatted_row[key] = value

        output.append(formatted_row)

    return output