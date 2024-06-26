import json
from multiprocessing import Value

from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, CharField, Value, Subquery, OuterRef, IntegerField, QuerySet

from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .forms import SubmitForm, UpdateForm, EtapeForm, ConfirmationSujetReservation, \
    FichierDelivrableForm
from .models import FichierDelivrable
from .queries import *

from .restrictions import *
from .utils.date import get_today_year


@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_required
def topics(request: HttpRequest, idue: str) -> HttpResponse:
    """
    :param request: La requête courante
    :param idue: L'id d'une ue
    :return: La page html affichant les sujets dédiés pour un cours ainsi que la requête http
    """
    ue: Ue = find_ue(idue=idue)
    # Récupèrer tous les sujets associés à cette ue
    year: Periode = find_periode_by_year(get_today_year())
    sujets: list[Sujet] = Sujet.objects.filter(idue=ue, idperiode=year)
    sujet_infos: list[dict[str, list | Any]] = []

    for sujet in sujets:
        sujet_info: dict[str, Any] = {
            'id': sujet.idsujet,
            'titre': sujet.titre,
            'description': sujet.descriptif,
            'referent': sujet.idprof.idpersonne.prenom + " " + sujet.idprof.idpersonne.nom if sujet.idprof_id is not None else sujet.idsuperviseur.idpersonne.prenom + " " + sujet.idsuperviseur.idpersonne.nom,
            'etudiants': [],
            'estPris': sujet.estpris
        }

        if sujet.estpris:
            etudiants = SelectionSujet.objects.filter(idsujet=sujet.idsujet)
            etudiants_noms = [f"{etudiant.idetudiant.idpersonne.nom} {etudiant.idetudiant.idpersonne.prenom}" for
                              etudiant in etudiants]
            sujet_info['etudiants'] = etudiants_noms

        sujet_infos.append(sujet_info)

    return render(request, "otherRole/topic.html", {'sujet_infos': sujet_infos, 'ue': ue})


@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_or_superviseur_required
def new(request: HttpRequest, idue: str) -> HttpResponse:
    """
    Fonction renvoyant la page pour enregistrer un nouveau sujet
    :param request: Requête http courante
    :param idue: l'idue
    :return:
    """
    ue: Ue = find_ue(idue=idue)
    # Récupérer tous les sujets associés à cette ue
    year_sujet: list[Periode] = Periode.objects.filter(annee__lt=get_today_year()).distinct()

    years: list[dict[str, Periode | list[Sujet]]] = []
    for year in year_sujet:
        sujet_query: list[Sujet] = Sujet.objects.filter(idue=ue, estpris=False, idperiode__annee=year.annee)
        sujets: list[Sujet] = []
        for sujet in sujet_query:
            sujets.append(sujet)
        years.append({'year': year, 'sujets': sujets})

    return render(request, "otherRole/ReuseSubject.html", {'years': years, 'ue': ue})


@login_required(login_url='/polls')
@csrf_exempt
@prof_or_superviseur_required
def myTopics(request, idue: str) -> HttpResponse:
    """
    Affichage des sujets d'un prof ou d'un superviseur
    :param request: La requête http courante
    :param idue: l'id de l'ue à rechercher
    :return: la page html pour afficher les sujets liés à un prof ou un superviseur
    """
    user = request.user
    ue: Ue = find_ue(idue=idue)
    year: Periode = find_periode_by_year(get_today_year())
    if 'professeur' in user.role['role']:

        # Récupèrer tous les sujets associés à ces cours
        sujets: QuerySet[Sujet] | list[Sujet] = Sujet.objects.filter(idue=ue,
                                                                     idprof=find_prof_by_id_personne(user.idpersonne),
                                                                     idperiode=year)
        sujet2: QuerySet[Sujet] = Sujet.objects.filter(idue=ue, idperiode=year,
                                                       idsuperviseur__idpersonne=user.idpersonne)
        sujets: list[Sujet] = sujets.union(sujet2)
    else:
        sujets = find_subject_for_a_superviseur(user.idpersonne, year)
    sujet_infos: list[dict[str, Any]] = []
    for sujet in sujets:
        sujet_info = {
            'id': sujet.idsujet,
            'titre': sujet.titre,
            'description': sujet.descriptif,
            'referent': sujet.idprof.idpersonne.prenom + " " + sujet.idprof.idpersonne.nom if sujet.idprof_id is not None else sujet.idsuperviseur.idpersonne.prenom + " " + sujet.idsuperviseur.idpersonne.nom,
            'etudiants': [],
            'estPris': sujet.estpris
        }

        if sujet.estpris:
            etudiants = [SelectionSujet.objects.get(idsujet=sujet.idsujet).idetudiant]
            etudiants_noms = [f"{etudiant.idpersonne.nom} {etudiant.idpersonne.prenom}" for etudiant in etudiants]
            sujet_info['etudiants'] = etudiants_noms

        sujet_infos.append(sujet_info)

    return render(request, "otherRole/topic.html", {'sujet_infos': sujet_infos, 'ue': ue})


@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_or_superviseur_required
@is_owner_of_ue_or_admin
def participants(request: HttpRequest, idue: str) -> HttpResponse:
    """
    Affiche tous les participants d'une ue
    :param request: La requête courante
    :param idue: l'id de l'ue concernée
    :return: la page html affichant les participants
    """
    ue: Ue = find_ue(idue)
    students: list[Personne] = find_students_of_ue(ue)
    professor: Personne = find_owner_of_ue(ue)
    supervisors: list[Personne] = find_supervisors_of_ue(ue)
    context: dict[str, list[Personne] | Personne] = {
        'students': students,
        'professor': professor,
        'supervisors': supervisors,
        'ue': Ue
    }
    return render(request, "otherRole/participants.html",
                  context=context)


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
@csrf_exempt
def NoteTopic(request: HttpRequest, sujet_id: int, idue: str) -> HttpResponse:
    """
    Affiche la page pour noter un délivrable
    :param request: La requête http courante
    :param sujet_id: l'id du sujet a évalué
    :param idue: l'id de l'ue auquel le sujet est rattaché.
    :return:
    """
    ue: Ue = find_ue(idue)
    etapes: Etape | EtapeUe = find_etapes_of_ue(ue)[0]
    current_etape: Etape = find_current_etape_of_ue(ue)
    etapes_passees: list[Etape] = []
    sujet: Sujet = find_sujet_by_id(sujet_id)
    # ajoute les délivrables passés et celui en cours
    for etape in etapes:
        if etape.idetape == current_etape.idetape:
            etapes_passees.append(etape)
            break
        else:
            etapes_passees.append(etape)
    delivrables: list[dict[str, Any]] = []

    for etape in etapes_passees:
        iddelivrable: int = etape.iddelivrable_id
        delivrable: list[FichierDelivrable] = FichierDelivrable.objects.filter(iddelivrable=iddelivrable,
                                                                               idsujet=sujet_id)
        for deli in delivrable:
            if 'iddeli' in request.GET and 'idetudiant' in request.GET:
                if int(request.GET['iddeli']) == deli.iddelivrable_id and int(
                        request.GET['idetudiant']) == deli.idetudiant_id:
                    deli.note = request.GET['note']
                    deli.save()
            etape_info: dict[str, Any] = {
                "titre": etape.titre,
                "description": etape.description,
                "fichier": deli.fichier,
                "note": deli.note,
                "idetudiant": deli.idetudiant,
                "iddelivrable": deli.iddelivrable_id
            }
            delivrables.append(etape_info)
    return render(request, "otherRole/note_topic.html", {"sujet": sujet, "ue": ue, 'delivrables': delivrables})


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
@csrf_exempt
def editTopic(request, sujet_id) -> HttpResponse:
    """
    Page affichant un formulaire pour modifier un sujet
    :param request: Requête http courante
    :param sujet_id: l'id du sujet
    :return: page pour modifier le sujet
    """
    sujet: Sujet = get_object_or_404(Sujet, idsujet=sujet_id)
    id_ue: int = sujet.idue
    form_data: dict[str, str] = {
        'title': sujet.titre,
        'description': sujet.descriptif,
        'destination': sujet.destination,
        'fichier': sujet.fichier,
    }
    if request.method == 'POST':
        year: Periode = find_periode_by_year(get_today_year())
        form = UpdateForm(request.POST, request.FILES, list_students=find_students_of_ue(id_ue),
                          list_referent=find_supervisors_of_ue(id_ue).union(
                              Personne.objects.filter(idpersonne=find_owner_of_ue(id_ue).idpersonne)),
                          is_admin=is_user_admin(request.user.idpersonne))
        sujet.titre = request.POST['title']
        sujet.descriptif = request.POST['description']
        sujet.destination = request.POST['destination']
        sujet.fichier = request.FILES['file'] if bool(request.FILES) else None
        sujet.nbpersonnes = request.POST['nb_personnes']
        sujet.idperiode = year
        sujet.save()

        return HttpResponseRedirect(request.GET.get('next'))
    else:
        form = UpdateForm(initial=form_data, list_students=find_students_of_ue(id_ue),
                          list_referent=find_supervisors_of_ue(id_ue).union(
                              Personne.objects.filter(idpersonne=find_owner_of_ue(id_ue).idpersonne)),
                          is_admin=is_user_admin(request.user.idpersonne))

    return render(request, 'otherRole/submitSubject.html',
                  {'form': form, 'ue': id_ue, 'edit': True, 'previous_url': request.GET.get('next')})


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
@csrf_exempt
def deleteTopic(request: HttpRequest, sujet_id: int) -> HttpResponse:
    """
    Efface le sujet défini par sujet_id
    :param request: La requête courante
    :param sujet_id: l'id du sujet à effacer
    :return:
    """
    sujet: Sujet = get_object_or_404(Sujet, idsujet=sujet_id)
    selections: list[SelectionSujet] = find_selection_by_id_sujet(sujet)
    for selection in selections:
        selection.delete()
    sujet.delete()
    return HttpResponseRedirect(request.GET.get('next'))


@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_or_superviseur_required
def add_topic(request: HttpRequest, idue: str) -> HttpResponse:
    """
    Affiche la page pour ajouter un sujet
    :param request: Requête http courante
    :param idue: l'id de l'ue auquel le sujet doit être rattaché
    :return: La page contenant le formulaire pour ajouter un sujet
    """
    user = request.user
    is_admin: bool = is_user_admin(user.idpersonne)
    ue = find_ue(idue)
    if request.method == 'POST':
        form = SubmitForm(request.POST, request.FILES, list_students=find_students_of_ue(ue),
                          list_referent=find_supervisors_of_ue(ue).union(
                              Personne.objects.filter(idpersonne=find_owner_of_ue(ue).idpersonne)), is_admin=is_admin)

        titre: str = request.POST['title']
        descriptif: str = request.POST['description']
        destination: str = request.POST['destination']
        fichier: str = request.FILES['file'] if bool(request.FILES) else None
        nb_personnes: int = request.POST['nb_personnes']
        year: Periode = find_periode_by_year(get_today_year())
        if 'admin' in user.role['role']:
            referent_id: int = request.POST['referent_select']
            is_prof: bool = True if find_owner_of_ue(ue) == find_personne_by_id(referent_id) else False
            if is_prof:
                prof: Professeur = find_prof_by_id_personne(referent_id)
                sujet: Sujet = Sujet(titre=titre, descriptif=descriptif, destination=destination, fichier=fichier,
                                     idprof=prof,
                                     nbpersonnes=nb_personnes, idue=ue, idperiode=year)
            else:
                sup: Superviseur = find_superviseur_by_id_personne(referent_id)
                sujet: Sujet = Sujet(titre=titre, descriptif=descriptif, destination=destination, fichier=fichier,
                                     idsuperviseur=sup, nbpersonnes=nb_personnes, idue=ue, idperiode=year)

        elif 'professeur' in user.role['role']:
            prof: Professeur = find_prof_by_id_personne(user.idpersonne)
            sujet: Sujet = Sujet(titre=titre, descriptif=descriptif,
                                 destination=destination, fichier=fichier,
                                 idprof=prof, nbpersonnes=nb_personnes, idue=ue, idperiode=year)
        else:
            superviseur: Superviseur = find_superviseur_by_id_personne(user.idpersonne)
            sujet: Sujet = Sujet(titre=titre, descriptif=descriptif,
                                 destination=destination, fichier=fichier,
                                 idsuperviseur=superviseur, nbpersonnes=nb_personnes, idue=ue, idperiode=year)

        sujet.save()

        return HttpResponseRedirect("../")

    else:
        form: SubmitForm = SubmitForm(list_students=find_students_of_ue(ue),
                                      list_referent=find_supervisors_of_ue(ue).union(
                                          Personne.objects.filter(idpersonne=find_owner_of_ue(ue).idpersonne)),
                                      is_admin=is_admin)

    context: dict[str, Any] = {
        'ue': ue,
        'title': 'Cours',
        'prenom': "Matthys",
        'role': "Etudiant",
        "form": form,
        'is_admin': is_admin,
        "previous_url": request.GET.get('next')
    }
    return render(request, 'otherRole/submitSubject.html', context)


@login_required(login_url="/polls")
@csrf_exempt
def ok(request: HttpRequest) -> HttpResponse:
    """
    Affichage de la page servant à valider une opération
    :param request: La requête courante
    :return: la page servant à afficher un message en cas de réussite d'une opération
    """
    return render(request, "otherRole/ok.html", context={ok: 'Votre sujet a été validé'})


@login_required(login_url='/polls')
@csrf_exempt
def afficher_etapes_ue(request: HttpRequest, idue: str) -> HttpResponse:
    """
    Affichage des différentes étapes de l'ue en cours
    :param request: La requête http courante
    :param idue: l'id de l'ue dont le professeur est en charge
    :return:
    """
    ue: Ue = get_object_or_404(Ue, idue=idue)
    professeur: Professeur = ue.idprof
    periode: Periode = professeur.idperiode
    etapes: list[Etape] = Etape.objects.filter(idperiode=periode).order_by('delai')
    context = {
        'etapes': etapes,
        'Ue': idue
    }
    return render(request, 'otherRole/afficher_etapes_ue.html', context=context)


@login_required(login_url='/polls')
def subscription_courses(request) -> HttpResponse:
    """
    Affichage des cours auxquels l'utilisateur n'est pas encore inscrit
    :param request: Requête http courante
    :return: La page html qui sert à afficher lesdits cours
    """
    user = request.user
    if 'etudiant' in user.role['role']:
        cours: list[Cours] = find_course_for_student_for_subscription(user.idpersonne)
        courses = []
        for cours in cours:
            courses.append(cours)
        context: dict[str, list[list[Cours]]] = {
            'courses': courses
        }
        return render(request, 'otherRole/inscription.html', context)
    else:
        return redirect("../../home/")


@login_required(login_url='/polls')
def subscription_validation(request, idue: str, nom: str) -> HttpResponse:
    """

    :param request: La requête http courante
    :param idue: id de l'ue auquel l'étudiant veut s'inscrire
    :param nom: nom de l'ue
    :return: La page auquel l'étudiant retourne quand l'inscription a eu lieu
    """
    user = request.user
    etudiant: Etudiant = Etudiant.objects.get(idpersonne=user.idpersonne)
    ue: Ue = Ue.objects.get(idue=idue)
    cours: Cours = Cours(idetudiant=etudiant, idue=ue, nom=nom)
    cours.save()
    return redirect("../../../home/")


@login_required(login_url='/polls')
@csrf_exempt
@student_required
def mycourses(request) -> HttpResponse:
    """
    Renvoie la page qui affiche les cours auxquels l'étudiant est inscrit
    :param request:
    :return: La page html avec comme context les cours auxquels l'étudiant eszt inscrit
    """
    user = request.user
    courses_query: list[Cours] = find_course_for_student(user.idpersonne)
    courses_ue: list[Cours] = []
    if courses_query:
        for cours in courses_query:
            courses_ue.append(cours.idue)

    context: dict[str, list[Cours]] = {
        'courses': courses_ue
    }
    return render(request, "otherRole/home.html", context=context)


@login_required(login_url='/polls')
@csrf_exempt
@is_student_of_ue
def mycourse(request, idue: str) -> HttpResponse:
    """
    Description du cours sélectionné
    :param request: Requête http courante
    :param idue: id de l'ue entrée en paramètre
    :return:
    """
    user = request.user
    etudiant: Etudiant = find_student_by_id_personne(user.idpersonne)
    ue: Ue = find_ue(idue)
    etapes, etapes_ue = find_etapes_of_ue(ue)
    current_etape: Etape = find_current_etape_of_ue(ue)
    fichier_delivrable_instance: FichierDelivrable | None = None
    form: FichierDelivrableForm | None = None
    already_submitted: bool = False
    # on part du principe que quand une étape ne contient pas de délivrable, c'est que c'est une étape de choix de sujet
    context_reservation = None
    topics_of_students: list[Sujet] = find_sujets_of_student_of_ue(find_student_by_id_personne(user.idpersonne), idue)
    if current_etape is not None and current_etape.iddelivrable_id is None:
        context_reservation = reservation_subject_student(idue, user.idpersonne)
    if current_etape.iddelivrable_id is not None:
        fichier_delivrable_instance: FichierDelivrable = FichierDelivrable.objects.filter(
            iddelivrable=current_etape.iddelivrable_id,
            idetudiant=etudiant,
            rendu=True
        ).first()
        already_submitted = fichier_delivrable_instance is not None
        form: FichierDelivrableForm = FichierDelivrableForm(
            instance=fichier_delivrable_instance) if fichier_delivrable_instance else FichierDelivrableForm()
        if request.method == 'POST':
            form: FichierDelivrableForm = FichierDelivrableForm(request.POST, request.FILES,
                                                                instance=fichier_delivrable_instance)
            if form.is_valid():
                fichier_delivrable: FichierDelivrableForm = form.save(commit=False)
                fichier_delivrable.iddelivrable = get_object_or_404(Delivrable,
                                                                    iddelivrable=current_etape.iddelivrable_id)
                fichier_delivrable.idetudiant = etudiant
                fichier_delivrable.nom_personne = etudiant.idpersonne.nom
                fichier_delivrable.nom_cours = idue
                fichier_delivrable.annee_periode = current_etape.idperiode.annee
                fichier_delivrable.rendu = True
                fichier_delivrable.save()
                return redirect("page d'un cours", idue=ue.idue)

    context: dict[str, Any] = {
        'ue': ue,
        'is_student': True,
        'etapes': etapes,
        'etapes_ue': etapes_ue,
        'current_etape': current_etape,
        'context_reservation': context_reservation,
        'form': form,
        'already_submitted': already_submitted,
        'topics_of_student': topics_of_students,
        'no_topic': len(topics_of_students) == 0

    }
    return render(request, "course.html", context=context)


@login_required(login_url='polls')
def reservation(request, idue: str) -> HttpResponse:
    """
    Affichage de la page de réservation pour un prof en particulier
    :param request:  la requête http courante
    :param idue: l'id de l'ue en courante
    :return: la page html décrivant les sujets qui sont à réserver
    """
    user = request.user
    if "professeur" in user.role['role']:
        subjects_query: list[Sujet] = find_all_subjects_for_a_teacher(user.idpersonne)
        subjects: list[Sujet] = []
        for subject in subjects_query:
            subjects.append(subject)

        context: dict[str, list[str] | list[Sujet]] = {
            'subjects': subjects,
            'subject_title': ["Titre", "Descriptif", "Á réserver"]
        }
        return render(request, "otherRole/reservation.html", context)
    else:
        return redirect('/polls')


@login_required(login_url='polls')
def knows_if_subject_is_booked_for_teacher(request, idue: str) -> HttpResponse:
    """
    La fonction sert à connaître si le sujet est réservé par un prof en particulier
    :param request: la requête http courante
    :param idue: l'ue en charge du professeur
    :return:
    """
    user = request.user
    if "professeur" in user.role['role']:
        subjects_query: list[Sujet] = find_all_subjects_for_a_teacher(user.idpersonne)
        subjects_reserved: list[dict[str, Sujet | list[SelectionSujet] | bool] | dict[str, Sujet | bool]] = []
        for subject in subjects_query:
            nbPersonne: int = nb_people_keeping_for_a_sujet(subject)
            if nbPersonne < subject.nbpersonnes:
                personnesReservees: list[SelectionSujet] = find_selection_by_id_sujet(subject)
                subjects_reserved.append(
                    {'sujet': subject, 'estReserve': True, 'personnesReservees': personnesReservees})
            else:
                subjects_reserved.append({'sujet': subject, 'estReserve': False})
        context: dict[str, Any] = {
            'subjects': subjects_reserved,
            'subject_title': ["Titre", "Descriptif", "Est réservé", 'Nombre de personnes'],
            "title": "Sujets réservés",
            'attribution': 'attribution'
        }
        return render(request, "otherRole/reservation.html", context)


@login_required(login_url='polls')
@prof_or_superviseur_required
@csrf_exempt
# pas besoin de validation vu que le formulaire est supposé correcte suit à l'envoi précédent
def booking(request, idue: str, idsujet: int) -> HttpResponse:
    """

    :param request: Requête http courante
    :param idue: id de l'ue
    :param idsujet: id du sujet pour la réservation en cours.
    :return: La page confirmant la réservation ou alors on effectue un retour à la page réservation
    """
    user = request.user
    if 'professeur' in user.role['role']:
        sujet: Sujet = find_sujet_by_id(idsujet)
        initial_data: dict[str, str | int | list[Etudiant]] = {
            'title': sujet.titre,
            'description': sujet.descriptif,
            'subject_id': idsujet,
            'students': find_students_without_subjects_by_teacher(user.idpersonne)
        }
        form: ConfirmationSujetReservation = ConfirmationSujetReservation(initial=initial_data)
        nbPersonnes: int = nb_people_keeping_for_a_sujet(sujet)
        isAvalaible: bool = nbPersonnes > 0
        context: dict[str, ConfirmationSujetReservation | int | bool] = {
            'form': form,
            'idsujet': idsujet,
            'isAvalaible': isAvalaible
        }
        return render(request, "otherRole/confirmationReservation.html", context=context)
    else:
        return redirect('../reservation')


@login_required(login_url='polls/')
def validation_booking(request, idue: str, idsujet: int) -> HttpResponse:
    """
    Méthode confirmant la réservation d'un sujet par un étudiant
    :param request: la requête http courante
    :param idue: id de l'ue du sujet
    :param idsujet: :l'id du sujet à réserver
    :return:
    """
    user = request.user
    if request.method == "POST" and "professeur" in user.role['role']:
        idstudent: int = request.POST.get('students')
        etudiant: Etudiant = find_student_by_id_etudiant(int(idstudent))
        sujet: Sujet = find_sujet_by_id(idsujet)
        selectionSujet: SelectionSujet = SelectionSujet(idsujet=sujet, idetudiant=etudiant)
        selectionSujet.save()
        sujet = find_sujet_by_id(idsujet)
        if sujet.nbpersonnes == 1:
            sujet.estPris = True
        else:
            if nb_people_keeping_for_a_sujet(sujet) == 0:
                sujet.estpris = True
        sujet.save()
        return redirect('../../../../')
    else:
        return redirect('../../../../ok', )


@login_required(login_url='/polls')
def vue_historique(request: HttpRequest) -> HttpResponse:
    """
    Affiche l'historique
    :param request: Requête courante
    :return: Retourne la page html affichant l'historique
    """
    # Main query
    queryset: QuerySet[SelectionSujet] = SelectionSujet.objects.filter(
        is_involved=True,  # Only include students who are involved in the subject
    ).values(
        annee_academique=F('idsujet__idperiode__annee'),
        nom_cours=F('idsujet__idue__cours__nom'),
        titre_sujet=F('idsujet__titre'),
        description_sujet=F('idsujet__descriptif'),
    ).annotate(
        nom_complet_etudiant=Concat('idetudiant__idpersonne__nom', Value(' '), 'idetudiant__idpersonne__prenom',
                                    output_field=CharField()),
        mark=Subquery(FichierDelivrable.objects.filter(idetudiant=OuterRef('idetudiant')).values('note')[:1],
                      output_field=IntegerField()),
        nom_complet_professeur=Concat('idsujet__idprof__idpersonne__nom', Value(' '),
                                      'idsujet__idprof__idpersonne__prenom',
                                      output_field=CharField()),
    ).order_by('idsujet__idperiode__annee').distinct()

    queries: list[SelectionSujet] = list(queryset)
    annees = list(set(query['annee_academique'] for query in queryset))
    context: dict[str, QuerySet[SelectionSujet] | list[int]] = {
        'queryset': queries,
        'annees': annees}
    return render(request, "otherRole/historique.html", context={'queryset': queries, 'annees': annees})


@login_required(login_url='/polls')
def vue_historique_annee(request, annee):
    # Subquery to get the names of students involved in the same topic
    """student_names = SelectionSujet.objects.filter(
        idsujet__idue=OuterRef('idue'),
        is_involved=True,  # Only include students who are involved in the topic
    ).annotate(
        full_name=Concat('idetudiant__idpersonne__nom', Value(' '), 'idetudiant__idpersonne__prenom',
                         output_field=CharField()),
        mark=Subquery(FichierDelivrable.objects.filter(idetudiant=OuterRef('idetudiant')).values('note')[:1],
                      output_field=IntegerField())
    ).values('full_name', 'mark')
    """

    # Main query
    queryset = SelectionSujet.objects.filter(
        is_involved=True,  # Only include students who are involved in the subject
    ).values(
        annee_academique=F('idsujet__idperiode__annee'),
        nom_cours=F('idsujet__idue__cours__nom'),
        titre_sujet=F('idsujet__titre'),
        description_sujet=F('idsujet__descriptif'),
    ).annotate(
        nom_complet_etudiant=Concat('idetudiant__idpersonne__nom', Value(' '), 'idetudiant__idpersonne__prenom',
                                    output_field=CharField()),
        mark=Subquery(
            FichierDelivrable.objects.filter(idetudiant=OuterRef('idetudiant')).order_by('-iddelivrable').values(
                'note')[:1],
            output_field=IntegerField()),
        nom_complet_professeur=Concat('idsujet__idprof__idpersonne__nom', Value(' '),
                                      'idsujet__idprof__idpersonne__prenom',
                                      output_field=CharField()),
    ).order_by('idsujet__idperiode__annee').filter(annee_academique=annee).distinct()

    queries = list(queryset)
    context = {'queryset': queries, 'title': f"Historique des sujets pour l\'année {str(annee)}", 'archivage': False}

    return render(request, "otherRole/historique.html", context=context)


@login_required(login_url='polls')
@is_owner_of_ue_or_admin
@csrf_protect
def etape_view(request: HttpRequest, idue: str) -> HttpResponse:
    """
    Affiche une vue correspondant aux différentes étapes
    :param request: La requête http courante
    :param idue: l'id de l'ue en cours
    :return: La page html permettant de paramétrer la timeline
    """
    ue: Ue = find_ue(idue)
    etapes, etapes_ue = find_etapes_of_ue(ue)

    if request.method == 'POST':
        form: EtapeForm = EtapeForm(request.POST)
        if form.is_valid():
            etape: Etape = form.save(commit=False)
            etape.idperiode = ue.idprof.idperiode
            delivrable: Delivrable | None = None
            if 'typeFichier' in request.POST and request.POST['typeFichier'].strip():
                delivrable: Delivrable = find_delivrable_by_type(request.POST['typeFichier'])
                if delivrable is None:
                    delivrable: Delivrable = Delivrable()
                    typeFichier = request.POST['typeFichier']
                    delivrable.typeFichier = typeFichier
                    delivrable.save()

            etape.iddelivrable = delivrable
            etape.save()
            EtapeUe(idue=ue, idetape=etape).save()
            return HttpResponseRedirect(request.path)
    else:
        form: EtapeForm = EtapeForm()
    context = {'form': form, 'etapes': etapes, 'ue': ue, 'etapes_ue': etapes_ue}
    return render(request, 'otherRole/commandTimeline.html',
                  context=context)


@login_required(login_url='/polls')
@is_student_of_ue
@student_required
@transaction.atomic
def confirmer_reservation_sujet(request, idue: str, idsujet: int):
    """
    Confirme la réservation d'un sujet
    :param request: Requête http courante
    :param idue: id de l'ue pour la réservation d'un sujet
    :param idsujet: id sujet à réserver
    :return: renvoie vers la requête suivante.
    """
    user = request.user
    etudiant: Etudiant = find_student_by_id_personne(user.idpersonne)
    sujet: Sujet = get_subject_by_id(idsujet)
    if nb_people_keeping_for_a_sujet(sujet) == 1:
        sujet.estpris = True
    selectionSujet: SelectionSujet = SelectionSujet(idetudiant=etudiant, idsujet=sujet)
    selectionSujet.save()
    sujet.save()

    return HttpResponseRedirect(request.GET.get('next'))


@login_required(login_url='/polls')
@is_owner_of_ue_or_admin
def deleteStep(request: HttpRequest, idue: str, idetape: int) -> HttpResponse:
    """
    Efface l'étape correspondante à idEtape
    :param request: Requête http courante
    :param idue: id de l'ue
    :param idetape: id de l'étape envoyé par le formulaire
    :return: Renvoie vers la page précédente
    """
    etape: Etape = find_etape_by_id(idetape)
    etapeue: EtapeUe = find_etapeue_by_idetape_and_ue(idetape, idue)
    if etapeue is not None and etape is not None:
        etapeue.delete()
        etape.delete()
    return HttpResponseRedirect("../")


@login_required(login_url='/polls')
@is_owner_of_ue_or_admin
def selectStep(request: HttpRequest, idue: str, idetapeue: int) -> JsonResponse:
    etapeue_to_select: EtapeUe = find_etapeue_by_idetape_and_ue(idetapeue, idue)
    etapes, etapes_ue = find_etapes_of_ue(find_ue(idue))
    for etape in etapes_ue:
        etape.etapecourante = False
        etape.save()
    etapeue_to_select.etapecourante = True
    etapeue_to_select.save()
    etapes, etapes_ue = find_etapes_of_ue(find_ue(idue))
    return JsonResponse({'etapes_ue': json.loads(serialize('json', etapes_ue))})


@login_required(login_url='/polls')
@is_owner_of_ue_or_admin
def changeAccess(request, idue: str, val: bool):
    ue: Ue = find_ue(idue)
    ue.isopen = val
    ue.save()
    return JsonResponse({'succes': "ok"})


@login_required(login_url='/polls')
def back(request: HttpRequest) -> HttpResponse:
    """
    Fonction servant à retourner à la page précédente dans certains
    :param request:
    :return:
    """
    return HttpResponseRedirect("../")


# ne pas mettre de décorateur pour cette fonction
def reservation_subject_student(idue: str, idpersonne: int) -> dict[str, list[str] | list[Sujet] | int | str] | None:
    """
    Retourne les sujets d'un étudiantpour une ue
    :param idue: id de l'ue courante
    :param idpersonne: idpersonne de l'étudiant
    :return: toutes les informations nécessaires.
    """
    etudiant: Etudiant = find_student_by_id_personne(idpersonne)
    if count_subject_for_one_student_and_one_ue(etudiant.idetudiant, idue) == 0:
        sujets_query: list[Sujet] = find_sujets_by_idue(idue)
        sujets: list[dict[str, list[Sujet] | list[str] | int]] = []
        for sujet in sujets_query:
            nbPersonnesRestantes = nb_people_keeping_for_a_sujet(sujet)
            sujets.append(
                {'sujet': sujet, 'nbPersonnesRestantes': nbPersonnesRestantes, 'nbPersonnes': sujet.nbpersonnes})
        if len(sujets) > 0:
            context: dict[str, list[str] | list[Sujet] | int | str] = {
                'titles': ['Titre', 'Description', 'Professeur/Superviseur', 'Nombre de personnes', 'Réserver'],
                'sujets': sujets,
                'idue': idue
            }
        else:
            context = {
                'failure': "Vous ne pouvez plus réserver de sujet pour ce cours"
            }
    else:
        context = {
            'failure': "Vous ne pouvez plus réserver de sujet pour ce cours"
        }
    return context


@login_required(login_url='/polls')
def archivage(request:HttpRequest, idue:str)->HttpResponse:
    """
    Affiche l'archivage des sujets par année à partir de l'année précédente de celle actuelle
    :param request: La requête Http courante
    :param idue: id de l'ue courante
    :return: L'état de l'archivage des sujets pour par année et par cours
    """
    # Main query
    queryset:QuerySet[SelectionSujet] = SelectionSujet.objects.filter(
        is_involved=True,  # Only include students who are involved in the subject
    ).values(
        annee_academique=F('idsujet__idperiode__annee'),
        nom_cours=F('idsujet__idue__cours__nom'),
        titre_sujet=F('idsujet__titre'),
        description_sujet=F('idsujet__descriptif'),
    ).annotate(
        nom_complet_etudiant=Concat('idetudiant__idpersonne__nom', Value(' '), 'idetudiant__idpersonne__prenom',
                                    output_field=CharField()),
        mark=Subquery(
            FichierDelivrable.objects.filter(idetudiant=OuterRef('idetudiant')).order_by('-iddelivrable').values(
                'note')[:1],
            output_field=IntegerField()),
        nom_complet_professeur=Concat('idsujet__idprof__idpersonne__nom', Value(' '),
                                      'idsujet__idprof__idpersonne__prenom',
                                      output_field=CharField()),
        delivrable_links=Subquery(
            FichierDelivrable.objects.filter(idetudiant=OuterRef('idetudiant')).order_by('-iddelivrable').values(
                'fichier').values('fichier')),
    ).order_by('idsujet__idperiode__annee').distinct()

    queries:list = list(queryset)
    titles:list[str] = ['Année académique', 'Nom du cours', 'Titre du sujet', 'Description du sujet', 'Note Attribuée',
              'Nom complet de l\'étudiant', 'Professeur.e.s', 'Lien vers le délivrable']
    context:dict[str,QuerySet[SelectionSujet]|str|bool|list[str]] = {'queryset': queries, 'title': f"Archivage des sujets", 'archivage': True, 'titles': titles}
    return render(request, "otherRole/historique.html", context=context)


@login_required(login_url='/polls')
def deliverable_file(request:HttpRequest, idue:str, path:str)->FileResponse:
    """
    Renvoi le fichier référencé par path
    :param request: la requête courante
    :param idue: l'id de l'ue auquel est rattaché le fichier
    :param path: le chemin d'accès au fichier
    :return: Le fichier en question
    """
    deliverable:FichierDelivrable = get_object_or_404(FichierDelivrable, fichier=path)
    return FileResponse(deliverable.fichier)
