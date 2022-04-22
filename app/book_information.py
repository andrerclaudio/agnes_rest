# Build-in modules
import os
import logging
import configparser

# Installed modules
import requests
from bs4 import BeautifulSoup

# Local modules
from app.connectors import mongo
from app.Tools.helpers import isbn_checker
from app.error_codes import ValidationMessages
from app.GoodReads.client import GoodReadsClient

# Printing object
logger = logging.getLogger(__name__)


class FetchBookInformation(object):
    """
    Add a new reading given a ISBN.
    """

    def __init__(self):
        # Make the default answer
        self.response = []
        # The code is Ok but more details is in self.response
        self.code = 200

    @isbn_checker
    def on_local_library(self, isbn=''):
        """
        Fetch book information given an ISBN code on local Library.
        """

        # Make the default answer
        self.response = [{
            "successOnRequest": False,
            "errorCode": ValidationMessages.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE,
            "title": "",
            "author": "",
            "publisher": "",
            "isbn": "",
            "pagesQty": "",
            "genres": "",
            "coverType": "",
            "coverLink": "",
            "ratingAverage": ""
        }]

        try:
            if isbn:
                # Find the book by ISBN.
                ret = list(mongo.db.library.find({'isbn': isbn}))
                # Make sure query find a book.
                if len(ret) > 0:
                    # Prepare the answer back
                    for idx, value in enumerate(ret):
                        self.response = [{
                            "successOnRequest": True,
                            "errorCode": ValidationMessages.SUCCESS,
                            "title": ret[idx]["title"],
                            "author": ret[idx]["author"],
                            "publisher": ret[idx]["publisher"],
                            "isbn": ret[idx]["isbn"],
                            "pagesQty": ret[idx]["pagesQty"],
                            "genres": ret[idx]["genres"],
                            "coverType": ret[idx]["coverType"],
                            "coverLink": ret[idx]["coverLink"],
                            "ratingAverage": ret[idx]["ratingAverage"]
                        }]

        except Exception as e:
            # If something wrong happens, raise an Internal ser error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code

    @isbn_checker
    def on_internet(self, isbn=''):
        """
        Fetch book information given an ISBN code on the internet.
        """

        # Make the default answer
        self.response = {
            "successOnRequest": False,
            "errorCode": ValidationMessages.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE,
            "title": "",
            "author": "",
            "publisher": "",
            "isbn": "",
            "pagesQty": "",
            "genres": "",
            "coverType": "",
            "coverLink": "",
            "ratingAverage": ""
        }

        try:
            if isbn:
                # Find on GoodReads
                ret = self.__good_reads(isbn)
                if len(ret) > 0:
                    # Create the new book Schema
                    book = [{
                        "title": ret["title"],
                        "author": ret["author"],
                        "publisher": ret["publisher"],
                        "isbn": ret["isbn"],
                        "pagesQty": ret["pagesQty"],
                        "description": ret["description"],
                        "link": ret["link"],
                        "genres": "",
                        "coverType": "",
                        "coverLink": ret["coverLink"],
                        "favoriteCount": "",
                        "language": ret["language_code"],
                        "publicationDate": "",
                        "similar": [
                            {
                                "bookId": ""
                            }
                        ],
                        "ratingAverage": "0.0",
                        "ratingDetails": [
                            {
                                "rating": "5",
                                "ratingCount": "0"
                            },
                            {
                                "rating": "4",
                                "ratingCount": "0"
                            },
                            {
                                "rating": "3",
                                "ratingCount": "0"
                            },
                            {
                                "rating": "2",
                                "ratingCount": "0"
                            },
                            {
                                "rating": "1",
                                "ratingCount": "0"
                            }
                        ],
                        "reviewsCount": "0",
                        "reviews": [
                            {
                                "reviewerId": "",
                                "reviewerRating": "",
                                "reviewerComment": ""
                            }
                        ]
                    }]

                    # Save on Database
                    added = mongo.db.library.insert_many(book)
                    if not added:
                        raise Exception('The database have failed to add the new book to database.')

                    self.response["successOnRequest"] = True
                    self.response["errorCode"] = ValidationMessages.SUCCESS,
                    self.response.update(ret)

        except Exception as e:
            # If something wrong happens, raise an Internal ser error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return [self.response], self.code

    def __good_reads(self, isbn):
        """
        Find the book info on the GoodReads.
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
            book_info = self.__isbn_lookup(self, isbn, good_reads)
            # Check for a valid information
            if len(book_info) > 0:
                # Return the book info
                rsp = book_info

        except Exception as e:
            logger.exception(e, exc_info=False)

        finally:
            return rsp

    @staticmethod
    def __isbn_lookup(self, isbn, good_reads):
        """
        Fetch in Good Reads for a given ISBN code and scrapy for its cover image.
        """

        info = {}

        try:
            book = good_reads.book(isbn=isbn)

            publisher = book.publisher if book.publisher is not None else '-'
            description = book.description if book.description is not None else '-'
            language = book.language_code if book.language_code is not None else '-'
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

            info = {

                "title": book.title,
                "author": str(book.authors[0]),
                "publisher": publisher,
                "isbn": book.isbn13,
                "pagesQty": pages_qty,
                "coverLink": tag.attrs['src'],
                "description": description,
                "language_code": language,
                "link": book.link

            }

        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)

        finally:
            return info
