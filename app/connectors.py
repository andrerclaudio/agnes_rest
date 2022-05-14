# Build-in modules
import configparser
import logging
import os

# Installed modules
from flask import Flask
from flask_httpauth import HTTPTokenAuth
from flask_pymongo import PyMongo

# Printing object
logger = logging.getLogger(__name__)


class CreateApp(object):
    """
    Start Flask application and Initialize MongoDB instance.
    """

    def __init__(self):
        # Place where app is defined
        self.app = Flask(__name__, instance_relative_config=False)

        if 'CLOUD' not in os.environ:
            # If the application is running locally, use config.ini anf if not, set environment variables# MongoDB
            config = configparser.ConfigParser()
            config.read_file(open('config.ini'))
            # Agnes API secret
            secret = config['AGNES_SECRET']['secret']
            # Mongo path
            mongo_path = config['MONGO_PATH']['url']
        else:
            # Agnes API secret
            secret = os.environ['AGNES_SECRET']
            # Mongo path
            mongo_path = os.environ['MONGO_PATH']

        # Set the API secret value
        self.app.config['SECRET_KEY'] = secret
        # Bearer authentication
        self.auth = HTTPTokenAuth(scheme='Bearer', realm=secret)
        # MongoDB
        self.app.config["MONGO_URI"] = mongo_path
        self.mongo = PyMongo()
        self.mongo.init_app(self.app)
