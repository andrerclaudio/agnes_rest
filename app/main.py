# Build-in modules
# import configparser
import logging
# import os

# Installed modules
# from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
# from flask_pymongo import PyMongo

# Local modules
# import app.schedulers as schedulers
# from app.schedulers import currency_info
from app.queries.query_currency import dollar_currency as currency

# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)

"""
Add a scheduler to the application
"""
# sched = BackgroundScheduler(daemon=True)
# sched.add_job(schedulers.get_currency, 'interval', seconds=currency_info.ALPHA_VANTAGE_REQUEST_CURRENCY_TIMEOUT)
# sched.start()

"""
Start Flask and related functions and decorators
"""
# Place where app is defined
app = Flask(__name__)
# MongoDB
# config = configparser.ConfigParser()
# config.read_file(open('config.ini'))
# if 'CLOUD' not in os.environ:
#     # If the application is running locally, use config.ini anf if not, use environment variables
#     mongo_path = config['MONGO_PATH']['url']
# else:
#     mongo_path = os.environ['MONGO_PATH']
#
# app.config["MONGO_URI"] = mongo_path
# mongo = PyMongo(app)
# External methods
app.add_url_rule('/currency', methods=['GET'], view_func=currency)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Application is alive"""
    # Making the message looks good

    # books = []
    # gather = list(mongo.db.books.find({}))
    #
    # for v in gather:
    #     del v['_id']
    #     books.append(v)

    resp = jsonify([{"bookName": "Agnes",
                     "bookAuthor": "Andre Ribeiro",
                     "bookPublisher": "Cia. das Letras",
                     "bookIsbn": "123456789",
                     "bookQtyPages": "123",
                     "bookCoverLink": 'https://images-na.ssl-images-amazon.com/images/I/41tpztfvPML.jpg'},
                    {"bookName": "Livoreto",
                     "bookAuthor": "Michele Costa",
                     "bookPublisher": "Morro Branco",
                     "bookIsbn": "987654321",
                     "bookQtyPages": "456",
                     "bookCoverLink": 'https://m.media-amazon.com/images/I/41BrJbt2TML.jpg'}
                    ])

    # resp = jsonify(books)
    # Sending OK response
    resp.status_code = 200
    # Returning the object
    return resp


@app.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    # Message to the user
    message = {
        "err":
            {
                "msg": "This route is currently not supported."
            }
    }
    logger.error(e)
    # Making the message looks good
    resp = jsonify(message)
    # Sending ERROR response
    resp.status_code = 404
    # Returning the object
    return resp
