"""
All functions that need to be scheduled are here.
"""

import os

import requests

from app.contants import currency_info


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
    currency_info['5. Exchange Rate'] = data['5. Exchange Rate']
    currency_info['6. Last Refreshed'] = data['6. Last Refreshed']
