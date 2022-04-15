# Build-in modules
import logging

# Local modules
from app.connectors import mongo

# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


def query_fetch_book_info(isbn):
    """
    Fetch book information given an ISBN code.
    """

    # Make the default answer
    rsp = {
        "successOnRequest": False,
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
    # The code is Ok but a flag with fail will be sent back.
    code = 200

    try:
        # Find the book by ISBN.
        ret = list(mongo.db.library.find({'isbn': isbn}))
        # Make sure query find a book.
        if len(ret) > 0:
            # Prepare the answer back
            for idx, value in enumerate(ret):
                rsp = {
                    "successOnRequest": True,
                    "title": ret[idx]["title"],
                    "author": ret[idx]["author"],
                    "publisher": ret[idx]["publisher"],
                    "isbn": ret[idx]["isbn"],
                    "pagesQty": ret[idx]["pagesQty"],
                    "genres": ret[idx]["genres"],
                    "coverType": ret[idx]["coverType"],
                    "coverLink": ret[idx]["coverLink"],
                    "ratingAverage": ret[idx]["ratingAverage"]
                }
            # Ok
            code = 200

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        return [rsp], code
