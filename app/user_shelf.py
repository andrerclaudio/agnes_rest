# Build-in modules
import base64
import logging
from datetime import datetime

# Installed modules
import pytz
from bson.objectid import ObjectId

# Local modules
from app.Tools.helpers import isbn_checker
from app.book_format import BookBasicInformation
from app.connectors import mongo
from app.error_codes import ValidationCodes

# Printing object
logger = logging.getLogger(__name__)


class UserShelf(object):
    """
    Add a new reading given a ISBN.
    """

    def __init__(self):
        # Make the default answer
        self.response = []
        # The code is Ok but more details is in self.response
        self.code = 200

    @isbn_checker
    def add_new_book(self, isbn):
        """
        Add a new book to user Shelf given an ISBN code
        """

        # Make the default answer
        self.response = [{
            'successOnRequest': False,
            "errorCode": ValidationCodes.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE,
            'isbn': '',
            'title': ''
        }]

        try:
            if isbn:
                # Check whether the given Isbn is already active (Reading ou Paused) or not.
                active_books, _ = self.current_readings()

                book_list = [book_info['bookInfo'] for book_info in active_books]

                if isbn not in [isbn_code['isbn'] for isbn_code in book_list]:
                    # Find the book by ISBN.
                    query = {'isbn': isbn}
                    ret = list(mongo.db.library.find(query))
                    if len(ret) > 0:
                        book_id = str(ret[0]['_id'])
                        # Mount the New Reading Schema.
                        info = [{
                            "readingInProgress": True,
                            "readingPaused": False,
                            "readingCanceled": False,
                            "readingFinished": False,
                            "favorite": False,
                            "lastPage": "",
                            "rating": "",
                            "review": "",
                            "quotes": {},
                            "remarks": {},
                            "sameBookCount": {
                                "0": {
                                    "startedAt": datetime.now(tz=pytz.UTC),
                                    "finishedAt": "",
                                    "canceledAt": ""
                                }
                            },
                            "targetBookId": book_id
                        }]
                        # Store the New Reading schema on the user shelf.
                        added = mongo.db.users_shelf.insert_many(info)
                        if not added:
                            raise Exception('The database have failed to add the book to user shelf.')

                        # Prepare the answer back
                        self.response = [{
                            'successOnRequest': True,
                            "errorCode": ValidationCodes.SUCCESS,
                            'isbn': ret[0]['isbn'],
                            'title': ret[0]['title']
                        }]
                        # Created
                        self.code = 201
                else:
                    # Make the default answer
                    self.response = [{
                        'successOnRequest': False,
                        "errorCode": ValidationCodes.BOOK_HAS_ALREADY_BEEN_ADDED_TO_BOOK_SHELF,
                        'isbn': '',
                        'title': ''
                    }]

        except Exception as e:
            # If something wrong happens, raise an Internal ser error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code

    def current_readings(self):
        """
        Fetch the active or paused readings.
        """

        # Make the default answer
        self.response = [
            {
                "successOnRequest": False,
                "errorCode": ValidationCodes.NO_ACTIVE_OR_PAUSED_READING_WAS_FOUND,
                "readingInProgress": False,
                "readingPaused": False,
                "readingCanceled": False,
                "readingFinished": False,
                "bookInfo": BookBasicInformation.bookBasicInformation
            }
        ]

        try:
            # Fetch readings in Progress or Paused.
            query = {"$or": [{'readingInProgress': True}, {'readingPaused': True}]}
            query_resp = list(mongo.db.users_shelf.find(query))
            # Check if the query returned results
            if len(query_resp) > 0:
                # Iterate over the books details by book ID.
                book_details = []
                for value in query_resp:
                    # Fetch book information
                    ret = list(mongo.db.library.find({'_id': ObjectId(value['targetBookId'])}))
                    book_details.extend(ret)
                    # Fetch book cover
                    ret = list(mongo.db.covers.find({'name': ObjectId(value['targetBookId'])}))[0]
                    pic = ret["data"]
                    pic_64 = base64.b64decode(pic)

                # Make sure a book was found
                if len(book_details) > 0:
                    # Prepare the answer back
                    self.response.clear()
                    for idx, value in enumerate(query_resp):
                        info = {
                            "successOnRequest": True,
                            "errorCode": ValidationCodes.SUCCESS,
                            "readingInProgress": value["readingInProgress"],
                            "readingPaused": value["readingPaused"],
                            "readingCanceled": value["readingCanceled"],
                            "readingFinished": value["readingFinished"],
                            "bookInfo":
                                {
                                    "title": book_details[idx]["title"],
                                    "author": book_details[idx]["author"],
                                    "publisher": book_details[idx]["publisher"],
                                    "isbn": book_details[idx]["isbn"],
                                    "pagesQty": book_details[idx]["pagesQty"],
                                    "coverLink": book_details[idx]["coverLink"]
                                }
                        }
                        self.response.append(info)

        except Exception as e:
            # If something wrong happens, raise an Internal ser error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code
