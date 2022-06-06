# Build-in modules
import configparser
import json
import logging
import os
import smtplib
import ssl

import requests

# Printing object
logger = logging.getLogger(__name__)


def send_email(destination, code):
    """
    Send the validation email.
    """

    ret = False

    if 'CLOUD' not in os.environ:
        # If the application is running locally, use config.ini anf if not, set environment variables
        config = configparser.ConfigParser()
        config.read_file(open('config.ini'))
        # Sender email and account password
        sender = config['SENDER']['from']
        password = config['SENDER_PASSWORD']['psw']

        try:
            text = "Code:  {}".format(code)
            message = """\
            From: %s
            To: %s
            Subject: %s

            %s
            """ % (sender, destination, 'Agnes', text)
            # TODO Improve the email format. Let it more Readable
            # Log in to server using secure context and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender, password)
                server.sendmail(sender, destination, message)
                logger.debug('Sending email to {}'.format(destination))

            ret = True

        except Exception as e:
            logger.exception(e, exc_info=False)

        finally:
            return ret

    else:
        try:
            url = "https://be.trustifi.com/api/i/v1/email"

            payload = json.dumps({
                "recipients": [
                    {
                        "email": destination,
                    }
                ],
                "title": "Title",
                "html": code
            })
            headers = {
                'x-trustifi-key': os.environ['TRUSTIFI_KEY'],
                'x-trustifi-secret': os.environ['TRUSTIFI_SECRET'],
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            logger.info(response)
            ret = True

        except Exception as e:
            logger.exception(e, exc_info=False)

        finally:
            return ret
