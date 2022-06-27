# Build-in modules
import logging

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
Create Flask object, Database connector and basic routes.
"""
application = CreateApp()
app = application.app
auth = application.auth
mongoDB = application.mongo


@auth.verify_password
def verify_password(email, password):
    # Make sure the connection is secure
    if request.is_secure:
        # Fetch the User ID
        query_resp = list(mongoDB.db.users_info.find({'userEmail': email}, {'password', '_id', 'userShelfId'}))

        # TODO Crypt the data on database
        # TODO Register the login time

        # Confirm the passed email exists
        if len(query_resp):
            user_id = str(query_resp[0]['_id'])
            user_password = query_resp[0]['password']
            user_shelf_id = query_resp[0]['userShelfId']
            # Check the password
            if password == user_password:
                # Return the user ID and its shelf ID
                return user_id, user_shelf_id


# ----------------------------------------------------------------------------------------------------------------------
# Basic routes

@app.route('/', methods=['GET'])
def index():
    """Application is alive"""
    message = {"Agnes. Your reading companion!"}
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


# ----------------------------------------------------------------------------------------------------------------------
# New user steps

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
        ret, code = UnknownUser().validate_email(user_email, mongoDB)

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
        ret, code = UnknownUser().validate_code(user_code, user_email, mongoDB)

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
        user_password = request.values.get('password')
        user_email = request.values.get('email')
        ret, code = UnknownUser().create_user(user_password, user_email, mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


# ----------------------------------------------------------------------------------------------------------------------


@app.route('/user/shelf/add_new_book', methods=['POST'])
@auth.login_required
def user_add_new_book():
    """
    Add a new book to a given user shelf.
    """
    # Default answer and Not implemented error.
    code = 501
    ret = []

    # Fetch the User Shelf ID from the login data
    _, user_shelf_id = auth.current_user()

    try:
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


@app.route('/user/shelf/books', methods=['GET'])
@auth.login_required
def user_shelf():
    """
    Fetch the user Books parsing the incoming condition.
    """
    # Default answer and Not implemented error.
    code = 501
    ret = []

    # Fetch the User Shelf ID from the login data
    _, shelf_id = auth.current_user()

    try:
        # Fetch the User Books as the given parameters
        book_status = request.values.get('bookStatus')
        ret, code = UserShelf().books(shelf_id, book_status, mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


@app.route('/user/shelf/update_book_status', methods=['POST'])
@auth.login_required
def update_book_status():
    """
    Update a book status on user Shelf.
    """
    # Default answer and Not implemented error.
    code = 501
    ret = []

    # Fetch the User Shelf ID from the login data
    _, user_shelf_id = auth.current_user()

    try:
        book_status = request.values.get('bookStatus')
        target_book_id = request.values.get('targetBookId')
        ret, code = UserShelf().update_book_status(user_shelf_id, target_book_id, book_status, mongoDB)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        # Message to the user
        resp = jsonify(ret)
        # Sending the response
        resp.status_code = code
        # Returning the object
        return resp


# ----------------------------------------------------------------------------------------------------------------------


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

# ----------------------------------------------------------------------------------------------------------------------
