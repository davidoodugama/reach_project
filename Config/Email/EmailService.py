"""
# EMAIL SERVICE
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jul-15
"""


from Const.const import SOURCE_EMAIL, GMAIL_AUTHENTICATION_PIN, EMAIL_ERROR_LOG, EMAIL, EMAIL_LOG
from email.message import EmailMessage
import ssl
import smtplib
from Config.Logger.Logger import Logger
from flask import jsonify

class EmailService:
    def __init__(self, message, subject, destination_address):
        try:
            self.debug = Logger()
            self.username = SOURCE_EMAIL
            self.password = GMAIL_AUTHENTICATION_PIN
            self.message = message
            self.destination_address = destination_address
            self.subject = subject
            self.em = EmailMessage()
            self.context = ssl.create_default_context()
            self.__sendEmail__()

        except Exception as e:
            self.debug = Logger()
            self.debug.error_log(EMAIL_ERROR_LOG, e, EMAIL)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
    
    def __sendEmail__(self):
        try:
            self.em["From"] = self.username
            self.em["To"] = self.destination_address
            self.em["Subject"] = self.subject
            self.em.set_content(self.message)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = self.context) as smtp: # SENDING EMAIL
                smtp.login(self.username, self.password)
                smtp.sendmail(self.username, self.destination_address, self.em.as_string())

            self.debug.debug(EMAIL, EMAIL_LOG, "Email successfully sent to " + str(self.destination_address)) 

        except Exception as e:
            self.debug = Logger()
            self.debug.error_log(EMAIL_ERROR_LOG, e, EMAIL)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })


