# Build-in modules
from bson.objectid import ObjectId
import logging

# Local modules
from app.connectors import mongo

# Printing object
logger = logging.getLogger(__name__)


def query_reading_screen():
    """
    Fetch the active or paused readings.
    """

    # Make the default answer
    rsp = [{
        "successOnRequest": False,
        "readingInProgress": False,
        "readingPaused": False,
        "readingCanceled": False,
        "readingFinished": False,
        "title": "",
        "author": "",
        "publisher": "",
        "isbn": "",
        "pagesQty": "",
        "coverLink": ""
    }]
    # The code is Ok but a flag with fail will be sent back.
    code = 200

    try:
        # Fetch readings in Progress or Paused.
        query = {"$or": [{'readingInProgress': True}, {'readingPaused': True}]}
        query_resp = list(mongo.db.users_shelf.find(query))
        # Check if the query get results
        if len(query_resp) > 0:
            # Fetch those books details by book ID.
            book_details = []
            for idx, value in enumerate(query_resp):
                ret = list(mongo.db.library.find({'_id': ObjectId(value['targetBookId'])}))
                book_details.extend(ret)
            # Make sure a book was found
            if len(book_details) > 0:
                # Prepare the answer back
                rsp.clear()
                for idx, value in enumerate(query_resp):
                    info = {
                        "successOnRequest": True,
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
                    rsp.append(info)
                code = 200
            else:
                raise Exception('The database failed to reply with the book info')

    except Exception as e:
        # If something wrong happens, raise an Internal ser error
        rsp = []
        # Internal server error
        code = 500
        logger.exception(e, exc_info=False)

    finally:
        return rsp, code
