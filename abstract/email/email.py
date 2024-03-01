import smtplib, ssl
from django.core.mail import EmailMessage
from django.conf import settings
import os


class Email(object):

    def __init__(self, subject: str, message: str, to: str) -> None:

        self.message = message
        self.subject = subject
        self.to = to
        self.from_email = settings.DEFAULT_FROM_EMAIL

    def send(self):

        mail = EmailMessage(self.subject, self.message, self.from_email, [self.to])
        mail.content_subtype = "html"

        try:
            mail.send()
            
        except Exception as e:
            print(str(e))
        