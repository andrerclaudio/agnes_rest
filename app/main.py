# Build-in modules
import logging

# Installed modules
# from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify

# Local modules
# import app.schedulers as schedulers
# from app.schedulers import currency_info
from app.auth import token_required
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
# External methods
app.add_url_rule('/currency', methods=['GET'], view_func=currency)


@app.route('/', methods=['GET', 'POST'])
@token_required
def index():
    """Welcome message for the API."""

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
                "msg": "This route is currently not supported."
            }
    }
    logger.error(e)
    # Making the message looks good
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 404
    # Returning the object
    return resp
