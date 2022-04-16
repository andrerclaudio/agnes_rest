"""
Dispatcher all ingoing queries.
"""

# Build-in modules

# Installed modules
from flask import jsonify, request

# Local modules
from .queries.fetch_book_locally import query_fetch_book_info
from .queries.reading_screen import query_reading_screen


def query_dispatcher():
    """
    Retrieve an information given some parameters.
    /query
    """

    # Default answer and Not implemented error.
    code = 501
    ret = []

    # Parse the query type
    values = {}
    for argument, function in request.args.items():
        values[argument] = function

    # Route the given query
    if values['function'] == 'readingScreen':
        # Fetch the info about the readings that are happening
        ret, code = query_reading_screen()

    elif values['function'] == 'fetchBookInfo':
        # Fetch the info about one book given an ISBN code
        isbn = values['isbn']
        ret, code = query_fetch_book_info(isbn)

    # Message to the user
    resp = jsonify(ret)
    # Sending the response
    resp.status_code = code
    # Returning the object
    return resp
