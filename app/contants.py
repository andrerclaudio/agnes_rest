"""
All system constants.
"""


class CurrencyExchangeInfo(object):
    """

    """

    def __init__(self):
        # The alpha vantage API is free until 500 requests a day. https://www.alphavantage.co/documentation/
        self.ALPHA_VANTAGE_REQUEST_CURRENCY_TIMEOUT = 300

        self.currency_dollar_brl_info = {

            '5. Exchange Rate': 0,
            '6. Last Refreshed': 0

        }


currency_info = CurrencyExchangeInfo()
