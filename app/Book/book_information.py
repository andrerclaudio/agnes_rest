# Build-in modules
import base64
import configparser
import logging
import os

import requests
from bs4 import BeautifulSoup
from flask import json

from app.Book.book_format import BookFullInformation
from app.GoodReads.client import GoodReadsClient
from app.Tools.helpers import isbn_checker
from app.error_codes import ValidationCodes

# Printing object
logger = logging.getLogger(__name__)


class RetrieveBookInformation(object):
    """
    Retrieve information about a Book.
    """

    def __init__(self):
        # Make the default answer
        self.response = [
            {
                "successOnRequest": False,
                "errorCode": ValidationCodes.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE,
                "bookInfo": BookFullInformation.bookFullInformation
            }
        ]
        self.code = 200

    @isbn_checker
    def on_local_library(self, isbn, mongo):
        """
        Fetch book information given an ISBN code on local Library.
        """

        try:
            if isbn:
                books_covers = []
                # Find the book by ISBN.
                ret = list(mongo.db.library.find({'isbn': isbn}))
                # Make sure query find a book.
                if len(ret):
                    # Prepare the answer back
                    for idx, value in enumerate(ret):
                        # Fetch book cover
                        r = ret[0]
                        pic = r["rawCoverPic"].decode("utf-8")
                        book_cover_picture = json.dumps(pic)
                        books_covers.append(book_cover_picture)

                        self.response = [
                            {
                                "successOnRequest": True,
                                "errorCode": ValidationCodes.SUCCESS,
                                "bookInfo": {

                                    "title": ret[idx]["title"],
                                    "author": ret[idx]["author"],
                                    "publisher": ret[idx]["publisher"],
                                    "isbn": ret[idx]["isbn"],
                                    "pagesQty": ret[idx]["pagesQty"],
                                    "description": ret[idx]["description"],
                                    "link": ret[idx]["link"],
                                    "genres": ret[idx]["genres"],
                                    "coverType": ret[idx]["coverType"],
                                    "coverPic": books_covers[idx],
                                    "language": ret[idx]["language"],
                                    "ratingAverage": ret[idx]["ratingAverage"]
                                }
                            }
                        ]

        except Exception as e:
            # If something wrong happens, raise an Internal server error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code

    @isbn_checker
    def on_internet(self, isbn, mongo):
        """
        Retrieve information about a Book remotely.
        """

        try:
            if isbn:
                # Find on GoodReads
                ret = self.__good_reads(isbn)
                if len(ret):

                    # Parse the Cover picture format
                    response = requests.get(ret["coverLink"])
                    book_cover_picture = base64.b64encode(response.content)

                    # Create the new book Schema
                    book = [
                        {
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
                            "rawCoverPic": book_cover_picture,
                            "language": ret["language"],
                            "ratingAverage": "0.0",
                            "favoriteCount": "",
                            "publicationDate": "",
                            "similar": [
                                {
                                    "bookId": ""
                                }
                            ],
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
                        }
                    ]

                    # Save the book Information on Database
                    added = mongo.db.library.insert_many(book)
                    if not added.acknowledged:
                        raise Exception('The database have failed to add the new book to database.')

                    # Adjust the book Cover Picture format
                    pic = book_cover_picture.decode("utf-8")
                    book_cover_picture = json.dumps(pic)

                    self.response = [
                        {
                            "successOnRequest": True,
                            "errorCode": ValidationCodes.SUCCESS,
                            "bookInfo":
                                {
                                    "title": ret["title"],
                                    "author": ret["author"],
                                    "publisher": ret["publisher"],
                                    "isbn": ret["isbn"],
                                    "pagesQty": ret["pagesQty"],
                                    "description": ret["description"],
                                    "link": ret["link"],
                                    "genres": "",
                                    "coverType": "",
                                    "coverPic": book_cover_picture,
                                    "language": ret["language"],
                                    "ratingAverage": "0.0"
                                }
                        }
                    ]

        except Exception as e:
            # If something wrong happens, raise an Internal server error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code

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
            book_info = self.__isbn_lookup(isbn, good_reads)
            # Check for a valid information
            if len(book_info):
                # Return the book info
                rsp = book_info

        except Exception as e:
            logger.exception(e, exc_info=False)

        finally:
            return rsp

    @staticmethod
    def __isbn_lookup(isbn, good_reads):
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

            # Scrap the book cover link
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
            cover_link = soup.find("img", {"id": "coverImage"})

            info = {

                "title": book.title,
                "author": str(book.authors[0]),
                "publisher": publisher,
                "isbn": book.isbn13,
                "pagesQty": pages_qty,
                "coverLink": cover_link.attrs['src'],
                "description": description,
                "language": language,
                "link": book.link

            }

        except Exception as e:
            logger.exception('{}'.format(e), exc_info=False)

        finally:
            return info
