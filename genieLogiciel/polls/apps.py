from django.apps import AppConfig


class PollsConfig(AppConfig):
    """
    Définis le nom de l'application au sein de django
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
