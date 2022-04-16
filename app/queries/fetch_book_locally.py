# Build-in modules
import logging

# Local modules
from app.connectors import mongo
from app.tools.fetch_book_remote import fetch_book_remote

# Printing object
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
                else:
                    rsp["successOnRequest"] = True
                    rsp.update(ret)

    except Exception as e:
        logger.exception(e, exc_info=False)

    finally:
        return [rsp], code
