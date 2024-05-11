from django.http import HttpRequest
from django.shortcuts import redirect


def redirect_to_polls(request: HttpRequest) -> HttpRequest:
    """
    La racine redirige automatiquement vers la page de login.
    :param request: La requête courante
    :return: Une redirection vers l'url adéquate
    """
    return redirect("/polls")
