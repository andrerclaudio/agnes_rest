# Build-in modules

# Installed modules

# Local modules
from app.connectors import mongo


def query_fetch_book_info(isbn):
    """
    Fetch book information given an ISBN code.
    """

    book_info = {}

    ret = list(mongo.db.library.find({'isbn': isbn}))

    for idx, value in enumerate(ret):
        book_info = {
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

    return [book_info]
