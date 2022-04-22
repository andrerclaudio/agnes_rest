"""
Dispatcher all ingoing Posts and Queries.
"""

# Build-in modules
import logging

# Installed modules
from flask import jsonify, request

# Local modules
from app.user_shelf import UserShelf
from app.error_codes import ValidationCodes
from app.book_information import FetchBookInformation

# Printing object
logger = logging.getLogger(__name__)


def post_dispatcher():
    """
    Reply on posts requests.
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

        if values['function'] == 'addNewBook':
            user = UserShelf()
            ret, code = user.add_new_book(isbn=values['isbnCode'])

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


def query_dispatcher():
    """
    Reply on queries requests.
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
        if values['function'] == 'currentReadings':
            # Fetch the info about the current readings
            user = UserShelf()
            ret, code = user.current_readings()

        elif values['function'] == 'fetchBookInfo':
            # Fetch the info about a book given an ISBN code
            fetch = FetchBookInformation()
            ret, code = fetch.on_local_library(isbn=values['isbn'])
            if code == 200 and not ret[0]['successOnRequest'] and \
                    ret[0]['errorCode'] == ValidationCodes.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE:
                # In fails on local Library, go to internet
                ret, code = fetch.on_internet(isbn=values['isbn'])

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp
