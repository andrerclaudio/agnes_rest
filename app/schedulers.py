"""
All functions that need to be scheduled are here.
"""

# Build-in modules
import logging
import os

# Installed modules
import requests

# Local modules
from app.shared_variables_ import currency_info


def get_currency():
    """
    Go fetch the currency Dollar x Brazilian Real
    """

    alpha_vantage_apikey = os.environ['ALPHA_VANTAGE_KEY']

    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=BRL&apikey' \
          '={}'.format(alpha_vantage_apikey)

    try:
        r = requests.get(url)
        data = r.json()
        currency_info.dollar_brl_info = data['Realtime Currency Exchange Rate']

    except requests.exceptions as e:
        logging.exception(e, exc_info=False)
