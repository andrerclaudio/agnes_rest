from flask import Flask
from distutils.log import debug
import logging
from flask import request, jsonify
from importlib.machinery import SourceFileLoader

# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


# Place where app is defined
app = Flask(__name__)


# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


# Import the helpers module
helper_module = SourceFileLoader('*', './app/helpers.py').load_module()

@app.route("/")
def get_initial_response():
    """Welcome message for the API."""
    # Message to the user
    message = {
        'apiVersion': 'v1.0',
        'status': '200',
        'message': 'Welcome to the Agnes API'
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp


@app.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    # Message to the user
    message = {
        "err":
            {
                "msg": "This route is currently not supported. Please refer API documentation."
            }
    }
    # Making the message looks good
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 404
    # Returning the object
    return resp


@app.route("/api/v1/eval", methods=['GET'])
def fetch_users():
    """
    Function to fetch the users.
    """
    try:

        logger.debug(request.query_string)

        # Call the function to get the query params
        query_params = helper_module.parse_query_params(request.query_string)
        # Check if dictionary is not empty
        if query_params:
            return jsonify({'andre': 'ribeiro'})
        else:
            return jsonify([])

    except:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return "", 500