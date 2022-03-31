"""

All methods related to the dollar API.

"""

# Installed modules
from flask import jsonify

# Local modules
from app.shared_variables_ import currency_info as currency


def dollar_currency():
    """
    Get dollar to Brazilian Real currency rate.
    /currency
    """

    value = float(currency.dollar_brl_info["5. Exchange Rate"])

    # Message to the user
    message = {
        'dollarRate': f'{value:.2f}'
    }

    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp