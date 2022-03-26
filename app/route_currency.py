"""

All methods related to the dollar API.

"""

from flask import jsonify
from forex_python.converter import CurrencyRates

from app.contants import currency_info


def dollar_currency():
    """
    Get dollar to Brazilian Real currency rate.
    /currency
    """

    c = CurrencyRates(force_decimal=False)
    ret = c.get_rate('USD', 'BRL')

    # Message to the user
    message = {
        'Exchange Rate': f'{currency_info["5. Exchange Rate"]:.2f}',
        'Last Refreshed': f'{currency_info["6. Last Refreshed"]}'
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp
