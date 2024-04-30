from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password


class EmailBackend(ModelBackend):
    def authenticate(self, request, mail=None, password=None, **kwargs):
        user_model = get_user_model()
        print(mail)
        try:
            user = user_model.objects.get(mail=mail)
        except user_model.DoesNotExist:
            return None

        if user.check_password(password):
            return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
