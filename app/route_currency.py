"""

All methods related to the dollar API.

"""

from flask import jsonify
from forex_python.converter import CurrencyRates


def dollar_currency():
    """
    Get dollar to Brazilian Real currency rate.
    /currency
    """

    c = CurrencyRates(force_decimal=False)
    ret = c.get_rate('USD', 'BRL')

    # Message to the user
    message = {
        'dollarXbrl': f'{ret:.2f}',
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp
