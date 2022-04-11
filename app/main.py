# Build-in modules
import logging

# Installed modules
# from apscheduler.schedulers.background import BackgroundScheduler
from flask import jsonify

# Local modules
from app.connectors import create_app
from app.dispatcher import query_dispatcher as dispatcher

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
Start Flask, related functions and basic routes. 
"""
app = create_app()
# External methods
app.add_url_rule('/query', methods=['GET'], view_func=dispatcher)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Application is alive"""

    # This route is used when the incoming user is not registered yet.
    resp = jsonify([])

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
