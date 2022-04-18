"""
Support and Helpers functions.
"""

# Installed modules
import isbnlib


def fetch_token(request):
    """
    Function to parse the query parameter string.
    """

    # Return the raw token string
    values = {}
    for k, v in request.args.items():
        values[k] = v

    return values['token']


def fix_isbn_format(isbn_like):
    """
    This function is going to check if the ISBN is valid.
    """

    val = [c for c in isbn_like if c.isdigit()]
    isbn = ''.join(val)

    if isbnlib.is_isbn10(val):
        isbn = isbnlib.to_isbn13(val)

    if isbnlib.is_isbn13(isbn):
        return isbn
    else:
        return False
