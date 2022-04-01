"""
This module will encode and parse the query string params.
"""


def fetch_query_params(request):
    """
    Function to parse the query parameter string.
    """
    values = {}
    # Fetch the query param string
    for k, v in request.args.items():
        values[k] = v

    return values
