from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, TextField, JSONField
from django.db.models.functions import Cast

from .models import Ue, Cours, Personne, Professeur, Etudiant, Sujet, Periode, Etape, Superviseur, Supervision


def get_all_ue():
    """
    Retourne toutes les UE
    """
    return Ue.objects.all()

def get_ue(idue):
    """
    Retourne une UE
    """
    return Ue.objects.get(idue=idue)


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


def find_courses_by_professeur(idpersonne: int):
    """
    :param idpersonne:
    :return: les cours dont le professeur est responsable
    """
    teacher = Professeur.objects.get(idpersonne=idpersonne)
    ues = Ue.objects.filter(idprof=teacher.idprof)
    return ues

def find_courses_by_supervisor(idpersonne: int):
    """
    :param idpersonne:
    :return: les cours dont le professeur est responsable
    """
    sup = Superviseur.objects.get(idpersonne=idpersonne)
    supervisions = Supervision.objects.filter(idsuperviseur=sup.idsuperviseur)
    ues = []
    for supervision in supervisions:
        ues.append(Ue.objects.get(idue=supervision.idue_id))
    return ues


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
    return cours


def get_student_by_id_personne(idpersonne:int):
    # à développer
    """
    :param idpersonne:
    :return: Le délais des échéances pour chaque cours même si l'étudiant n'est pas inscrit
    """
    return Etudiant.objects.get(idpersonne=idpersonne)

def get_student_by_id_etudiant(idetudiant:int):
    """

    :param idetudiant:
    :return: l'étudiant en question
    """
    return Etudiant.objects.get(idetudiant=idetudiant)



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
    return Cours.objects.get(idue=ue.idue, idetudiant=idstudent)


def get_students_by_teacher_without_subject(idteacher: int):
    """
    :param idstudent:
    :param idteacher:
    :param idsujet:
    :return: les étudiant appartenant à un cours donné par un prof
    """
    prof:list[Professeur] = Professeur.objects.get(idpersonne=idteacher)
    ues:Ue = Ue.objects.get(idprof=prof.idprof)
    if ues is not None:
        cours_query = Cours.objects.filter(idue=ues)
        cours = []
        for cour in cours_query:
            cours.append(cour)
        if len(cours) > 0:
            students = []
            for cour in cours:
                students_query = Etudiant.objects.filter(idetudiant=cour.idetudiant_id,idsujet=None)
                print(students_query)
                for student in students_query:
                    students.append((int(student.idetudiant),f"{student.idpersonne.nom} {student.idpersonne.prenom}"))
            return students
        return None
    else:
        return None
    
def get_personne_by_id(idpersonne:int):
    """
    :param idpersonne:
    :return: une personne en particulier
    """
    return Personne.objects.get(idpersonne=idpersonne)

def get_owner_of_ue(ue:Ue):
    """
    :param idue:
    :return: le propriétaire de l'ue
    """
    prof = Professeur.objects.get(idprof=ue.idprof_id)
    return Personne.objects.get(idpersonne=prof.idpersonne_id)

def get_students_of_ue(ue:Ue):
    """
    :param idue:
    :return: les étudinats participants d'une ue 
    """
    courses = Cours.objects.filter(idue=ue)
    students = []
    for cours in courses:
        student = Etudiant.objects.get(idetudiant=cours.idetudiant_id)
        pers = Personne.objects.get(idpersonne=student.idpersonne_id)
        students.append(pers)
    return students

def get_supervisors_of_ue(ue:Ue):
    """
    :param idue:
    :return: les superviseurs d'une ue
    """
    supervisions = Supervision.objects.filter(idue=ue)
    supervisors = []
    for supervision in supervisions:
        superviseur = Superviseur.objects.get(idsuperviseur=supervision.idsuperviseur_id)
        pers = Personne.objects.get(idpersonne=superviseur.idpersonne_id)
        supervisors.append(pers)
    return supervisors


def get_subject_for_a_superviseur(idpersonne):
    """
    :param idpersonne:
    :return: les sujets pour un superviseur donné
    """
    superviseur = Supervision.objects.get(idpersonne=idpersonne)
    sujets_query = Sujet.objects.filter(idsuperviseur=superviseur.idsuperviseur)
    sujets = []
    for sujet in sujets_query:
        sujets.append(sujet)
    return sujets


