from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpRequest


class EmailBackend(ModelBackend):
    def authenticate(self, request:HttpRequest, mail:str=None, password:str=None, **kwargs):
        """
        Classe assurant l'authentification en ne passant pas par le modèle de base défini par django
        :param request: Requête http courante
        :param mail: le mail de la personne cherchant à s'authentifier
        :param password: Le mot de passe de la personne cherchant à se connecter
        :param kwargs: Autre argument possible entré en paramètre
        :return: L'utilisateur authentifié si celui-ci existe
        """
        user_model = get_user_model()
        try:
            user = user_model.objects.get(mail=mail)
        except user_model.DoesNotExist:
            return None

        if user.check_password(password):
            return user

    def get_user(self, user_id:int):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
