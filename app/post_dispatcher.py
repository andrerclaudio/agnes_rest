"""
Dispatcher all ingoing posts.
"""

# Build-in modules

# Installed modules
from flask import jsonify, request

# Local modules
from app.posts.add_new_reading import post_add_new_reading


def post_dispatcher():
    """
    Retrieve an information given some parameters.
    /post
    """

    # Parse the query type
    values = {}
    for argument, function in request.args.items():
        values[argument] = function

    if values['function'] == 'addNewReading':
        isbn = values['isbnCode']
        ret = post_add_new_reading(isbn)

        # Message to the user
        resp = jsonify(ret)
        # Sending OK response
        resp.status_code = 201
        # Returning the object
        return resp
