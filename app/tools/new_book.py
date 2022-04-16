# Build-in modules
import logging

# Installed modules
import requests
import isbnlib
from bs4 import BeautifulSoup

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

            headers = {
                'dnt': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/83.0.4103.61 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                          'application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'referer': 'https://www.goodreaders.com/',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }

            raw = requests.get(book.link, headers=headers).content
            soup = BeautifulSoup(raw, 'html.parser', from_encoding='UTF-8')
            tag = soup.find("img", {"id": "coverImage"})

            book_info = {

                "title": book.title,
                "author": str(book.authors[0]),
                "publisher": publisher,
                "isbn": book.isbn13,
                "pagesQty": pages_qty,
                "coverLink": tag.attrs['src'],

            }

        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)
        finally:
            return book_info
    else:
        return book_info
