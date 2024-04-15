from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, TextField, JSONField
from django.db.models.functions import Cast

from .models import Ue, Cours, Personne, Professeur, Etudiant, Sujet, Periode, Etape


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
    return Professeur.objects.all()


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


def get_all_subjects():
    """
    Retourne la liste de tous les sujets
    """
    return Sujet.objects.all()


def get_subject(idue: str):
    """
    Retourne un sujet en particulier
    """
    return Sujet.objects.get(idsujet=idue)


def find_student_by_id_personne(idpersonne):
    """
    Retourne un étudiant en particulier
    """
    try:
        return Etudiant.objects.get(idpersonne=idpersonne)
    except ObjectDoesNotExist:
        return None


def find_professeur_by_id_personne(idpersonne):
    """
    Retourne un professeur en particulier
    """
    try:
        return Professeur.objects.get(idpersonne=idpersonne)
    except ObjectDoesNotExist:
        return None


def find_course_by_student(idpersonne: int):
    """
    Retourne les cours d'un étudiant
    """
    return Cours.objects.get(idetudiant=idpersonne)


def find_course_by_professeur_or_superviseur(idpersonne: int):
    """
    :param idpersonne:
    :return: les cours dont le professeur est responsable
    """
    teacher = Professeur.objects.get(idpersonne=idpersonne)
    ues = Ue.objects.get(idprof=teacher.idprof)
    return Cours.objects.get(idue=ues.idue)


def find_course_for_student_for_subscription(idpersonne):
    """
    :param idpersonne:
    :return:  les cours auquel l'étudiant n'est pas inscrit
    """
    ues = []
    cours = []
    student = Etudiant.objects.get(idpersonne=idpersonne)
    ues_query = get_all_ue()
    for ue in ues_query:
        ues.append(ue)
    cours_query = Cours.objects.filter(idetudiant=student.idetudiant, idue__in=ues)
    if len(cours_query) == 0:
        for ue in ues:
            cours.append(Cours(nom=ue.nom, idue_id=ue.idue))
    else:
        if len(cours_query) < len(ues):
            cours_int = []
            if len(cours_query) >= 1:
                for cour in cours_query:
                    cours_int.append(cour)

                for ue in ues:
                    for cour in cours_int:
                        if cour.idue_id != ue.idue:
                            cours.append(Cours(nom=ue.nom, idue_id=ue.idue))
                print(cours)
                for cour in cours:
                    for cour_int in cours_int:
                        if cour_int.idue_id == cour.idue_id:
                            cours.remove(cour)


    return cours


def find_course_for_student(idpersonne):
    """
    :param idpersonne:
    :return:  les cours auquel l'étudiant est inscrit
    """
    student = Etudiant.objects.get(idpersonne=idpersonne)
    cours = Cours.objects.filter(idetudiant=student.idetudiant)
    print(cours)
    return cours


def get_student(idpersonne):
    # à développer
    """
    :param idpersonne:
    :return: Le délais des échéances pour chaque cours même si l'étudiant n'est pas inscrit
    """
    return Etudiant.objects.get(idpersonne=idpersonne)


def get_delais(idPeriode):
    return Etape.objects.filter(idperiode=idPeriode)


def get_all_subjects_for_a_teacher(idPersonne: int):
    """
    :return: Tous les sujets qui ne sont pas encore réservé
    """
    teacher = Professeur.objects.get(idpersonne=idPersonne)
    return Sujet.objects.filter(idprof=teacher.idprof).exclude(estPris=True)


def get_subject(idsujet: int):
    return Sujet.objects.get(idsujet=idsujet)


def get_people_by_mail(mail: str):
    """
    :return: all people
    """
    return Personne.objects.get(mail=mail)


def get_cours_by_id_sujet_and_id_student(idsujet: int, idstudent: int):
    """
    L'étudiant doit être inscrit au cours pour que l'assignation fonctionne
    :param idsujet: l'id du sujet en cours
    :return: le cours auquel l'étudiant est inscrit
    """
    sujet = Sujet.objects.get(idsujet=idsujet)
    prof = Professeur.objects.get(idprof=sujet.idprof_id)

    ue = Ue.objects.get(idprof=prof.idprof)
    print(ue.idue, idstudent)
    return Cours.objects.get(idue=ue.idue, idetudiant=idstudent)
