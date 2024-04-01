from django.db.models import Q, TextField, JSONField
from django.db.models.functions import Cast

from .models import Ue, Cours, Personne, Professeur, Etudiant


def get_all_ue():
    """
    Retourne toutes les UE
    """
    return Ue.objects.all()


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



def get_Professeur_People():
    """
        Retourne une liste des professeurs
    """
    return  Professeur.objects.all()



def get_All_People():
    """
        Retourne une liste des personnes
    """
    return Personne.objects.all()

def get_Etudiant_People():
    """
        Retourne une liste des étudiants
    """
    return Etudiant.objects.all()