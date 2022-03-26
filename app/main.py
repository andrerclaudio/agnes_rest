import logging
import os
from flask import Flask,request, jsonify
from flask_talisman import Talisman, ALLOW_FROM
from flask_seasurf import SeaSurf


# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


# Place where app is defined
app = Flask(__name__)
# app.secret_key = '123abc'
# csrf = SeaSurf(app)
# talisman = Talisman(app)

# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
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



# Example of a route-specific talisman configuration
# @app.route('/secure')
# @talisman()
# def embeddable():
#     return "<html>I can be secured!</html>"





@app.route("/api/v1/eval", methods=['GET'])
def fetch_users():
    """
    Function to fetch the users.
    """
    try:
        logger.debug(request.query_string)
        return jsonify([])

    except:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return "", 500