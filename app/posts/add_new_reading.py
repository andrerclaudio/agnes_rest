# Build-in modules
from datetime import datetime
import logging

# Installed modules
import pytz

# Local modules
from app.connectors import mongo

# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


def post_add_new_reading(isbn):
    """
    Add a new reading given a ISBN.
    """

    # Make the default answer
    rsp = {
        'successOnRequest': False,
        'isbn': '',
        'title': ''
    }
    # The code is Ok but a flag with fail will be sent back.
    code = 200

    try:
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
            mongo.db.users_shelf.insert_many(info)
            # Prepare the answer back
            rsp = {
                'successOnRequest': True,
                'isbn': ret[0]['isbn'],
                'title': ret[0]['title']
            }
            # Created
            code = 201

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        return [rsp], code
