# Build-in modules
import logging
from datetime import datetime

# Installed modules
import pytz
from bson.objectid import ObjectId
from flask import json

# Local modules
from app.Book.book_format import BookBasicInformation
from app.Tools.helpers import isbn_checker
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
    def add_new_book(self, user_shelf_id, isbn, mongo):
        """
        Add a new book to user Shelf given an ISBN code
        """
        try:
            # Check ISBN sanity
            if isbn:
                # Check whether the given Isbn is already active (Reading ou Paused) or not.
                active_books, _ = self.current_readings(user_shelf_id, mongo=mongo, only_isbn=True)
                # List all active readings
                book_list = [book_info['bookInfo'] for book_info in active_books]
                # Check the given one is one of them
                if isbn not in [isbn_code['isbn'] for isbn_code in book_list]:
                    # Find the book by ISBN.
                    ret = list(mongo.db.library.find({'isbn': isbn}, {'isbn', 'title'}))
                    if len(ret):
                        book_id = str(ret[0]['_id'])
                        # Mount the New Reading Schema.
                        info = {
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
                        }
                        # Store the New Reading schema on the user shelf.
                        updated = mongo.db.users_shelf.update_one({'_id': ObjectId(user_shelf_id)},
                                                                  {'$push': {'books': info}})

                        if not updated.acknowledged:
                            raise Exception('The database have failed to add the book to user shelf.')

                        mongo.db.users_shelf.update_one({'_id': ObjectId(user_shelf_id)},
                                                        {'$inc': {'booksQty': 1}})

                        mongo.db.users_shelf.update_one({'_id': ObjectId(user_shelf_id)},
                                                        {'$set': {'lastUpdate': datetime.now(tz=pytz.UTC)}})

                        # TODO What happens if any of the updates before fail

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
                        raise Exception('The given book as not previous added on Library!')
                else:
                    # Make the default answer
                    self.response = [{
                        'successOnRequest': False,
                        "errorCode": ValidationCodes.BOOK_HAS_ALREADY_BEEN_ADDED_TO_BOOK_SHELF,
                        'isbn': '',
                        'title': ''
                    }]
            else:
                self.response = [{
                    'successOnRequest': False,
                    "errorCode": ValidationCodes.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE,
                    'isbn': '',
                    'title': ''
                }]

        except Exception as e:
            # If something wrong happens, raise an Internal server error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code

    def current_readings(self, user_shelf_id, mongo, only_isbn=False):
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
            if only_isbn:
                # Fetch readings in Progress or Paused.
                query_resp = list(mongo.db.users_shelf.find({"$and": [{"$and": [{'_id': ObjectId(user_shelf_id)}]},
                                                                      {"$or": [
                                                                          {'books.readingInProgress': True},
                                                                          {'books.readingPaused': True}]}
                                                                      ]}, {'books.targetBookId'}))

                if len(query_resp):
                    # Prettify the fetched data
                    data = query_resp[0]['books']
                    # Iterate over the books details by book ID.
                    book_details = []
                    for value in data:
                        # Fetch book information
                        ret = list(mongo.db.library.find({'_id': ObjectId(value['targetBookId'])},
                                                         {'isbn'}))
                        book_details.extend(ret)
                    # Make sure a book was found
                    if len(book_details):
                        # Prepare the answer back
                        self.response.clear()
                        for idx, _ in enumerate(data):
                            info = {
                                "bookInfo":
                                    {
                                        "isbn": book_details[idx]["isbn"],
                                    }
                            }
                            self.response.append(info)

            else:
                # Fetch readings in Progress or Paused on a given User ID
                query_resp = list(mongo.db.users_shelf.find({"$and": [{"$and": [{'_id': ObjectId(user_shelf_id)}]},
                                                                      {"$or": [
                                                                          {'books.readingInProgress': True},
                                                                          {'books.readingPaused': True}]}
                                                                      ]}, {'books'}))
                # Check if the query returned results
                if len(query_resp):
                    # Prettify the fetched data
                    data = query_resp[0]['books']
                    # Iterate over the books details by book ID.
                    book_details = []
                    books_covers = []
                    for value in data:
                        # Fetch book information
                        ret = list(mongo.db.library.find({'_id': ObjectId(value['targetBookId'])}))
                        book_details.extend(ret)
                        # Fetch book cover
                        ret = ret[0]
                        pic = ret["rawCoverPic"].decode("utf-8")
                        book_cover_picture = json.dumps(pic)
                        books_covers.append(book_cover_picture)

                    # Make sure a book was found
                    if len(book_details):
                        # Prepare the answer back
                        self.response.clear()
                        for idx, value in enumerate(data):
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
                                        "coverPic": books_covers[idx]
                                    }
                            }
                            self.response.append(info)

        except Exception as e:
            # If something wrong happens, raise an Internal server error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code
