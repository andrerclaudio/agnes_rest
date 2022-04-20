"""
Dispatcher all ingoing Posts.
"""

# Build-in modules
import logging

# Installed modules
from flask import jsonify, request

# Local modules
from app.Posts.add_new_reading import post_add_new_reading

# Printing object
logger = logging.getLogger(__name__)


def post_dispatcher():
    """
    Retrieve an information given some parameters.
    /post
    """

    # Default answer and Not implemented error.
    code = 501
    ret = []

    try:
        # Parse the query type
        values = {}
        for argument, function in request.args.items():
            values[argument] = function

        if values['function'] == 'addNewReading':
            isbn = values['isbnCode']
            ret, code = post_add_new_reading(isbn)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp
