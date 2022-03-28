"""

All methods related to the dollar API.

"""

from flask import jsonify

from app.contants import currency_info as currency


def dollar_currency():
    """
    Get dollar to Brazilian Real currency rate.
    /currency
    """

    # Message to the user
    message = {
        'dollarRate': f'{currency.dollar_brl_info["5. Exchange Rate"]:.2f}',
        'lastRefreshed': f'{currency.dollar_brl_info["6. Last Refreshed"]}'
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp
