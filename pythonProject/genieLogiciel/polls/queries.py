from .models import Ue, Cours


async def get_all_ue():
    """
    Retourne toutes les UE
    """
    return await Ue.objects.all()


def get_all_course():
    """
    Retourne une UE
    """
    return Cours.objects.all()


def get_roles_user(idpersonne):
    """
    Retourne une liste des rôles d'une personne
    """
    pass 

def get_topics_course(idcours):
    """
    Retourne une liste des sujets lié à un cours spécifique
    """
    pass
