"""

All methods related to the dollar API.

"""

# Installed modules
from flask import jsonify

from app.auth import auth
# Local modules
from app.decryption import decryption


class CurrencyExchangeInfo(object):
    """
    Currency constants and data
    """

    def __init__(self):
        # The alpha vantage API is free until 500 requests a day. https://www.alphavantage.co/documentation/
        self.ALPHA_VANTAGE_REQUEST_CURRENCY_TIMEOUT_IN_SECONDS = 300
        # Hold all information fetched from Alpha Vantage
        self.dollar_brl_values = {
            # Initialize the variables
            '5. Exchange Rate': f'{0.00}'
        }


# Initialize the object
currency_info = CurrencyExchangeInfo()


@auth.login_required
@decryption
def dollar_currency(f):
    """
    Get dollar to Brazilian Real currency rate.
    /currency
    """

    value = float(currency_info.dollar_brl_values["5. Exchange Rate"])

    # Message to the user
    message = {
        'dollarRate': f'{value:.2f}'
    }

    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp
