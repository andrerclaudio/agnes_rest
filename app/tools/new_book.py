# Build-in modules
import logging
from urllib.request import urlopen
import json

# Installed modules
import isbnlib

# Local modules

# Printing object
logger = logging.getLogger(__name__)


def isbn_lookup(isbnlike, good_reads):
    """
    Fetch in Good Reads for a given ISBN code
    """
    book_info = {}

    val = [c for c in isbnlike if c.isdigit()]
    isbn = ''.join(val)

    if isbnlib.is_isbn10(val):
        isbn = isbnlib.to_isbn13(val)

    if isbnlib.is_isbn13(isbn):
        try:
            book = good_reads.book(isbn=isbn)

            publisher = book.publisher if book.publisher is not None else '-'
            pages_qty = book.num_pages if book.num_pages is not None else '0'

            book_info = {

                "title": book.title,
                "author": str(book.authors[0]),
                "publisher": publisher,
                "isbn": book.isbn13,
                "pagesQty": pages_qty,
                "coverLink": book.small_image_url,

            }

        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)
        finally:
            return book_info
    else:
        return book_info
