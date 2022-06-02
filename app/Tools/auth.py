# Build-in modules
import configparser
import logging
import os
from functools import wraps

# from cryptography.fernet import Fernet
# from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, request


def authorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if 'CLOUD' not in os.environ:
            config = configparser.ConfigParser()
            config.read_file(open('config.ini'))
            # Agnes API key
            # key = config['AGNES_KEY']['key']
            # enc = Fernet(key)
            # Agnes API secret
            secret = config['AGNES_SECRET']['secret']
            # token = f.encrypt(secret)
        else:
            # Agnes API key
            # key = os.environ['AGNES_KEY']
            # enc = Fernet(key)
            # Agnes API secret
            secret = os.environ['AGNES_SECRET']
            # token = f.encrypt(secret)

        try:
            header = str(request.headers.get('Authorization')).split(' ')
            if len(header) > 1:
                token = header[1]
            else:
                raise Exception('API token not valid!')

            if not token or token != secret:
                raise Exception('API token not valid!')
            else:
                return f(*args, **kwargs)

        except Exception as e:
            logging.exception(e, exc_info=False)
            message = {'message': 'Invalid Credentials.'}
            # Making the message looks good
            resp = jsonify(message)
            # Sending OK response
            resp.status_code = 401
            return resp

    return decorated
