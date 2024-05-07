import logging, json
from multiprocessing import Value
from multiprocessing.managers import BaseManager

from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, CharField, Value, Subquery, OuterRef, Case, When, IntegerField
from django.contrib.postgres.aggregates import StringAgg
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .forms import SubmitForm, UpdateForm, EtapeForm, SubjectReservationForm, ConfirmationSujetReservation, \
    FichierDelivrableForm
from .models import Sujet, Etudiant, Ue, Cours, Etape, Delivrable, FichierDelivrable
from .queries import *

from .restrictions import *
from .utils.date import get_today_date, get_today_year
from .utils.remove import remove_duplicates


@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_required
def topics(request, idue) -> HttpResponse:
    ue = find_ue(idue=idue)
    # Récupèrer tous les sujets associés à cette ue
    sujets = Sujet.objects.filter(idue=ue)
    sujet_infos = []

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
            etudiants = SelectionSujet.objects.filter(idsujet=sujet.idsujet)
            etudiants_noms = [f"{etudiant.idetudiant.idpersonne.nom} {etudiant.idetudiant.idpersonne.prenom}" for
                              etudiant in etudiants]
            sujet_info['etudiants'] = etudiants_noms

        sujet_infos.append(sujet_info)

    return render(request, "otherRole/topic.html", {'sujet_infos': sujet_infos, 'ue': ue})


@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_or_superviseur_required
def new(request, idue) -> HttpResponse:
    ue = find_ue(idue=idue)
    # Récupérer tous les sujets associés à cette ue
    year_sujet = Periode.objects.filter(annee__lt=get_today_year()).distinct()

    years = []
    for year in year_sujet:
        sujet_query = Sujet.objects.filter(idue=ue,estpris=False,idperiode__annee=year.annee)
        sujets = []
        for sujet in sujet_query:
            sujets.append(sujet)
        years.append({'year':year, 'sujets':sujets})
    print(years)


    return render(request, "otherRole/ReuseSubject.html", {'years': years, 'ue': ue})


@login_required(login_url='/polls')
@csrf_exempt
@prof_or_superviseur_required
def myTopics(request, idue) -> HttpResponse:
    user = request.user
    ue = find_ue(idue=idue)
    if 'professeur' in user.role['role']:
        # Récupèrer tous les sujets associés à ces cours
        sujets = Sujet.objects.filter(idue=ue, idprof=find_prof_by_id_personne(user.idpersonne).idprof)
    else:
        sujets = find_subject_for_a_superviseur(user.idpersonne)
    sujet_infos = []
    for sujet in sujets:
        sujet_info = {
            'id': sujet.idsujet,
            'titre': sujet.titre,
            'description': sujet.descriptif,
            'referent': sujet.idprof.idpersonne.prenom + " " + sujet.idprof.idpersonne.nom if sujet.idprof is not None else sujet.idsuperviseur.idpersonne.prenom + " " + sujet.idsuperviseur.idpersonne.nom,
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
def participants(request, idue) -> HttpResponse:
    ue = find_ue(idue)
    students = find_students_of_ue(ue)
    professor = find_owner_of_ue(ue)
    supervisors = find_supervisors_of_ue(ue)
    return render(request, "otherRole/participants.html",
                  context={"students": students, "professor": professor, "supervisors": supervisors, "ue": ue})


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
@csrf_exempt
def NoteTopic(request, sujet_id, idue):
    ue = find_ue(idue)
    etapes = find_etapes_of_ue(ue)[0]
    current_etape = find_current_etape_of_ue(ue)
    etapes_passees = []
    sujet = find_sujet_by_id(sujet_id)
    # ajoute les délivrables passés et celui en cours
    for etape in etapes:
        if etape.idetape == current_etape.idetape:
            etapes_passees.append(etape)
            break
        else:
            etapes_passees.append(etape)
    delivrables = []

    for etape in etapes_passees:
        iddelivrable = etape.iddelivrable_id
        delivrable = FichierDelivrable.objects.filter(iddelivrable=iddelivrable,idsujet=sujet_id)
        for deli in delivrable:
            if 'iddeli' in request.GET and 'idetudiant' in request.GET:
                if int(request.GET['iddeli']) == deli.iddelivrable_id and int(
                        request.GET['idetudiant']) == deli.idetudiant_id:
                    deli.note = request.GET['note']
                    deli.save()
            etape_info = {
                "titre": etape.titre,
                "description": etape.description,
                "fichier": deli.fichier,
                "note": deli.note,
                "idetudiant": deli.idetudiant,
                "iddelivrable": deli.iddelivrable_id
            }
            delivrables.append(etape_info)
    print(delivrables)
    return render(request, "otherRole/note_topic.html", {"sujet": sujet, "ue": ue, 'delivrables': delivrables})


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
@csrf_exempt
def editTopic(request, sujet_id):
    sujet = get_object_or_404(Sujet, idsujet=sujet_id)
    id_ue = sujet.idue
    form_data = {
        'title': sujet.titre,
        'description': sujet.descriptif,
        'destination': sujet.destination,
        'fichier': sujet.fichier,
    }
    if request.method == 'POST':
        form = UpdateForm(request.POST, request.FILES, list_students=find_students_of_ue(id_ue),
                          list_referent=find_supervisors_of_ue(id_ue).union(
                              Personne.objects.filter(idpersonne=find_owner_of_ue(id_ue).idpersonne)),
                          is_admin=is_user_admin(request.user.idpersonne))
        student_id = request.POST['student_select']
        sujet.titre = request.POST['title']
        sujet.descriptif = request.POST['description']
        sujet.destination = request.POST['destination']
        sujet.fichier = request.FILES['file'] if bool(request.FILES) else None
        sujet.nbpersonnes = request.POST['nb_personnes']
        subject_is_taken = True if request.POST['student_select'] != '' else False

        sujet.save()

        if subject_is_taken:
            SelectionSujet(idetudiant=find_student_by_id_personne(student_id), idsujet=sujet).save()

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
def deleteTopic(request, sujet_id):
    sujet = get_object_or_404(Sujet, idsujet=sujet_id)
    selections = find_selection_by_id_sujet(sujet)
    for selection in selections:
        selection.delete()
    sujet.delete()
    return HttpResponseRedirect(request.GET.get('next'))


@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_or_superviseur_required
def add_topic(request, idue) -> HttpResponse:
    logger = logging.getLogger()
    user = request.user
    is_admin = is_user_admin(user.idpersonne)
    ue = find_ue(idue)
    if request.method == 'POST':
        form = SubmitForm(request.POST, request.FILES, list_students=find_students_of_ue(ue),
                          list_referent=find_supervisors_of_ue(ue).union(
                              Personne.objects.filter(idpersonne=find_owner_of_ue(ue).idpersonne)), is_admin=is_admin)

        #print(request.FILES['file'])

        titre = request.POST['title']
        descriptif = request.POST['description']
        destination = request.POST['destination']
        fichier = request.FILES['file'] if bool(request.FILES) else None
        student_id = request.POST['student_select']
        nb_personnes = request.POST['nb_personnes']
        logger.info("form is valid")
        subject_is_taken = True if student_id != '' else False
        if 'admin' in user.role['role']:
            referent_id = request.POST['referent_select']
            is_prof = True if find_owner_of_ue(ue) == find_personne_by_id(referent_id) else False
            if is_prof:
                prof = find_prof_by_id_personne(referent_id)
                sujet = Sujet(titre=titre, descriptif=descriptif, destination=destination, fichier=fichier, idprof=prof,
                              estpris=subject_is_taken, nbpersonnes=nb_personnes, idue=ue)
            else:
                sup = find_superviseur_by_id_personne(referent_id)
                sujet = Sujet(titre=titre, descriptif=descriptif, destination=destination, fichier=fichier,
                              idsuperviseur=sup, estpris=subject_is_taken, nbpersonnes=nb_personnes, idue=ue)

        elif 'professeur' in user.role['role']:
            prof = find_prof_by_id_personne(user.idpersonne)
            sujet = Sujet(titre=titre, descriptif=descriptif,
                          destination=destination, fichier=fichier,
                          idprof=prof, estpris=subject_is_taken, nbpersonnes=nb_personnes, idue=ue)
        else:
            superviseur = find_superviseur_by_id_personne(user.idpersonne)
            sujet = Sujet(titre=titre, descriptif=descriptif,
                          destination=destination, fichier=fichier,
                          idsuperviseur=superviseur, estpris=subject_is_taken, nbpersonnes=nb_personnes, idue=ue)

        sujet.save()

        if subject_is_taken:
            SelectionSujet(idetudiant=find_student_by_id_personne(student_id), idsujet=sujet).save()

        return HttpResponseRedirect("../")

    else:
        form = SubmitForm(list_students=find_students_of_ue(ue), list_referent=find_supervisors_of_ue(ue).union(
            Personne.objects.filter(idpersonne=find_owner_of_ue(ue).idpersonne)), is_admin=is_admin)

    context = {
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
def ok(request) -> HttpResponse:
    return render(request, "otherRole/ok.html", context={ok: 'Votre sujet a été validé'})


@login_required(login_url='/polls')
@csrf_exempt
def afficher_etapes_ue(request, idue) -> HttpResponse:
    ue = get_object_or_404(Ue, idue=idue)
    professeur = ue.idprof
    periode = professeur.idperiode
    etapes = Etape.objects.filter(idperiode=periode).order_by('delai')

    return render(request, 'otherRole/afficher_etapes_ue.html', {'etapes': etapes, 'Ue': idue})


@login_required(login_url='/polls')
def subscription(request) -> HttpResponse:
    user = request.user
    if 'etudiant' in user.role['role']:
        cours = find_course_for_student_for_subscription(user.idpersonne)
        courses = []
        for cours in cours:
            courses.append(cours)
        context = {
            'courses': courses
        }
        return render(request, 'otherRole/inscription.html', context)
    else:
        return redirect("../../home/")


@login_required(login_url='/polls')
def subscription_validation(request, idue, nom):
    user = request.user
    etudiant = Etudiant.objects.get(idpersonne=user.idpersonne)
    ue = Ue.objects.get(idue=idue)
    cours = Cours(idetudiant=etudiant, idue=ue, nom=nom)
    cours.save()
    return redirect("../../../home/")


@login_required(login_url='/polls')
@csrf_exempt
@student_required
def mycourses(request) -> HttpResponse:
    user = request.user
    courses_query = find_course_for_student(user.idpersonne)
    courses_ue = []
    if courses_query:
        for cours in courses_query:
            courses_ue.append(cours.idue)

    context = {
        'courses': courses_ue
    }
    return render(request, "otherRole/home.html", context=context)


@login_required(login_url='/polls')
@csrf_exempt
@is_student_of_ue
def mycourse(request, idue):
    user = request.user
    etudiant = find_student_by_id_personne(user.idpersonne)
    ue = find_ue(idue)
    etapes, etapes_ue = find_etapes_of_ue(ue)
    current_etape = find_current_etape_of_ue(ue)
    fichier_delivrable_instance = None
    form = None
    already_submitted = False
    # on part du principe que quand une étape ne contient pas de délivrable, c'est que c'est une étape de choix de sujet
    context_reservation = None
    topics_of_students = find_sujets_of_student_of_ue(find_student_by_id_personne(user.idpersonne), idue)
    if current_etape is not None and current_etape.iddelivrable_id is None:
        context_reservation = reservation_subject_student(idue, user.idpersonne)
    if current_etape.iddelivrable_id is not None:
        fichier_delivrable_instance = FichierDelivrable.objects.filter(
            iddelivrable=current_etape.iddelivrable_id,
            idetudiant=etudiant,
            rendu=True
        ).first()
        already_submitted = fichier_delivrable_instance is not None
        form = FichierDelivrableForm(
            instance=fichier_delivrable_instance) if fichier_delivrable_instance else FichierDelivrableForm()
        if request.method == 'POST':
            form = FichierDelivrableForm(request.POST, request.FILES, instance=fichier_delivrable_instance)
            if form.is_valid():
                fichier_delivrable = form.save(commit=False)
                fichier_delivrable.iddelivrable = get_object_or_404(Delivrable,
                                                                    iddelivrable=current_etape.iddelivrable_id)
                fichier_delivrable.idetudiant = etudiant
                fichier_delivrable.nom_personne = etudiant.idpersonne.nom
                fichier_delivrable.nom_cours = idue
                fichier_delivrable.annee_periode = current_etape.idperiode.annee
                fichier_delivrable.rendu = True
                fichier_delivrable.save()
                return redirect("page d'un cours", idue=ue.idue)

    context = {
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
def reservation(request, idue):
    user = request.user
    if "professeur" in user.role['role']:
        subjects_query = find_all_subjects_for_a_teacher(user.idpersonne)
        print(subjects_query)
        sujets = find_students_without_subjects_by_teacher(user.idpersonne)
        subjects = []
        for subject in subjects_query:
            subjects.append(subject)

        context = {
            'subjects': subjects,
            'subject_title': ["Titre", "Descriptif", "Á réserver"]
        }
        return render(request, "otherRole/reservation.html", context)
    else:
        return redirect('/polls')


@login_required(login_url='polls')
def knows_if_subject_is_booked_for_teacher(request, idue: str):
    user = request.user
    if "professeur" in user.role['role']:
        subjects_query = find_all_subjects_for_a_teacher(user.idpersonne)
        subjects_reserved = []
        for subject in subjects_query:
            nbPersonne = nb_people_keeping_for_a_sujet(subject)
            print(nbPersonne, subject.nbpersonnes)
            if nbPersonne < subject.nbpersonnes:
                personnesReservees = find_selection_by_id_sujet(subject)
                print(personnesReservees[0].idetudiant.idpersonne.nom)
                subjects_reserved.append(
                    {'sujet': subject, 'estReserve': True, 'personnesReservees': personnesReservees})
            else:
                subjects_reserved.append({'sujet': subject, 'estReserve': False})
        context = {
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
def booking(request, idue, idsujet):
    user = request.user
    if 'professeur' in user.role['role']:
        sujet = find_sujet_by_id(idsujet)
        initial_data = {
            'title': sujet.titre,
            'description': sujet.descriptif,
            'subject_id': idsujet,
            'students': find_students_without_subjects_by_teacher(user.idpersonne)
        }
        form = ConfirmationSujetReservation(initial=initial_data)
        nbPersonnes = nb_people_keeping_for_a_sujet(sujet)
        isAvalaible = nbPersonnes > 0
        context = {
            'form': form,
            'idsujet': idsujet,
            'isAvalaible': isAvalaible
        }
        return render(request, "otherRole/confirmationReservation.html", context=context)
    else:
        return redirect('../reservation')


def validation_booking(request, idue, idsujet):
    user = request.user
    if request.method == "POST" and "professeur" in user.role['role']:
        idstudent = request.POST.get('students')
        etudiant = find_student_by_id_etudiant(int(idstudent))
        sujet = find_sujet_by_id(idsujet)
        selectionSujet = SelectionSujet(idsujet=sujet, idetudiant=etudiant)
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
def vue_historique(request):
    # Subquery to get the names of students involved in the same topic
    student_names = SelectionSujet.objects.filter(
        idsujet__idue=OuterRef('idue'),
        is_involved=True,  # Only include students who are involved in the topic
    ).annotate(
        full_name=Concat('idetudiant__idpersonne__nom', Value(' '), 'idetudiant__idpersonne__prenom',
                         output_field=CharField()),
        mark=Subquery(FichierDelivrable.objects.filter(idetudiant=OuterRef('idetudiant')).values('note')[:1],
                      output_field=IntegerField())
    ).values('full_name', 'mark')

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
        mark=Subquery(FichierDelivrable.objects.filter(idetudiant=OuterRef('idetudiant')).values('note')[:1],
                      output_field=IntegerField()),
        nom_complet_professeur=Concat('idsujet__idprof__idpersonne__nom', Value(' '),
                                      'idsujet__idprof__idpersonne__prenom',
                                      output_field=CharField()),
    ).order_by('idsujet__idperiode__annee').distinct()

    queries = list(queryset)
    annees = list(set(query['annee_academique'] for query in queryset))
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
def etape_view(request, idue):
    ue = find_ue(idue)
    etapes, etapes_ue = find_etapes_of_ue(ue)

    if request.method == 'POST':
        form = EtapeForm(request.POST)
        if form.is_valid():
            etape = form.save(commit=False)
            etape.idperiode = ue.idprof.idperiode
            delivrable = None
            if 'typeFichier' in request.POST and request.POST['typeFichier'].strip():
                delivrable = find_delivrable_by_type(request.POST['typeFichier'])
                if delivrable is None:
                    delivrable = Delivrable()
                    typeFichier = request.POST['typeFichier']
                    delivrable.typeFichier = typeFichier
                    delivrable.save()

            etape.iddelivrable = delivrable
            etape.save()
            EtapeUe(idue=ue, idetape=etape).save()
            return HttpResponseRedirect(request.path)
    else:
        form = EtapeForm()

    return render(request, 'otherRole/commandTimeline.html',
                  {'form': form, 'etapes': etapes, 'ue': ue, 'etapes_ue': etapes_ue})


@login_required(login_url='/polls')
@is_student_of_ue
@student_required
@transaction.atomic
def confirmer_reservation_sujet(request, idue, idsujet):
    user = request.user
    etudiant = find_student_by_id_personne(user.idpersonne)
    sujet = get_subject_by_id(idsujet)
    if nb_people_keeping_for_a_sujet(sujet) == 1:
        sujet.estpris = True
    selectionSujet = SelectionSujet(idetudiant=etudiant, idsujet=sujet)
    selectionSujet.save()
    sujet.save()

    return HttpResponseRedirect(request.GET.get('next'))


@login_required(login_url='/polls')
@is_owner_of_ue_or_admin
def deleteStep(request, idue, idetape):
    etape = find_etape_by_id(idetape)
    etapeue = find_etapeue_by_idetape_and_ue(idetape, idue)
    if etapeue is not None and etape is not None:
        etapeue.delete()
        etape.delete()
    return HttpResponseRedirect("../")


@login_required(login_url='/polls')
@is_owner_of_ue_or_admin
def selectStep(request, idue, idetapeue):
    etapeue_to_select = find_etapeue_by_idetape_and_ue(idetapeue, idue)
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
def changeAccess(request, idue, val: bool):
    ue = find_ue(idue)
    ue.isopen = val
    ue.save()
    return JsonResponse({'succes': "ok"})


@login_required(login_url='/polls')
def back(request):
    return HttpResponseRedirect("../")


# ne pas mettre de décorateur pour cette fonction
def reservation_subject_student(idue, idpersonne):
    etudiant = find_student_by_id_personne(idpersonne)
    if count_subject_for_one_student_and_one_ue(etudiant.idetudiant, idue) == 0:
        sujets_query = find_sujets_by_idue(idue)
        sujets = []
        for sujet in sujets_query:
            nbPersonnesRestantes = nb_people_keeping_for_a_sujet(sujet)
            sujets.append(
                {'sujet': sujet, 'nbPersonnesRestantes': nbPersonnesRestantes, 'nbPersonnes': sujet.nbpersonnes})
        if len(sujets) > 0:
            context = {
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


def archivage(request, idue):
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
        delivrable_links=Subquery(
            FichierDelivrable.objects.filter(idetudiant=OuterRef('idetudiant')).order_by('-iddelivrable').values(
                'fichier').values('fichier')),
    ).order_by('idsujet__idperiode__annee').distinct()

    queries = list(queryset)
    print(queries)
    titles = ['Année académique', 'Nom du cours', 'Titre du sujet', 'Description du sujet', 'Note Attribuée',
              'Nom complet de l\'étudiant', 'Professeur.e.s', 'Lien vers le délivrable']
    context = {'queryset': queries, 'title': f"Archivage des sujets", 'archivage': True, 'titles': titles}
    return render(request, "otherRole/historique.html", context=context)


@login_required(login_url='/polls')
def deliverable_file(request, idue, path):
    deliverable = get_object_or_404(FichierDelivrable, fichier=path)
    return FileResponse(deliverable.fichier)
