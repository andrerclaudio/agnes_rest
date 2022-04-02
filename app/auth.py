# Build-in modules
import configparser
import logging
import os
from functools import wraps

# Installed modules
import jwt
# from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, request
from flask_httpauth import HTTPTokenAuth  # HTTPBasicAuth
from jwt import InvalidTokenError

# Basic Authentication - User and Password
# auth = HTTPBasicAuth()
auth = HTTPTokenAuth(scheme='Bearer')


# users = {
#     "john": generate_password_hash("hello"),
#     "susan": generate_password_hash("bye")
# }


# @auth.verify_password
# def verify_password(username, password):
#     if username in users and check_password_hash(users.get(username), password):
#         return username


def authorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        config = configparser.ConfigParser()
        config.read_file(open('config.ini'))

        if 'CLOUD' not in os.environ:
            # If the application is running locally, use config.ini anf if not, use environment variables
            agnes_secret = config['AGNES_SECRET']['secret']
        else:
            agnes_secret = os.environ['AGNES_SECRET']

        try:
            header = str(request.headers.get('Authorization')).split(' ')
            token = header[1]
            payload = jwt.decode(token, agnes_secret, algorithms=['HS256'])
            return f(payload)

        except InvalidTokenError as e:
            logging.exception(e, exc_info=False)
            message = {'message': 'Invalid Credentials.'}
            # Making the message looks good
            resp = jsonify(message)
            # Sending OK response
            resp.status_code = 403
            return resp

    return decorated
