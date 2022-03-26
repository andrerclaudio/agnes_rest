"""

All methods related to the dollar API.

"""

from flask import jsonify


def dollar_currency():
    """Welcome message for the API."""
    # Message to the user
    message = {
        'dollar': '1.00',
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp
