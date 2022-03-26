"""
All system constants.
"""


class CurrencyExchangeInfo(object):
    """
    Currency constants and data
    """

    def __init__(self):
        # The alpha vantage API is free until 500 requests a day. https://www.alphavantage.co/documentation/
        self.ALPHA_VANTAGE_REQUEST_CURRENCY_TIMEOUT = 300
        # Hold all information fetched from Alpha Vantage
        self.dollar_brl_info = dict()


# Initialize the object
currency_info = CurrencyExchangeInfo()
