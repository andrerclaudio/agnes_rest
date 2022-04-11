"""
Dispatcher all ingoing functions.
"""

# Build-in modules
from bson.objectid import ObjectId

# Installed modules
from flask import jsonify, request

# Local modules
from .connectors import mongo


def query_dispatcher():
    """
    Retrieve an information given some parameters.
    /query
    """

    books_shelf = list(mongo.db.users_shelf.find({}))
    book_detail = list(mongo.db.library.find({'_id': ObjectId(books_shelf[0]['_id'])}))

    # Return the raw token string
    values = {}
    for k, v in request.args.items():
        values[k] = v

    # Message to the user
    resp = jsonify([{"readingInProgress": False,
                     "readingCanceled": False,
                     "readingFinished": False,
                     "bookTitle": "",
                     "bookAuthor": "",
                     "bookPublisher": "",
                     "bookIsbn": "",
                     "bookQtyPages": "",
                     "bookCoverLink": ""}
                    ])
    # Sending OK response
    resp.status_code = 200
    # Returning the object
    return resp
