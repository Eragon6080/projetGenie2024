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
