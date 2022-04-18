# Build-in modules
import configparser
import logging
import os

# Installed modules

# Local modules
from app.Book.client import GoodReadsClient
from app.Tools.new_book import isbn_lookup

# Printing object
logger = logging.getLogger(__name__)


def fetch_book_remote(isbn):
    """
    Find the book info over the internet.
    """

    rsp = {}

    try:
        # GoodReader initializer
        if 'CLOUD' not in os.environ:
            config = configparser.ConfigParser()
            config.read_file(open('config.ini'))
            # If the application is running locally, use config.ini anf if not, use environment variables
            good_reads_key = config['GOOD_READS_KEY']['key']
            good_reads_secret = config['GOOD_READS_SECRET']['secret']
        else:
            good_reads_key = os.environ['GOOD_READS_KEY']
            good_reads_secret = os.environ['GOOD_READS_SECRET']

        good_reads = GoodReadsClient(good_reads_key, good_reads_secret)
        # ISBN related functions
        book_info = isbn_lookup(isbn, good_reads)
        # Check for a valid information
        if len(book_info) > 0:
            # Return the book info
            rsp = book_info

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        return rsp
