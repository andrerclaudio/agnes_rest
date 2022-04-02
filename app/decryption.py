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
from app.helpers import fetch_payload


def decryption(f):
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
            payload_encrypted = fetch_payload(request)
            payload_decrypted = jwt.decode(payload_encrypted, agnes_secret, algorithms=['HS256'])
            return f(payload_decrypted)

        except InvalidTokenError as e:
            logging.exception(e, exc_info=False)
            message = {'message': 'The payload is not valid.'}
            # Making the message looks good
            resp = jsonify(message)
            # Sending OK response
            resp.status_code = 400
            return resp

    return decorated
