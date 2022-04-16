# Build-in modules
import configparser
import logging
import os
from functools import wraps

# Installed modules
import jwt
from flask import jsonify, request
from jwt import InvalidTokenError

# Local modules
from app.helpers import fetch_token


def decryption(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if 'CLOUD' not in os.environ:
            config = configparser.ConfigParser()
            config.read_file(open('config.ini'))
            # If the application is running locally, use config.ini anf if not, use environment variables
            agnes_secret = config['AGNES_SECRET']['secret']
        else:
            agnes_secret = os.environ['AGNES_SECRET']

        try:
            token = fetch_token(request)
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
