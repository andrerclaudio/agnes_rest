# Build-in modules
import logging

# Installed modules
from flask import jsonify, request

from app.Book.book_information import RetrieveBookInformation
# Local modules
from app.Tools.auth import authorization
from app.User.user_shelf import UserShelf
from app.connectors import CreateApp
from app.error_codes import ValidationCodes

# Print in software terminal
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)

"""
Create Flask object, related Queries and basic routes.
"""
application = CreateApp()
app = application.app
auth = application.auth
mongoDB = application.mongo


@app.route('/', methods=['GET'])
@authorization
def index():
    """Application is alive"""
    # This route is used when the incoming user is not registered yet.
    message = {
        "welcome":
            {
                "msg": "Agnes. Your reading companion!"
            }
    }
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 200
    # Returning the object
    return resp


@app.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    # Message to the user
    message = {
        "err":
            {
                "msg": "This route is currently not supported."
            }
    }
    logger.error(e)
    # Making the message looks good
    resp = jsonify(message)
    # Sending ERROR response
    resp.status_code = 404
    # Returning the object
    return resp


@app.route('/post', methods=['POST'])
@authorization
def post_dispatcher():
    """
    Reply on Post requests.
    /post
    """

    # Default answer and Not implemented error.
    code = 501
    ret = []

    try:
        # Parse the Post type
        values = {}
        for argument, function in request.args.items():
            values[argument] = function

        # Route the given Post
        if values['function'] == 'addNewBook':
            user = UserShelf()
            ret, code = user.add_new_book(isbn=values['isbnCode'], mongo=mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


@app.route('/query', methods=['GET'])
@authorization
def query_dispatcher():
    """
    Reply on Query requests.
    /query
    """

    # Default answer and Not implemented error.
    code = 501
    ret = []

    try:
        # Parse the Query type
        values = {}
        for argument, function in request.args.items():
            values[argument] = function

        # Route the given query
        if values['function'] == 'currentReadings':
            # Fetch the User current readings
            user = UserShelf()
            ret, code = user.current_readings(mongo=mongoDB)

        elif values['function'] == 'fetchBookInfo':
            # Fetch the info about a book given an ISBN code
            ret, code = RetrieveBookInformation().on_local_library(isbn=values['isbn'], mongo=mongoDB)
            if code == 200 and not ret[0]['successOnRequest'] and \
                    ret[0]['errorCode'] == ValidationCodes.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE:
                # In fails on local Library, go to internet
                ret, code = RetrieveBookInformation().on_internet(isbn=values['isbn'], mongo=mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp
