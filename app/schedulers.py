"""
All functions that need to be scheduled are here.
"""

import configparser
# Build-in modules
import logging
import os

# Installed modules
import requests

# Local modules
from app.queries.query_currency import currency_info


def get_currency():
    """
    Go fetch the currency Dollar x Brazilian Real
    """

    config = configparser.ConfigParser()
    config.read_file(open('config.ini'))

    if 'CLOUD' not in os.environ:
        # If the application is running locally, use config.ini anf if not, use environment variables
        alpha_vantage_apikey = config['ALPHA_VANTAGE_KEY']['key']
    else:
        alpha_vantage_apikey = os.environ['ALPHA_VANTAGE_KEY']

    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=BRL&apikey' \
          '={}'.format(alpha_vantage_apikey)

    try:
        r = requests.get(url)
        data = r.json()
        currency_info.dollar_brl_values = data['Realtime Currency Exchange Rate']

    except requests.exceptions as e:
        logging.exception(e, exc_info=False)
