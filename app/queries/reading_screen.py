# Build-in modules
from bson.objectid import ObjectId

# Installed modules

# Local modules
from app.connectors import mongo


def query_reading_screen():
    """
    Fetch the active or paused readings.
    """

    reading_details = []
    book_details = []

    query = {"$or": [{'readingInProgress': True}, {'readingPaused': True}]}
    query_resp = list(mongo.db.users_shelf.find(query))

    for idx, value in enumerate(query_resp):
        ret = list(mongo.db.library.find({'_id': ObjectId(value['targetBookId'])}))
        book_details.extend(ret)

    for idx, value in enumerate(query_resp):
        info = {
            "readingInProgress": value["readingInProgress"],
            "readingPaused": value["readingPaused"],
            "readingCanceled": value["readingCanceled"],
            "readingFinished": value["readingFinished"],
            "title": book_details[idx]["title"],
            "author": book_details[idx]["author"],
            "publisher": book_details[idx]["publisher"],
            "isbn": book_details[idx]["isbn"],
            "pagesQty": book_details[idx]["pagesQty"],
            "coverLink": book_details[idx]["coverLink"]
        }

        reading_details.append(info)

    return reading_details
