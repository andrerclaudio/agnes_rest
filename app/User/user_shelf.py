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
    User Shelf related methods.
    """

    def __init__(self):
        # Make the default answer
        self.response = []
        self.code = 200

    @isbn_checker
    def add_new_book(self, user_shelf_id, isbn, mongo):
        """
        Add a new book to user Shelf.
        """
        try:
            # Sanity check
            if isbn:
                # Check whether the given Isbn is already added to shelf or not.
                ret, _ = self.books(user_shelf_id, 'all', mongo)
                # Transform the result into a list
                isbn_list = [info['bookInfo'] for info in ret if info['successOnRequest']]
                # Check the given one is one of them
                if isbn not in [isbn_code['isbn'] for isbn_code in isbn_list]:
                    # Fetch the books details
                    ret = list(mongo.db.library.find({'isbn': isbn}, {'isbn', 'title'}))
                    if len(ret):
                        book_id = str(ret[0]['_id'])
                        # Mount the New Reading Schema.
                        t = datetime.now(tz=pytz.UTC)
                        info = {
                            "readingInProgress": True,
                            "readingPaused": False,
                            "readingCanceled": False,
                            "readingFinished": False,
                            "readingInStandby": False,
                            "wishList": False,
                            "favorite": False,
                            "lastPage": "",
                            "rating": "",
                            "review": "",
                            "quotes": {},
                            "remarks": {},
                            "addedToShelfAt": t,
                            "startedAt": t,
                            "finishedAt": "",
                            "canceledAt": "",
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

                        # Prepare the answer back
                        self.code = 201
                        self.response = [{
                            'successOnRequest': True,
                            "errorCode": ValidationCodes.SUCCESS}]
                    else:
                        raise Exception('The ISBN must be added to application library before reaching this point.')
                else:
                    # Make the default answer
                    self.response = [{
                        'successOnRequest': False,
                        "errorCode": ValidationCodes.BOOK_HAS_ALREADY_BEEN_ADDED_TO_USER_SHELF,
                    }]
            else:
                self.response = [{
                    'successOnRequest': False,
                    "errorCode": ValidationCodes.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE,
                }]

        except Exception as e:
            # If something wrong happens, raise an Internal server error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code

    def books(self, user_shelf_id, status, mongo):
        """
        Fetch the user shelf books.
        """

        try:

            if status == 'all':
                # Fetch all books and return only the ISBN code
                query_resp = list(mongo.db.users_shelf.find({'_id': ObjectId(user_shelf_id)}, {'books.targetBookId'}))
                # Verify the amount of books encountered
                if len(query_resp):
                    # Prettify the fetched data
                    data = query_resp[0]['books']
                    # Iterate over the books details by book ID.
                    book_details = []
                    for value in data:
                        # Fetch book information
                        ret = list(mongo.db.library.find({'_id': ObjectId(value['targetBookId'])}, {'isbn'}))
                        book_details.extend(ret)

                    # Prepare the answer back
                    self.response.clear()

                    for idx, _ in enumerate(data):
                        info = {
                            "successOnRequest": True,
                            "errorCode": ValidationCodes.SUCCESS,
                            "bookInfo":
                                {
                                    "isbn": book_details[idx]["isbn"],
                                }
                        }
                        self.response.append(info)

                else:
                    self.response = [
                        {
                            "successOnRequest": False,
                            "errorCode": ValidationCodes.BOOK_SHELF_IS_EMPTY,
                            "bookInfo": BookBasicInformation.bookBasicInformation
                        }
                    ]

            elif status == 'active':
                # Fetch readings in Progress or Paused ones
                query_resp = list(mongo.db.users_shelf.aggregate([{'$match': {'_id': ObjectId(user_shelf_id)}},
                                                                  {'$unwind': "$books"},
                                                                  {'$match': {"$or": [
                                                                      {'books.readingInProgress': True},
                                                                      {'books.readingPaused': True}]
                                                                  }}]))

            elif status == 'notActive':
                # Fetch readings with Canceled or Finished status
                query_resp = list(mongo.db.users_shelf.aggregate([{'$match': {'_id': ObjectId(user_shelf_id)}},
                                                                  {'$unwind': "$books"},
                                                                  {'$match': {"$or": [
                                                                      {'books.readingCanceled': True},
                                                                      {'books.readingFinished': True}]
                                                                  }}]))

            else:
                query_resp = []

            # Prepare the answer if the parameter is different of 'All'
            if status != 'all':
                # Check if the query returned results
                if len(query_resp):
                    # Prettify the fetched data
                    data = [i['books'] for i in query_resp]
                    # Iterate over the books details by book ID.
                    book_details = []
                    book_covers = []
                    book_target_ids = []
                    for value in data:
                        # Fetch book information
                        ret = list(mongo.db.library.find({'_id': ObjectId(value['targetBookId'])}))
                        book_target_ids.append(value['targetBookId'])
                        book_details.extend(ret)
                        # Fetch book cover
                        ret = ret[0]
                        pic = ret["rawCoverPic"].decode("utf-8")
                        book_cover_picture = json.dumps(pic)
                        book_covers.append(book_cover_picture)

                    # Prepare the answer back
                    self.response.clear()

                    for idx, _ in enumerate(data):
                        info = {
                            "successOnRequest": True,
                            "errorCode": ValidationCodes.SUCCESS,
                            "bookInfo":
                                {
                                    "title": book_details[idx]["title"],
                                    "author": book_details[idx]["author"],
                                    "publisher": book_details[idx]["publisher"],
                                    "isbn": book_details[idx]["isbn"],
                                    "pagesQty": book_details[idx]["pagesQty"],
                                    "coverPic": book_covers[idx],
                                    "targetBookId": book_target_ids[idx],
                                }
                        }
                        self.response.append(info)

                else:
                    self.response = [
                        {
                            "successOnRequest": False,
                            "errorCode": ValidationCodes.BOOK_SHELF_IS_EMPTY,
                            "bookInfo": BookBasicInformation.bookBasicInformation
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

    def update_book_status(self, user_shelf_id, target_book_id, status, mongo):
        """
        Update the book status.
        """

        try:
            # Parse the target status
            if status == 'finished':
                # Set the books as Finished
                updated = mongo.db.users_shelf.update_one(
                    {"_id": ObjectId(user_shelf_id),
                     "books.targetBookId": target_book_id},
                    {"$set": {"books.$.readingInProgress": False,
                              "books.$.readingPaused": False,
                              "books.$.readingCanceled": False,
                              "books.$.readingFinished": True,
                              }})

                mongo.db.users_shelf.update_one(
                    {"_id": ObjectId(user_shelf_id),
                     "books.targetBookId": target_book_id},
                    {"$set": {"books.$.finishedAt": datetime.now(tz=pytz.UTC),
                              }})

            elif status == 'canceled':
                # Set the books as Canceled
                updated = mongo.db.users_shelf.update_one(
                    {"_id": ObjectId(user_shelf_id),
                     "books.targetBookId": target_book_id},
                    {"$set": {"books.$.readingInProgress": False,
                              "books.$.readingPaused": False,
                              "books.$.readingCanceled": True,
                              "books.$.readingFinished": False,
                              }})

                mongo.db.users_shelf.update_one(
                    {"_id": ObjectId(user_shelf_id),
                     "books.targetBookId": target_book_id},
                    {"$set": {"books.$.canceledAt": datetime.now(tz=pytz.UTC),
                              }})

            elif status == 'paused':
                # Set the books as Paused
                updated = mongo.db.users_shelf.update_one(
                    {"_id": ObjectId(user_shelf_id),
                     "books.targetBookId": target_book_id},
                    {"$set": {"books.$.readingInProgress": False,
                              "books.$.readingPaused": True,
                              "books.$.readingCanceled": False,
                              "books.$.readingFinished": False,
                              }})

            elif status == 'reading':
                # Set the books as Reading
                updated = mongo.db.users_shelf.update_one(
                    {"_id": ObjectId(user_shelf_id),
                     "books.targetBookId": target_book_id},
                    {"$set": {"books.$.readingInProgress": True,
                              "books.$.readingPaused": False,
                              "books.$.readingCanceled": False,
                              "books.$.readingFinished": False,
                              }})

                mongo.db.users_shelf.update_one(
                    {"_id": ObjectId(user_shelf_id),
                     "books.targetBookId": target_book_id},
                    {"$set": {"books.$.startedAt": datetime.now(tz=pytz.UTC),
                              }})

            else:
                raise Exception('Status not recognized.')

            if not updated.acknowledged:
                raise Exception('The database have failed to update the information.')

            mongo.db.users_shelf.update_one({'_id': ObjectId(user_shelf_id)},
                                            {'$set': {'lastUpdate': datetime.now(tz=pytz.UTC)}})

            # Prepare the answer back
            self.code = 201
            self.response = [{
                'successOnRequest': True,
                'errorCode': ValidationCodes.SUCCESS,
            }]

        except Exception as e:
            # If something wrong happens, raise an Internal server error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code
