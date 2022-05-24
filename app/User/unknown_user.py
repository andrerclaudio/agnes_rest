# Build-in modules
import logging
import random
from datetime import datetime

# Installed modules
import pytz

# Local modules
from app.Tools.email import send_email
from app.error_codes import ValidationCodes

# Printing object
logger = logging.getLogger(__name__)

# Maximum value to generate
MAX_RANDOM_VALUE = 999999
n_digits = 6


class UnknownUser(object):
    """
    New user related methods.
    """

    def __init__(self):
        # Make the default answer
        self.response = []
        # The code is Ok but more details is in self.response
        self.code = 200

    def validate_email(self, email, mongo):
        """
        Validate the given email.
        """

        # Make the default answer
        self.response = [{
            'successOnRequest': False,
            "errorCode": ValidationCodes.EMAIL_HAS_ALREADY_BEEN_ADDED_TO_APPLICATION,
            "userEmail": "",
            "attemptsToValidate": "0"
        }]

        try:
            # Format the email string
            email = str(email).lower().replace(" ", "")
            # Sanity check
            if email.isascii():

                query = {'userEmail': email}
                ret = list(mongo.db.users_info.find(query))
                # Check if the email is already in use
                if not len(ret):
                    # Generate a random code and fill with zeros left
                    code = str(random.randint(0, MAX_RANDOM_VALUE)).rjust(n_digits, '0')
                    # Verify the email
                    if send_email(email, code):

                        # Mount the New User Schema
                        info = [
                            {
                                "userEmail": email,
                                "emailConfirmed": False,
                                "lastCodeSent": code,
                                "attemptsToValidate": "0",
                                "password": "",
                                "userName": "",
                                "userNickName": "",
                                "userShelfId": "",
                                "lastLogin": "",
                                "accountCreated": "",
                                "gender": "",
                                "birthDate": "",
                                "mobileNumber": "",
                                "booksPreferences": [],
                            }
                        ]

                        # Store the New user schema on the user info.
                        added = mongo.db.users_info.insert_many(info)
                        if not added.acknowledged:
                            raise Exception('The database have failed to add the email to user info.')

                        # The email was sent.
                        self.response = [{
                            'successOnRequest': True,
                            "errorCode": ValidationCodes.SUCCESS,
                            "userEmail": email,
                            "attemptsToValidate": "0"
                        }]

                    else:
                        # Something went wrong with the email.
                        raise Exception('Something went wrong sending the email.')
                else:
                    user = ret[0]
                    if not user["emailConfirmed"]:
                        attempts = str(int(user["attemptsToValidate"]) + 1)
                        self.response = [{
                            'successOnRequest': False,
                            "errorCode": ValidationCodes.EMAIL_NOT_CONFIRMED,
                            "userEmail": email,
                            "attemptsToValidate": attempts
                        }]

                        mongo.db.users_info.update_one(
                            {"userEmail": user['userEmail']},
                            {"$set": {"attemptsToValidate": attempts}})

                        # TODO What happens if update fails

            else:
                raise Exception('Invalid email format.')

        except Exception as e:
            # If something wrong happens, raise an Internal server error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code

    def validate_code(self, verif_code, email, mongo):
        """
        Validate the given code.
        """

        try:
            query = {'userEmail': email}
            ret = list(mongo.db.users_info.find(query))
            # Check if the email is there
            if len(ret):
                # Fetch some information
                user = ret[0]
                attempts = str(int(user["attemptsToValidate"]) + 1)

                self.response = [{
                    'successOnRequest': False,
                    "errorCode": ValidationCodes.WRONG_VALIDATION_CODE,
                    "userEmail": user['userEmail'],
                    "attemptsToValidate": attempts
                }]

                # Sanity check
                if str(verif_code).isdigit():
                    # Then compare the codes
                    if verif_code == user['lastCodeSent']:
                        # The email was sent.
                        self.response = [{
                            'successOnRequest': True,
                            "errorCode": ValidationCodes.SUCCESS,
                            "userEmail": user['userEmail'],
                            "attemptsToValidate": "0"
                        }]
                        attempts = "0"

                    # Update the attempts to validate the email
                    mongo.db.users_info.update_one(
                        {"userEmail": user['userEmail']},
                        {"$set": {"attemptsToValidate": attempts}})

                    # TODO What happens if update fails
            else:
                # Something went wrong with the email.
                raise Exception('Something went wrong with the stored email.')

        except Exception as e:
            # If something wrong happens, raise an Internal server error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code

    def create_user(self, form, email, mongo):
        """
        Create the user.
        """

        try:
            query = {'userEmail': email}
            ret = list(mongo.db.users_info.find(query))
            # Check if the email is there
            if len(ret):
                # Mount the New User Shelf Schema
                info = [
                    {
                        "shelfName": "",
                        "lastUpdate": "",
                        "booksQty": 0,
                        "description": "",
                        "books": [],
                    }
                ]
                # Store the New user schema on the user info.
                added = mongo.db.users_shelf.insert_many(info)
                if not added.acknowledged:
                    raise Exception('The database have failed to create the new schema.')

                # Fetch some information
                user = ret[0]
                index = str(added.inserted_ids[0])
                # Generate the new user data
                t = datetime.now(tz=pytz.UTC)
                mongo.db.users_info.update_one(
                    {"userEmail": user['userEmail']},
                    {"$set": {

                        "emailConfirmed": True,
                        "password": form['password'],
                        "userName": form['userName'],
                        "userNickName": "",
                        "userShelfId": index,
                        "lastLogin": t,
                        "accountCreated": t,

                    }})

                # TODO What happens if update fails

                # The user was created.
                self.code = 201
                self.response = [{
                    "successOnRequest": True,
                    "errorCode": ValidationCodes.SUCCESS,
                    "token": "",
                    "userId": str(user['_id']),
                }]

            else:
                # Something went wrong with the email.
                raise Exception('Something went wrong with the stored email.')

        except Exception as e:
            # If something wrong happens, raise an Internal server error
            self.response = []
            # Internal server error
            self.code = 500
            logger.exception(e, exc_info=False)

        finally:
            return self.response, self.code
