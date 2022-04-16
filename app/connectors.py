# Build-in modules
import configparser
import logging
import os

# Installed modules
from flask import Flask
from flask_pymongo import PyMongo

# Database connector
mongo = PyMongo()

# Printing object
logger = logging.getLogger(__name__)


def create_app():
    """
    Start Flask application and Initialize MongoDB.
    """
    # Place where app is defined
    app = Flask(__name__, instance_relative_config=False)

    # MongoDB
    config = configparser.ConfigParser()
    config.read_file(open('config.ini'))
    if 'CLOUD' not in os.environ:
        # If the application is running locally, use config.ini anf if not, use environment variables
        mongo_path = config['MONGO_PATH']['url']
    else:
        mongo_path = os.environ['MONGO_PATH']

    app.config["MONGO_URI"] = mongo_path
    mongo.init_app(app)

    return app
