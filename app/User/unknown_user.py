# Build-in modules
import logging
# Installed modules
import random

# Local modules
from app.Tools.email import send_email
from app.error_codes import ValidationCodes

# Printing object
logger = logging.getLogger(__name__)

# Maximum value to generate
MAX_RANDOM_VALUE = 999999


class UnknownUser(object):
    """
    Add a new reading given a ISBN.
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
                    # Generate a random code
                    code = str(random.randint(0, MAX_RANDOM_VALUE))
                    # Verify the email
                    if send_email(email, code):

                        # Mount the New User Schema
                        info = [
                            {
                                "userEmail": email,
                                "emailConfirmed": False,
                                "lastCodeSent": code,
                                "attemptsToValidate": 0,
                                "password": "",
                                "userName": "",
                                "userId": "",
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
                        if not added:
                            raise Exception('The database have failed to add the email to user info.')

                        # The email was sent.
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
