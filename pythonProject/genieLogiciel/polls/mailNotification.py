import os

from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse


def sendMail(subject, message,to_mail=None):
    if to_mail is None:
        to_mail = [os.getenv('EMAIL_DEFAULT_RECIPIENT')]
    subject = subject
    message = message

    if subject and message:
        try:
            send_mail(subject=subject, message=message,from_email="pimsprojet@outlook.com",recipient_list=to_mail)
        except BadHeaderError:
            return HttpResponse("Invalid header found")
        return HttpResponse("ok")
    else:
        return HttpResponse("Make sur all fields are entered and valid")
