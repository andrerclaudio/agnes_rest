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
        try:
            # Format the email string
            email = str(email).lower().replace(" ", "")
            # Sanity check
            if email.isascii():
                ret = list(mongo.db.users_info.find({'userEmail': email}, {'emailConfirmed', 'userEmail'}))
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
                                "accountActivated": False,
                                "accountBlocked": False,
                                "lastCodeSent": code,
                                "attemptsToValidate": "0",
                                "password": "",
                                "userName": "",
                                "userNickName": "",
                                "userShelfId": "",
                                "lastAccess": "",
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
                        self.code = 201
                        self.response = [{
                            'successOnRequest': True,
                            "errorCode": ValidationCodes.SUCCESS,
                            "userEmail": email,
                            "attemptsToValidate": 0
                        }]

                    else:
                        # Something went wrong with the email.
                        raise Exception('Something went wrong sending the email.')

                else:

                    if ret[0]['emailConfirmed']:

                        self.response = [{
                            'successOnRequest': False,
                            "errorCode": ValidationCodes.EMAIL_HAS_ALREADY_BEEN_ADDED_TO_APPLICATION,
                            "userEmail": "",
                            "attemptsToValidate": 0
                        }]

                    else:

                        # Generate a random code and fill with zeros left
                        code = str(random.randint(0, MAX_RANDOM_VALUE)).rjust(n_digits, '0')
                        # Verify the email
                        if send_email(email, code):

                            # Update the attempts to validate the email
                            updated = mongo.db.users_info.update_one(
                                {"userEmail": ret[0]['userEmail']},
                                {"$set": {'lastCodeSent': code}})

                            if not updated.acknowledged:
                                raise Exception('The database have failed to update the information.')

                            # The email was sent.
                            self.code = 201
                            self.response = [{
                                'successOnRequest': True,
                                "errorCode": ValidationCodes.SUCCESS,
                                "userEmail": email,
                                "attemptsToValidate": 0
                            }]

                        else:
                            # Something went wrong with the email.
                            raise Exception('Something went wrong sending the email.')

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

            ret = list(mongo.db.users_info.find({'userEmail': email}))
            # Check if the email is there
            if len(ret):
                # Fetch some information
                user = ret[0]

                # Add 1 to validation attempts
                attempts = user["attemptsToValidate"]

                # Check if the verification code is checked already
                if not user['emailConfirmed']:
                    # Sanity check
                    if str(verif_code).isdecimal():
                        # Then compare the verification codes
                        if verif_code == user['lastCodeSent']:

                            # Update the attempts to validate the email
                            updated = mongo.db.users_info.update_one(
                                {"userEmail": user['userEmail']},
                                {"$set": {"attemptsToValidate": 0,
                                          "emailConfirmed": True
                                          }})

                            if not updated.acknowledged:
                                raise Exception('The database have failed to update the information.')

                            # The email was sent.
                            self.response = [{
                                'successOnRequest': True,
                                "errorCode": ValidationCodes.SUCCESS,
                                "userEmail": user['userEmail'],
                                "attemptsToValidate": 0
                            }]
                        else:
                            # Update the attempts to validate the email
                            updated = mongo.db.users_info.update_one(
                                {"userEmail": user['userEmail']},
                                {"$set": {"attemptsToValidate": attempts}})

                            if not updated.acknowledged:
                                raise Exception('The database have failed to update the information.')

                            self.response = [{
                                'successOnRequest': False,
                                "errorCode": ValidationCodes.WRONG_VALIDATION_CODE,
                                "userEmail": user['userEmail'],
                                "attemptsToValidate": attempts
                            }]
                    else:
                        self.response = [{
                            'successOnRequest': False,
                            "errorCode": ValidationCodes.WRONG_VALIDATION_CODE,
                            "userEmail": user['userEmail'],
                            "attemptsToValidate": attempts
                        }]
                else:
                    self.response = [{
                        'successOnRequest': False,
                        "errorCode": ValidationCodes.EMAIL_ALREADY_CHECKED,
                        "userEmail": user['userEmail'],
                        "attemptsToValidate": attempts
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

    def create_user(self, password, email, mongo):
        """
        Create the user.
        """
        try:
            ret = list(mongo.db.users_info.find({'userEmail': email}))
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

                        "accountActivated": True,
                        "password": password,
                        "userShelfId": index,
                        "lastAccess": t,
                        "accountCreated": t,

                    }})

                # TODO Make sure the userName is unique
                # TODO What happens if update fails

                # The user was created.
                self.code = 201
                self.response = [{
                    "successOnRequest": True,
                    "errorCode": ValidationCodes.SUCCESS,
                    "lastAccess": int(t.timestamp()),
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
