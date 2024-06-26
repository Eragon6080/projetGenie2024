from typing import List, Tuple, Any

from django.core.exceptions import ObjectDoesNotExist

from .models import Ue, Cours, Personne, Professeur, Etudiant, Sujet, Periode, Etape, Superviseur, Supervision, \
    SelectionSujet, EtapeUe, Delivrable


def find_all_ue() -> list[Ue] | None:
    """
    Retourne toutes les UE
    """
    try:
        return Ue.objects.all()
    except ObjectDoesNotExist:
        return None


def find_ue(idue: str) -> Ue | None:
    """
    Retourne une UE
    """
    try:
        return Ue.objects.get(idue=idue)
    except ObjectDoesNotExist:
        return None


def find_all_course() -> list[Cours] | None:
    """
    Retourne une UE
    """
    try:
        return Cours.objects.all()
    except ObjectDoesNotExist:
        return None


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


def find_Professeur_People() -> list[Professeur] | None:
    """
        Retourne une liste des professeurs
    """
    try:
        return Professeur.objects.all()
    except ObjectDoesNotExist:
        return None


def find_all_People() -> list[Personne] | None:
    """
        Retourne une liste des personnes
    """
    try:
        return Personne.objects.all()
    except ObjectDoesNotExist:
        return None


def find_etudiant_People() -> list[Etudiant] | None:
    """
        Retourne une liste des étudiants
    """
    try:
        return Etudiant.objects.all()
    except ObjectDoesNotExist:
        return None


def find_etape_by_id(idetape: int) -> Etape | None:
    """
    Retourne une étape
    """
    try:
        return Etape.objects.get(idetape=idetape)
    except ObjectDoesNotExist:
        return None


def find_etapeue_by_idetape_and_ue(idetape: int, idue: str) -> EtapeUe | None:
    """
    Retourne l'étape ue
    """
    try:
        return EtapeUe.objects.get(idetape_id=idetape, idue_id=idue)
    except ObjectDoesNotExist:
        return None


def find_student_by_id_personne(idpersonne: int) -> Etudiant | None:
    """
    Retourne un étudiant en particulier
    """
    try:
        return Etudiant.objects.get(idpersonne_id=idpersonne)
    except ObjectDoesNotExist:
        return None


def find_professeur_by_id_personne(idpersonne: int) -> Professeur | None:
    """
    Retourne un professeur en particulier
    """
    try:
        return Professeur.objects.get(idpersonne_id=idpersonne)
    except ObjectDoesNotExist:
        return None


def find_course_by_student(idpersonne: int) -> list[Cours] | None:
    """
    Retourne les cours d'un étudiant
    """
    try:
        courses = []
        etudiant = get_student_by_id_personne(idpersonne)
        courses_query = Cours.objects.filter(idetudiant_id=etudiant)
        for course in courses_query:
            courses.append(course)
        return courses
    except ObjectDoesNotExist:
        return None


def find_courses_by_professeur(idpersonne: int) -> list[Ue] | None:
    """
    :param idpersonne:
    :return: les cours dont le professeur est responsable
    """
    ues = []
    try:
        teacher = Professeur.objects.get(idpersonne_id=idpersonne)
        ues = Ue.objects.filter(idprof_id=teacher.idprof)
    except ObjectDoesNotExist:
        superviseur: Superviseur = Superviseur.objects.get(idpersonne_id=idpersonne)
        supervisions_query = Supervision.objects.filter(idsuperviseur_id=superviseur.idsuperviseur)
        supervisionsID = []
        for supervision in supervisions_query:
            supervisionsID.append(supervision.idue_id)
        ues = Ue.objects.filter(idue__in=supervisionsID)
    finally:
        return ues


def find_courses_by_supervisor(idpersonne: int) -> list[Ue] | None:
    """
    :param idpersonne:
    :return: les cours dont le professeur est responsable
    """
    try:
        sup = Superviseur.objects.get(idpersonne=idpersonne)
        supervisions = Supervision.objects.filter(idsuperviseur=sup.idsuperviseur)
        ues = []
        for supervision in supervisions:
            ues.append(Ue.objects.get(idue=supervision.idue_id))
        return ues
    except ObjectDoesNotExist:
        return None


def find_course_for_student_for_subscription(idpersonne: int) -> list[Cours] | None:
    """
    :param idpersonne:
    :return:  les cours auquel l'étudiant n'est pas inscrit
    """
    try:
        ues = []
        cours = []
        student = Etudiant.objects.get(idpersonne=idpersonne)
        ues_query = find_all_ue()
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
    except ObjectDoesNotExist:
        return None


def find_course_for_student(idpersonne: int) -> list[Cours] | None:
    """
    :param idpersonne:
    :return:  les cours auquels l'étudiant est inscrit
    """
    try:
        student = Etudiant.objects.get(idpersonne_id=idpersonne)
        cours = Cours.objects.filter(idetudiant_id=student.idetudiant)
    except:
        cours = []
        return cours
    return cours


def get_student_by_id_personne(idpersonne: int):
    # à développer
    """
    :param idpersonne:
    :return: l'étudiant en question
    """
    return Etudiant.objects.get(idpersonne_id=idpersonne)


def find_student_by_id_etudiant(idetudiant: int):
    """

    :param idetudiant:
    :return: l'étudiant en question
    """
    return Etudiant.objects.get(idetudiant=idetudiant)


def find_delais_by_sujet(sujet: Sujet) -> list[Etape]:
    if sujet is not None:
        return Etape.objects.filter(idperiode=sujet.idperiode)
    else:
        return []


def find_all_subjects_for_a_teacher(id_personne: int) -> list[Sujet] | None:
    """
    :return: Tous les sujets qui ne sont pas encore réservés
    """
    teacher = Professeur.objects.get(idpersonne_id=id_personne)
    return Sujet.objects.filter(idprof_id=teacher.idprof).exclude(estpris=True)


def find_sujet_by_id(idsujet: int) -> Sujet | None:
    try:
        return Sujet.objects.get(idsujet=idsujet)
    except ObjectDoesNotExist:
        return None


def find_people_by_mail(mail: str) -> Personne | None:
    """
    :return: all people
    """
    try:
        return Personne.objects.get(mail=mail)
    except ObjectDoesNotExist:
        return None


def find_cours_by_id_sujet_and_id_student(idsujet: int, idstudent: int) -> Cours | None:
    """
    L'étudiant doit être inscrit au cours pour que l'assignation fonctionne
    :param idstudent:
    :param idsujet: l'id du sujet en cours
    :return: le cours auquel l'étudiant est inscrit
    """
    try:
        sujet = Sujet.objects.get(idsujet=idsujet)
        prof = Professeur.objects.get(idprof=sujet.idprof_id)

        ue = Ue.objects.get(idprof_id=prof.idprof)
        return Cours.objects.get(idue_id=ue.idue, idetudiant_id=idstudent)
    except ObjectDoesNotExist:
        return None


def find_students_without_subjects_by_teacher(idpersonne: int) -> list[tuple[int, str]] | None:
    """
    :param idpersonne:
    :return:
    """
    try:

        students = find_students_by_teacher_without_subject(idpersonne)
        if students is not None:
            idstudents = []
            for student in students:
                idstudents.append(student[0])
            selections = []
            selections_query = SelectionSujet.objects.all().distinct()
            for selection in selections_query:
                selections.append(selection.idetudiant_id)
            newstudents = []
            new_students_query = Etudiant.objects.filter(idetudiant__in=idstudents).exclude(idetudiant__in=selections)
            for student in new_students_query:
                newstudents.append((int(student.idetudiant), f"{student.idpersonne.nom} {student.idpersonne.prenom}"))
            return newstudents

    except ObjectDoesNotExist:
        return None


def find_students_by_teacher_without_subject(idpersonne: int) -> list[tuple[int, str]] | None:
    """
    :param idpersonne:
    :param idstudent:
    :param idsujet:
    :return: les étudiants appartenant à un cours donné par un prof
    """
    try:
        prof: Professeur = Professeur.objects.get(idpersonne_id=idpersonne)
        ues: Ue = Ue.objects.get(idprof=prof.idprof)
        if ues is not None:
            cours_query = Cours.objects.filter(idue=ues)
            cours = []
            for cour in cours_query:
                cours.append(cour)
            if len(cours) > 0:
                students = []
                for cour in cours:
                    students_query = Etudiant.objects.filter(idetudiant=cour.idetudiant_id)
                    for student in students_query:
                        students.append(
                            (int(student.idetudiant), f"{student.idpersonne.nom} {student.idpersonne.prenom}"))
                return students
            return None
        else:
            return None
    except ObjectDoesNotExist:
        return None


def find_personne_by_id(idpersonne: int) -> Personne | None:
    """
    :param idpersonne:
    :return: une personne en particulier
    """
    try:
        return Personne.objects.get(idpersonne=idpersonne)
    except ObjectDoesNotExist:
        return None


def find_owner_of_ue(ue: Ue) -> Personne | None:
    """
    :param idue:
    :return: le propriétaire de l'ue
    """
    try:
        prof = Professeur.objects.get(idprof=ue.idprof_id)
        return Personne.objects.get(idpersonne=prof.idpersonne_id)
    except ObjectDoesNotExist:
        return None


def find_students_of_ue(ue: Ue) -> list[Personne] | None:
    """
    :param ue:
    :param idue:
    :return: les étudiants participants d'une ue 
    """
    try:
        courses = Cours.objects.filter(idue=ue)
        students_query = Etudiant.objects.filter(idetudiant__in=courses.values('idetudiant'))

        students_id = []
        for student in students_query:
            students_id.append(student.idpersonne_id)
        personne_query = Personne.objects.filter(idpersonne__in=students_id)

        return personne_query
    except ObjectDoesNotExist:
        return None


def find_supervisors_of_ue(ue: Ue) -> list[Personne] | None:
    """
    :param ue:
    :param idue:
    :return: les superviseurs d'une ue
    """
    try:
        supervisions = Supervision.objects.filter(idue=ue)
        supervisors_query = Superviseur.objects.filter(idsuperviseur__in=supervisions.values('idsuperviseur'))
        personne_query = Personne.objects.filter(superviseur__in=supervisors_query)
        return personne_query
    except ObjectDoesNotExist:
        return None


def find_subject_for_a_superviseur(idpersonne: int,year:Periode) -> list[Sujet] | None:
    """
    :param idpersonne:
    :return: les sujets pour un superviseur donné
    """
    try:
        superviseur = Supervision.objects.get(idpersonne_id=idpersonne)
        sujets_query = Sujet.objects.filter(idsuperviseur_id=superviseur.idsuperviseur,idperiode=year)
        sujets = []
        for sujet in sujets_query:
            sujets.append(sujet)
        return sujets
    except ObjectDoesNotExist:
        return None


def find_prof_by_id_personne(idpersonne: int) -> Professeur | None:
    """
    :param idpersonne:
    :return: le professeur en cours
    """
    try:
        return Professeur.objects.get(idpersonne_id=idpersonne)
    except ObjectDoesNotExist:
        return None


def find_superviseur_by_id_personne(idpersonne: int) -> Superviseur | None:
    """

    :param idpersonne:
    :return: le superviseur concerné
    """
    try:
        return Superviseur.objects.get(idpersonne_id=idpersonne)
    except ObjectDoesNotExist:
        return None


def find_sujets_by_idue(idue: str) -> list[Sujet] | None:
    """
    :rtype: object
    :param idue:
    :return: tous les sujets qui ne sont pas pris et qui font partie de l'ue concerné
    """
    try:
        return Sujet.objects.filter(idue=idue, estpris=False)
    except ObjectDoesNotExist:
        return None


def get_subject_by_id(idsujet: int) -> Sujet | None:
    """

    :param idsujet:
    :return: le sujet en question
    """
    try:
        return Sujet.objects.get(idsujet=idsujet)
    except ObjectDoesNotExist:
        return None


def count_subject_for_one_student_and_one_ue(idetudiant: int, idue: str) -> int:
    """
    :param idue:
    :param idetudiant:
    :return: le nombre de sujets pour l'étudiant en question
    """
    try:
        return SelectionSujet.objects.filter(idetudiant_id=idetudiant, idsujet__idue_id=idue).count()
    except ObjectDoesNotExist:
        return 0


def count_selection_for_one_subject(idsujet: int) -> int:
    """
    :param idsujet:
    :return: le nombre de sujets pour l'étudiant en question
    """
    try:
        return SelectionSujet.objects.filter(idsujet_id=idsujet).count()
    except ObjectDoesNotExist:
        return 0


def is_existing_personne_by_email(email: str) -> bool:
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


def find_student_by_id_personne(idpersonne: int) -> Etudiant | None:
    """
    :param idpersonne:
    :return: l'étudiant en question
    """
    try:
        return Etudiant.objects.get(idpersonne_id=idpersonne)
    except:
        return None


