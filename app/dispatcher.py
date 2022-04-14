"""
Dispatcher all ingoing queries.
"""

# Build-in modules

# Installed modules
from flask import jsonify, request

# Local modules
from .queries.fetch_book import query_fetch_book_info
from .queries.reading_screen import query_reading_screen


def query_dispatcher():
    """
    Retrieve an information given some parameters.
    /query
    """

    # Parse the query type
    values = {}
    for argument, function in request.args.items():
        values[argument] = function

    # Route the given query
    if values['function'] == 'readingScreen':
        ret = query_reading_screen()

        # Message to the user
        resp = jsonify(ret)
        # Sending OK response
        resp.status_code = 200
        # Returning the object
        return resp

    elif values['function'] == 'fetchBookInfo':

        isbn = values['isbn']
        ret = query_fetch_book_info(isbn)

        # Message to the user
        resp = jsonify(ret)
        # Sending OK response
        resp.status_code = 200
        # Returning the object
        return resp
