"""
Dispatcher all ingoing Queries.
"""

# Build-in modules
import logging

# Installed modules
from flask import jsonify, request

# Local modules
from .Queries.fetch_book_locally import query_fetch_book_info
from .Queries.reading_screen import query_reading_screen

# Printing object
logger = logging.getLogger(__name__)


def query_dispatcher():
    """
    Retrieve an information given some parameters.
    /query
    """

    # Default answer and Not implemented error.
    code = 501
    ret = []

    try:
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

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp
