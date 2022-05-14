# Build-in modules
import logging
from functools import wraps

# Installed modules
import isbnlib

# Printing object
logger = logging.getLogger(__name__)


def isbn_checker(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        """
        This method is going to check whether the ISBN is valid or not.
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
                return f(*args, isbn, kwargs['mongo'])
            else:
                return f(*args, '', '')

        except Exception as e:
            logging.exception(e, exc_info=False)
            return f(*args, '')

    return decorated
