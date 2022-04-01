# Build-in modules
import configparser
import logging
import os
from functools import wraps

# Installed modules
import jwt
from flask import jsonify, request
# from flask_login import login_required
from flask_httpauth import HTTPBasicAuth
from jwt import InvalidTokenError
from werkzeug.security import generate_password_hash, check_password_hash

# Local modules
from app.helpers import fetch_query_params

# Basic Authentication - User and Password
auth = HTTPBasicAuth()

users = {
    "john": generate_password_hash("hello"),
    "susan": generate_password_hash("bye")
}


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        config = configparser.ConfigParser()
        config.read_file(open('config.ini'))

        if 'CLOUD' not in os.environ:
            # If the application is running locally, use config.ini anf if not, use environment variables
            agnes_key = config['AGNES_KEY']['key']
            agnes_secret = config['AGNES_SECRET']['secret']
        else:
            agnes_key = os.environ['AGNES_KEY']
            agnes_secret = os.environ['AGNES_SECRET']

        ret = dict(fetch_query_params(request))

        if 'token' in ret.keys():
            token = ret.get('token')
            try:
                payload = jwt.decode(token, agnes_secret, algorithms=['HS256'])
                key = payload['key']

                if not token or agnes_key != key:
                    message = {'message': 'The provided API key is not valid'}
                    # Making the message looks good
                    resp = jsonify(message)
                    # Sending OK response
                    resp.status_code = 404
                    return resp

                return f(*args, **kwargs)

            except InvalidTokenError as e:
                logging.exception(e, exc_info=False)

                message = {'message': 'Please provide an valid API key'}
                # Making the message looks good
                resp = jsonify(message)
                # Sending OK response
                resp.status_code = 500
                return resp

        else:
            message = {'message': 'Please provide an valid API key'}
            # Making the message looks good
            resp = jsonify(message)
            # Sending OK response
            resp.status_code = 500
            return resp

    return decorated
