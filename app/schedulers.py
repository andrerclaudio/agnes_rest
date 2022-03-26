"""
All functions that need to be scheduled are here.
"""

import logging
import os

import requests

from app.contants import currency_info

# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


def get_currency():
    """
    Go fetch the currency Dollar x Brazilian Real
    """

    alpha_vantage_apikey = os.environ['ALPHA_VANTAGE_KEY']

    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=BRL&apikey' \
          '={}'.format(alpha_vantage_apikey)

    r = requests.get(url)
    data = r.json()
    currency_info.currency_dollar_brl_info = data
