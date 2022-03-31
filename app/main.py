# Build-in modules
import configparser
import logging
from functools import wraps

import jwt
# Installed modules
# from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

# Local modules
from app.queries import query_currency as currency

# import app.schedulers as schedulers
# from app.constants import currency_info

# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read_file(open('config.ini'))

AGNES_KEY = config['AGNES_KEY']['key']
AGNES_SECRET = config['AGNES_SECRET']['secret']

"""
Add a scheduler to the operation
"""
# sched = BackgroundScheduler(daemon=True)
# sched.add_job(schedulers.get_currency, 'interval', seconds=currency_info.ALPHA_VANTAGE_REQUEST_CURRENCY_TIMEOUT)
# sched.start()

# Place where app is defined
app = Flask(__name__)
# Basic Authentication
auth = HTTPBasicAuth()

# External methods
app.add_url_rule('/currency', methods=['GET'], view_func=currency.dollar_currency)

users = {
    "john": generate_password_hash("hello"),
    "susan": generate_password_hash("bye")
}


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        query = request.args
        token = query.get('token')

        try:
            payload = jwt.decode(token, AGNES_SECRET, algorithms=['HS256'])
            key = payload['key']
            if not token or AGNES_KEY != key:
                message = {'message': 'The provided API key is not valid'}
                # Making the message looks good
                resp = jsonify(message)
                # Sending OK response
                resp.status_code = 404

                return resp
            return f(*args, **kwargs)

        except Exception as e:
            logging.exception(e, exc_info=False)

            message = {'message': 'Please provide an API key'}
            # Making the message looks good
            resp = jsonify(message)
            # Sending OK response
            resp.status_code = 500

            return resp, 500

    return decorated


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@app.route('/', methods=['GET', 'POST'])
@token_required
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


@app.route('/auth', methods=['GET', 'POST'])
@auth.login_required
@token_required
def auth_handler():
    """Welcome message for the API."""

    # Message to the user
    message = {
        'User': '{}'.format(auth.current_user())
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
    logger.error(e)
    # Making the message looks good
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 404
    # Returning the object
    return resp
