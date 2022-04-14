# Build-in modules
from datetime import datetime

# Installed modules

# Local modules
import pytz

from app.connectors import mongo


def post_add_new_reading(isbn):
    """
    Add a new reading given a ISBN.
    """

    ret = list(mongo.db.library.find({'isbn': isbn}))
    book_id = str(ret[0]['_id'])

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
    }
    ]

    mongo.db.users_shelf.insert_many(info)

    rsp = {
        'isbn': ret[0]['isbn'],
        'title': ret[0]['title']
    }

    return [rsp]
