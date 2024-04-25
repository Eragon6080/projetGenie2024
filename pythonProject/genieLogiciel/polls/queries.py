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
    try:
        teacher = Professeur.objects.get(idpersonne=idpersonne)
        ues = Ue.objects.filter(idprof=teacher.idprof)
    except:
        superviseur: Superviseur = Superviseur.objects.get(idpersonne=idpersonne)
        supervisions_query = Supervision.objects.filter(idsuperviseur=superviseur.idsuperviseur)
        supervisionsID = []
        print(supervisions_query)
        for supervision in supervisions_query:
            print(supervision.idue)
            supervisionsID.append(supervision.idue_id)
        ues = Ue.objects.filter(idue__in=supervisionsID)
        print(ues)

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
        print(cours)
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
    try:
        student = Etudiant.objects.get(idpersonne=idpersonne)
        cours = Cours.objects.filter(idetudiant=student.idetudiant)
    except:
        cours = []
        return cours
    return cours


def get_student_by_id_personne(idpersonne: int):
    # à développer
    """
    :param idpersonne:
    :return: Le délais des échéances pour chaque cours même si l'étudiant n'est pas inscrit
    """
    return Etudiant.objects.get(idpersonne=idpersonne)


def get_student_by_id_etudiant(idetudiant: int):
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
    prof: list[Professeur] = Professeur.objects.get(idpersonne=idteacher)
    ues: Ue = Ue.objects.get(idprof=prof.idprof)
    if ues is not None:
        cours_query = Cours.objects.filter(idue=ues)
        cours = []
        for cour in cours_query:
            cours.append(cour)
        if len(cours) > 0:
            students = []
            for cour in cours:
                students_query = Etudiant.objects.filter(idetudiant=cour.idetudiant_id, idsujet=None)
                print(students_query)
                for student in students_query:
                    students.append((int(student.idetudiant), f"{student.idpersonne.nom} {student.idpersonne.prenom}"))
            return students
        return None
    else:
        return None


def get_personne_by_id(idpersonne: int):
    """
    :param idpersonne:
    :return: une personne en particulier
    """
    return Personne.objects.get(idpersonne=idpersonne)


def get_owner_of_ue(ue: Ue):
    """
    :param idue:
    :return: le propriétaire de l'ue
    """
    prof = Professeur.objects.get(idprof=ue.idprof_id)
    return Personne.objects.filter(idpersonne=prof.idpersonne_id)


def get_students_of_ue(ue: Ue):
    """
    :param idue:
    :return: les étudiants participants d'une ue 
    """
    courses = Cours.objects.filter(idue=ue)
    # for cours in courses:
    #     student = Etudiant.objects.get(idetudiant=cours.idetudiant_id)
    #     pers = Personne.objects.get(idpersonne=student.idpersonne_id)
    #     students.append(pers)
    students_query = Etudiant.objects.filter(idetudiant__in=courses)
    personne_students = Personne.objects.filter(etudiant__in=students_query)
    return personne_students


def get_supervisors_of_ue(ue: Ue):
    """
    :param idue:
    :return: les superviseurs d'une ue
    """
    supervisions = Supervision.objects.filter(idue=ue)
    # for supervision in supervisions:
    #     superviseur = Superviseur.objects.get(idsuperviseur=supervision.idsuperviseur_id)
    #     pers = Personne.objects.get(idpersonne=superviseur.idpersonne_id)
    #     supervisors.append(pers)
    supervisors_query = Superviseur.objects.filter(idsuperviseur__in=supervisions)

    personne_supervisors = Personne.objects.filter(superviseur__in=supervisors_query)
    print(personne_supervisors)
    return personne_supervisors


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


def get_prof_by_id_personne(idpersonne: int):
    """
    :param idpersonne:
    :return: le professeur en cours
    """
    return Professeur.objects.get(idpersonne=idpersonne)


def get_superviseur_by_id_personne(idpersonne: int):
    """

    :param idpersonne:
    :return: le superviseur concerné
    """
    return Superviseur.objects.get(idpersonne=idpersonne)


def get_sujets_by_idue(idue: str):
    """
    :param idue:
    :return: tous les sujets qui ne sont pas pris et qui font partie de l'ue concerné
    """
    return Sujet.objects.filter(idue=idue, estpris=False)


def get_subject_by_id(idsujet: int):
    """

    :param idsujet:
    :return: le sujet en question
    """
    return Sujet.objects.get(idsujet=idsujet)


def count_subject_for_one_student_and_one_ue(idetudiant: int, idue: str):
    """
    :param idetudiant:
    :return: le nombre de sujets pour l'étudiant en question
    """
    return len(Sujet.objects.filter(idetudiant=idetudiant, idue=idue))




def is_existing_personne_by_email(email)->bool:
    """

    :param email:
    :return: Un booléen si une personne existe en BD
    """
    try:
        personne = Personne.objects.get(mail=email)
        if personne is not None:
            return True
        else:
            return False
    except:
        return False


def find_course_by_id(idcours: int) -> Cours:
    """
    :param idcours:
    :return: le cours en question
    """
    return Cours.objects.get(idcours=idcours)
def find_sujet_by_id_cours(cours: Cours) -> Sujet | None:
    """
    :param cours:
    :return: le sujet en question
    """
    ue: Ue = cours.idue
    try:
        return Sujet.objects.get(idue=ue.idue)
    except:
        return None


def get_student_by_id_personne(idpersonne: int):
    """
    :param idpersonne:
    :return: l'étudiant en question
    """
    try:
        return Etudiant.objects.get(idpersonne_id=idpersonne)
    except:
        return None
    

def is_user_admin(idpersonne: int):
    """
    :param idpersonne:
    :return: un booléen si l'utilisateur est un admin
    """
    personne = Personne.objects.get(idpersonne=idpersonne)
    if "admin" in personne.role['role']:
        return True
    return False
