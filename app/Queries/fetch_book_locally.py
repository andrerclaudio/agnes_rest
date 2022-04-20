# Build-in modules
import logging

# Local modules
from app.connectors import mongo
from app.Tools.fetch_book_remote import fetch_book_remote
from app.helpers import fix_isbn_format
from app.validation import ValidationMessages


# Printing object
logger = logging.getLogger(__name__)


def query_fetch_book_info(isbn):
    """
    Fetch book information given an ISBN code.
    """

    # Make the default answer
    rsp = {
        "successOnRequest": False,
        "errorCode": ValidationMessages.NO_BOOK_WAS_FOUND_WITH_THE_GIVEN_ISBN_CODE,
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
        # Check the ISBN consistency
        isbn = fix_isbn_format(isbn)
        if isbn:
            # Find the book by ISBN.
            ret = list(mongo.db.library.find({'isbn': isbn}))
            # Make sure query find a book.
            if len(ret) > 0:
                # Prepare the answer back
                for idx, value in enumerate(ret):
                    rsp = {
                        "successOnRequest": True,
                        "errorCode": ValidationMessages.SUCCESS,
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
            else:
                ret = fetch_book_remote(isbn)
                if len(ret) > 0:
                    # Create the new book Schema
                    book = [{
                        "title": ret["title"],
                        "author": ret["author"],
                        "publisher": ret["publisher"],
                        "isbn": ret["isbn"],
                        "pagesQty": ret["pagesQty"],
                        "genres": "",
                        "coverType": "",
                        "coverLink": ret["coverLink"],
                        "favoriteCount": "",
                        "language": "",
                        "publicationDate": "",
                        "similar": [
                            {
                                "bookId": ""
                            }
                        ],
                        "ratingAverage": "0.0",
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
                    }]
                    # Save on Database
                    added = mongo.db.library.insert_many(book)
                    if not added:
                        raise Exception('The database have failed to add the new book to database.')

                    rsp["successOnRequest"] = True
                    rsp["errorCode"] = ValidationMessages.SUCCESS,
                    rsp.update(ret)

    except Exception as e:
        # If something wrong happens, raise an Internal ser error
        rsp = []
        # Internal server error
        code = 500
        logger.exception(e, exc_info=False)

    finally:
        return [rsp], code
