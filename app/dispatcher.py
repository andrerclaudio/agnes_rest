"""
Dispatcher all ingoing queries.
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

    my_query = {"$or": [{'readingInProgress': True}, {'readingPaused': True}]}
    books_shelf = list(mongo.db.users_shelf.find(my_query))
    book_detail = []
    for idx, value in enumerate(books_shelf):
        ret = list(mongo.db.library.find({'_id': ObjectId(value['bookTargetId'])}))
        book_detail.extend(ret)

    # Return the raw token string
    values = {}
    for k, v in request.args.items():
        values[k] = v

    reading_info = []

    for idx, value in enumerate(books_shelf):
        info = {"readingInProgress": value["readingInProgress"],
                "readingPaused": value["readingPaused"],
                "readingCanceled": value["readingCanceled"],
                "readingFinished": value["readingFinished"],
                "bookTitle": book_detail[idx]["bookTitle"],
                "bookAuthor": book_detail[idx]["bookAuthor"],
                "bookPublisher": book_detail[idx]["bookPublisher"],
                "bookIsbn": book_detail[idx]["bookIsbn"],
                "bookQtyPages": book_detail[idx]["bookQtyPages"],
                "bookCoverLink": book_detail[idx]["bookCoverLink"]}

        reading_info.append(info)

    # Message to the user
    resp = jsonify(reading_info)

    # Sending OK response
    resp.status_code = 200
    # Returning the object
    return resp
