# Build-in modules
import logging

from bson.objectid import ObjectId
# Installed modules
from flask import jsonify, request

# Local modules
from app.Book.book_information import RetrieveBookInformation
from app.User.unknown_user import UnknownUser
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


@auth.verify_password
def verify_password(email, password):
    # Fetch the specif Shelf ID
    query_resp = list(mongoDB.db.users_info.find({'userEmail': email}, {'password', '_id'}))
    stored_user_id = str(query_resp[0]['_id'])
    stored_user_pass = query_resp[0]['password']

    # TODO Crypt the data on rest
    # TODO Hash the password before sending
    # TODO Register the login time

    if len(query_resp):
        # The user exist
        if password == stored_user_pass:
            # the password is correct and the ID is returned
            return stored_user_id


@app.route('/', methods=['GET'])
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


@app.route('/unknown/validate_email', methods=['POST'])
def unknown_user_validate_email():
    """
    Receive the email from a new possibly user.
    """
    # Default answer and Not implemented error.
    code = 501
    ret = []

    try:
        user_email = request.values.get('email')
        unknown = UnknownUser()
        ret, code = unknown.validate_email(email=user_email, mongo=mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


@app.route('/unknown/validate_code', methods=['GET'])
def unknown_user_validate_code():
    """
    Validate the verification code sent to the proposal email.
    """
    # Default answer and Not implemented error.
    code = 501
    ret = []

    try:
        user_code = request.values.get('code')
        user_email = request.values.get('email')
        unknown = UnknownUser()
        ret, code = unknown.validate_code(verif_code=user_code, email=user_email, mongo=mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


@app.route('/unknown/create_user', methods=['POST'])
def unknown_user_create_user():
    """
    Create the new user.
    """
    # Default answer and Not implemented error.
    code = 501
    ret = []

    try:
        # data = request.get_json()
        # user_email = request.values.get('email')
        user_password = request.values.get('password')
        user_email = request.values.get('email')
        unknown = UnknownUser()
        ret, code = unknown.create_user(password=user_password, email=user_email, mongo=mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


@app.route('/user/shelf/add_new_book', methods=['POST'])
@auth.login_required
def user_add_new_books():
    """
    Add a new book to a given user shelf.
    """
    # Default answer and Not implemented error.
    code = 501
    ret = []

    # Fetch the UserId from the login data
    user_id = auth.current_user()

    try:
        # Fetch the specif Shelf ID
        query_resp = list(mongoDB.db.users_info.find({'_id': ObjectId(user_id)}, {'userShelfId'}))
        # Make sure the given use has a shelf
        if len(query_resp):
            # Identify the user shelf
            user_shelf_id = query_resp[0]['userShelfId']
            isbn_code = request.values.get('isbnCode')
            ret, code = UserShelf().add_new_book(user_shelf_id, isbn=isbn_code, mongo=mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


@app.route('/user/shelf/current_readings', methods=['GET'])
@auth.login_required
def user_current_readings():
    """
    Fetch the current reading from a given user.
    """
    # Default answer and Not implemented error.
    code = 501
    ret = []

    # Fetch the UserId from the login data
    user_id = auth.current_user()

    try:
        # Fetch the specif Shelf ID
        query_resp = list(mongoDB.db.users_info.find({'_id': ObjectId(user_id)}, {'userShelfId'}))
        # Make sure the given use has a shelf
        if len(query_resp):
            # Identify the user shelf
            user_shelf_id = query_resp[0]['userShelfId']
            # Fetch the User current readings
            ret, code = UserShelf().current_readings(user_shelf_id, mongo=mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


@app.route('/library/fetch_book_information', methods=['GET'])
@auth.login_required
def library_fetch_book_information():
    """
    Fetch some book information based on ISBN code.
    """
    # Default answer and Not implemented error.
    code = 501
    ret = []

    try:
        isbn_code = request.values.get('isbnCode')
        # Fetch the info about a book given an ISBN code
        ret, code = RetrieveBookInformation().on_local_library(isbn=isbn_code, mongo=mongoDB)
        if code == 200:
            if ret[0]['errorCode'] == ValidationCodes.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE:
                # In fails on local Library, go to internet
                ret, code = RetrieveBookInformation().on_internet(isbn=isbn_code, mongo=mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp
