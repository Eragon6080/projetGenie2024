import os

from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse


def sendMail(subject:str, message:str,to_mail=None)->HttpResponse:
    """
    Formulaire permettant d'envoyer une notification sous forme de mail
    :param subject: Sujet du mail
    :param message: message du mail
    :param to_mail: adresse mail du destinataire
    :return: Réponse pour savoir si le mail a été envoyé ou non
    """
    if to_mail is None:
        to_mail = [os.getenv('EMAIL_DEFAULT_RECIPIENT')]
    subject:str = subject
    message:str = message

    if subject and message:
        try:
            send_mail(subject=subject, message=message,from_email=os.getenv('EMAIL_HOST_USER'),recipient_list=to_mail)
        except BadHeaderError:
            return HttpResponse("Invalid header found")
        return HttpResponse("ok")
    else:
        return HttpResponse("Make sur all fields are entered and valid")
