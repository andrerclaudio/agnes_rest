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
# Number of digits to generate
n_digits = 6


class UnknownUser(object):
    """
    New user related methods.
    """

    def __init__(self):
        # Make the default answer
        self.response = []
        self.code = 200

    def validate_email(self, email, mongo):
        """
        Validate the given email.
        """
        try:
            # Format the email string
            email = str(email).lower().replace(" ", "")
            # Basic sanity check
            if email.isascii():
                ret = list(mongo.db.users_info.find({'userEmail': email}, {'emailConfirmed', 'userEmail'}))
                # Check if the email is already in use
                if not len(ret):
                    # It means the email is new to application
                    # Generate a random code and fill if necessary
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
                                "attemptsToValidate": 0,
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

                        # Store the New user schema
                        added = mongo.db.users_info.insert_many(info)
                        if not added.acknowledged:
                            raise Exception('The database have failed to add the email to user info.')

                        # The email was sent.
                        self.code = 201
                        self.response = [{
                            'successOnRequest': True,
                            "errorCode": ValidationCodes.SUCCESS,
                        }]

                    else:
                        # Something went wrong with the email.
                        raise Exception('Something went wrong sending the email.')

                else:
                    # It means the email was already added to application
                    if ret[0]['emailConfirmed']:
                        # The email was confirmed before
                        self.response = [{
                            'successOnRequest': False,
                            "errorCode": ValidationCodes.EMAIL_HAS_ALREADY_BEEN_ADDED_TO_APPLICATION,
                        }]

                    else:
                        # Generate a random code and fill with if necessary
                        code = str(random.randint(0, MAX_RANDOM_VALUE)).rjust(n_digits, '0')
                        # Verify the email
                        if send_email(email, code):
                            # Update the lastCodeSent information
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

    def validate_code(self, code, email, mongo):
        """
        Validate the given code.
        """
        try:
            # Fetch the user information
            ret = list(mongo.db.users_info.find({'userEmail': email}))
            # Check if there is any information
            if len(ret):
                # Prettify
                user = ret[0]
                # Check if the verification code is checked already
                if not user['emailConfirmed']:
                    # Basic sanity check
                    if str(code).isdecimal():
                        # Then compare the verification codes
                        if code == user['lastCodeSent']:
                            # Update the attempts to validate the email
                            updated = mongo.db.users_info.update_one(
                                {"userEmail": user['userEmail']},
                                {"$set": {"emailConfirmed": True}})

                            if not updated.acknowledged:
                                raise Exception('The database have failed to update the information.')

                            # The email was sent.
                            self.response = [{
                                'successOnRequest': True,
                                "errorCode": ValidationCodes.SUCCESS,
                            }]
                        else:
                            self.response = [{
                                'successOnRequest': False,
                                "errorCode": ValidationCodes.WRONG_VALIDATION_CODE,
                            }]
                    else:
                        self.response = [{
                            'successOnRequest': False,
                            "errorCode": ValidationCodes.WRONG_VALIDATION_CODE,
                        }]
                else:
                    self.response = [{
                        'successOnRequest': False,
                        "errorCode": ValidationCodes.EMAIL_ALREADY_CHECKED,
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
            # Fetch the user information
            ret = list(mongo.db.users_info.find({'userEmail': email}))
            # Check if there is any information
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

                user = ret[0]
                user_shelf_id = str(added.inserted_ids[0])
                # Update the new user data
                t = datetime.now(tz=pytz.UTC)

                updated = mongo.db.users_info.update_one(
                    {"userEmail": user['userEmail']},
                    {"$set": {
                        "accountActivated": True,
                        "password": password,
                        "userShelfId": user_shelf_id,
                        "lastAccess": t,
                        "accountCreated": t,
                    }})

                if not updated.acknowledged:
                    raise Exception('The database have failed to update the information.')

                # The user was created.
                self.code = 201
                self.response = [{
                    "successOnRequest": True,
                    "errorCode": ValidationCodes.SUCCESS}]

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
