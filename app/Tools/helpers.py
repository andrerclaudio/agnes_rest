"""
Support functions.
"""
# Build-in modules
from functools import wraps
import logging

# Installed modules
import isbnlib
from flask import request

# Printing object
logger = logging.getLogger(__name__)


def fetch_args():
    """
    # Return args inside a request.
    """
    values = {}
    for k, v in request.args.items():
        values[k] = v

    return values


def isbn_checker(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        """
        This function is going to check whether the ISBN is valid or return ''.
        """

        try:
            # Extract the ISBN code from kwargs
            isbn_code = kwargs['isbn']
            # Check its integrity
            val = [c for c in isbn_code if c.isdigit()]
            isbn = ''.join(val)

            if isbnlib.is_isbn10(val):
                isbn = isbnlib.to_isbn13(val)

            if isbnlib.is_isbn13(isbn):
                return f(*args, isbn)
            else:
                return f(*args, '')

        except Exception as e:
            logging.exception(e, exc_info=False)
            return f(*args, '')

    return decorated
