# Build-in modules
from datetime import datetime
import logging

# Installed modules
import pytz

# Local modules
from app.Queries.reading_screen import query_reading_screen
from app.connectors import mongo
from app.helpers import fix_isbn_format
from app.validation import ValidationMessages

# Printing object
logger = logging.getLogger(__name__)


def post_add_new_reading(isbn):
    """
    Add a new reading given a ISBN.
    """

    # Make the default answer
    rsp = {
        'successOnRequest': False,
        "errorCode": ValidationMessages.BOOK_HAS_ALREADY_BEEN_ADDED_TO_THE_BOOK_SHELF,
        'isbn': '',
        'title': ''
    }
    # The code is Ok but a flag with fail will be sent back.
    code = 200

    try:
        # Check the ISBN consistency
        isbn = fix_isbn_format(isbn)
        if isbn:
            # Check whether the given Isbn is already active (Reading ou Paused) or not.
            active_books, _ = query_reading_screen()
            if isbn not in [active_isbn['isbn'] for active_isbn in active_books]:
                # Find the book by ISBN.
                ret = list(mongo.db.library.find({'isbn': isbn}))
                # Make sure if a book was fetched
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
                    rsp = {
                        'successOnRequest': True,
                        "errorCode": ValidationMessages.SUCCESS,
                        'isbn': ret[0]['isbn'],
                        'title': ret[0]['title']
                    }
                    # Created
                    code = 201

    except Exception as e:
        # If something wrong happens, raise an Internal ser error
        rsp = []
        # Internal server error
        code = 500
        logger.exception(e, exc_info=False)

    finally:
        return [rsp], code
