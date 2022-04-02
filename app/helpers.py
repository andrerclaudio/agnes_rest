"""
This module will encode and parse the query string params.
"""


def fetch_token(request):
    """
    Function to parse the query parameter string.
    """

    # Return the raw token string
    values = {}
    for k, v in request.args.items():
        values[k] = v

    return values['token']