def find_sujet_by_id_etudiant(etudiant: Etudiant) -> list[Sujet] | None:
    """
    :param etudiant:
    :return: le sujet en question
    """
    try:
        sujets = []
        selections_query = SelectionSujet.objects.filter(idetudiant=etudiant)
        for selection in selections_query:
            sujets.append(selection.idsujet)
        return sujets
    except:
        return None


def find_sujets_of_student_of_ue(idetudiant, idue) -> list[Sujet] | None:
    """
    :param idue: l'ue en question
    :param idetudiant: l'étudiant en question
    :return: les sujets d'un étudiant pour une ue donnée
    """
    try:
        sujets_of_ue = Sujet.objects.filter(idue=idue)
        selections_query = SelectionSujet.objects.filter(idetudiant=idetudiant, idsujet__in=sujets_of_ue.values('idsujet'))
        sujets = []
        for selection in selections_query:
            sujets.append(selection.idsujet)
        return sujets
    except:
        return None


def is_user_admin(idpersonne: int) -> bool:
    """
    :param idpersonne:
    :return: un booléen si la personne est un admin
    """
    try:
        personne = Personne.objects.get(idpersonne=idpersonne)
        return "admin" in personne.role['role']
    except:
        return False


def find_periode_by_id(idperiode: int) -> Periode | None:
    """
    :param idperiode:
    :return: la période en question
    """
    try:
        periode = Periode.objects.get(idperiode=idperiode)
        return periode
    except:
        return None


def find_periode_by_year(year: int) -> Periode | None:
    """
    :param year:
    :return: la période en relation avec l'année donnée
    """
    try:
        periode = Periode.objects.get(annee=year)
        return periode
    except:
        return None


def find_delivrable_by_type(fichierType: str) -> Delivrable | None:
    """
    :param fichierType:
    :return: le type de délivrable en question
    """
    try:
        delivrable = Delivrable.objects.get(typefichier=fichierType)
        return delivrable
    except:
        return None


def nb_people_keeping_for_a_sujet(sujet: Sujet) -> int:
    """
    :param sujet:
    :return: le nombre de personnes qui ont choisi ce sujet
    """
    try:
        return sujet.nbpersonnes - SelectionSujet.objects.filter(idsujet=sujet).count()
    except ObjectDoesNotExist:
        return -1


def find_selection_by_id_sujet(sujet: Sujet) -> list[SelectionSujet] | None:
    """
    :param sujet:
    :return: la liste des assignations entre un sujet et un étudiant pour un sujet donné
    """
    try:
        selections = []
        selections_query = SelectionSujet.objects.filter(idsujet=sujet)
        for selection in selections_query:
            selections.append(selection)
        return selections
    except ObjectDoesNotExist:
        return None


def find_etapes_of_ue(ue: Ue) -> tuple[Etape, EtapeUe] | None:
    """
    :param ue:
    :return: les étapes d'une ue (dans l'ordre croissant de date de fin)
    """
    try:
        etapesUe_query = EtapeUe.objects.filter(idue=ue)
        etapes = Etape.objects.filter(idetape__in=etapesUe_query.values('idetape')).order_by('datefin')
        return etapes, etapesUe_query.order_by('idetape__datefin')
    except ObjectDoesNotExist:
        return None


def find_current_etape_of_ue(ue: Ue) -> Etape | None:
    """
    :param ue:
    :return: l'étape en cours d'une ue
    """
    try:
        etapesUe_query = EtapeUe.objects.filter(idue=ue, etapecourante=True)
        assert etapesUe_query.count() == 1
        etape = Etape.objects.get(idetape=etapesUe_query[0].idetape_id)
        return etape
    except ObjectDoesNotExist:
        return None


def find_selection_by_id_etudiant(idetudiant: int) -> list[SelectionSujet] | None:
    """
    :param idetudiant:
    :return: la sélection d'un étudiant
    """
    try:
        selections = []
        selections_query = SelectionSujet.objects.filter(idetudiant_id=idetudiant)
        for selection in selections_query:
            selections.append(selection)
        return selections
    except ObjectDoesNotExist:
        return None

def find_periode_by_year(year:int)->Periode|None:
    """

    :param year:
    :return:
    """
    try:
        return Periode.objects.get(annee=year)
    except ObjectDoesNotExist:
        return None
