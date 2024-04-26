import logging
from multiprocessing import Value
from multiprocessing.managers import BaseManager

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .forms import SubmitForm, UpdateForm, EtapeForm, SubjectReservationForm, ConfirmationSujetReservation
from .models import Sujet, Etudiant, Ue, Cours, Etape, Delivrable
from .queries import *

from .restrictions import *


@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_required
def topics(request, idue) -> HttpResponse:
    ue = get_ue(idue=idue)
    # Récupèrer tous les sujets associés à cette ue
    sujets = Sujet.objects.filter(idue=ue)
    sujet_infos = []
    for sujet in sujets:
        sujet_info = {
            'id': sujet.idsujet,
            'titre': sujet.titre,
            'description': sujet.descriptif,
            'etudiants': [],
            'estPris': sujet.estpris
        }

        if sujet.estpris:
            etudiants = [Sujet.objects.get(idsujet=sujet.idsujet).idetudiant]
            etudiants_noms = [f"{etudiant.idpersonne.nom} {etudiant.idpersonne.prenom}" for etudiant in etudiants]
            sujet_info['etudiants'] = etudiants_noms

        sujet_infos.append(sujet_info)

    return render(request, "otherRole/topic.html", {'sujet_infos': sujet_infos, 'ue': ue})


@login_required(login_url='/polls')
@csrf_exempt
@prof_or_superviseur_required
def myTopics(request, idue) -> HttpResponse:
    user = request.user
    ue = get_ue(idue=idue)
    if 'professeur' in user.role['role']:
        # Récupèrer tous les sujets associés à ces cours
        sujets = Sujet.objects.filter(idue=ue, idprof=get_prof_by_id_personne(user.idpersonne).idprof)
    else:
        sujets = get_subject_for_a_superviseur(user.idpersonne)
    sujet_infos = []
    for sujet in sujets:
        sujet_info = {
            'id': sujet.idsujet,
            'titre': sujet.titre,
            'description': sujet.descriptif,
            'etudiants': [],
            'estPris': sujet.estpris
        }

        if sujet.estpris:
            etudiants = [Sujet.objects.get(idsujet=sujet.idsujet).idetudiant]
            etudiants_noms = [f"{etudiant.idpersonne.nom} {etudiant.idpersonne.prenom}" for etudiant in etudiants]
            sujet_info['etudiants'] = etudiants_noms

        sujet_infos.append(sujet_info)

    return render(request, "otherRole/topic.html", {'sujet_infos': sujet_infos, 'ue': ue})


@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_or_superviseur_required
@is_owner_of_ue_or_admin
def participants(request, idue) -> HttpResponse:
    ue = get_ue(idue)
    students = get_students_of_ue(ue)
    professors = get_owner_of_ue(ue)
    supervisors = get_supervisors_of_ue(ue)
    return render(request, "otherRole/participants.html",
                  context={"students": students, "professors": professors, "supervisors": supervisors, "ue": ue})


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
@csrf_exempt
def editTopic(request, sujet_id):
    sujet = get_object_or_404(Sujet, idsujet=sujet_id)
    id_ue = sujet.idCours.idue.idue
    if request.method == 'POST':
        form = UpdateForm(request.POST, request.FILES)
        if form.is_valid():
            sujet.titre = form.cleaned_data['title']
            sujet.descriptif = form.cleaned_data['description']
            sujet.destination = form.cleaned_data['destination']
            if 'file' in request.FILES:
                sujet.file = request.FILES['file']
            sujet.save()
            return redirect("topics", code=id_ue)
    else:
        form_data = {
            'title': sujet.titre,
            'description': sujet.descriptif,
            'destination': sujet.destination,
        }

        form = UpdateForm(initial=form_data)

    return render(request, 'otherRole/edit_sujet.html', {'form': form, 'Ue': sujet.idCours.idue.idue})


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
@csrf_exempt
def deleteTopic(request, sujet_id):
    sujet = get_object_or_404(Sujet, idsujet=sujet_id)
    id_ue = sujet.idCours.idue.idue
    sujet.delete()
    return redirect("topics", code=id_ue)





@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_or_superviseur_required
def addTopic(request, idue) -> HttpResponse:
    logger = logging.getLogger()
    user = request.user
    is_admin = is_user_admin(user.idpersonne)
    ue = get_ue(idue)
    if request.method == 'POST':
        form = SubmitForm(request.POST, request.FILES, list_students=get_students_of_ue(ue), list_referent=get_owner_of_ue(ue) | get_supervisors_of_ue(ue), is_admin=is_admin)
        if form.is_valid():
            logger.info("form is valid")
            subject_is_taken = False
            print(form.cleaned_data['student_select'])
            if 'professeur' in user.role['role']:
                prof = get_prof_by_id_personne(user.idpersonne)
                sujet = Sujet(titre=form.cleaned_data['title'], descriptif=form.cleaned_data['description'],
                              destination=form.cleaned_data['destination'], fichier=form.cleaned_data['file'],
                              idprofesseur=prof)
            else:
                superviseur = get_superviseur_by_id_personne(user.idpersonne)
                sujet = Sujet(titre=form.cleaned_data['title'], descriptif=form.cleaned_data['description'],
                              destination=form.cleaned_data['destination'], fichier=form.cleaned_data['file'],
                              idsuperviseur=superviseur)

            sujet.save()

            return HttpResponseRedirect(f"polls/course/{idue}")
        else:
            print(form.errors)
    else:
        form = SubmitForm(list_students=get_students_of_ue(ue), list_referent=get_owner_of_ue(ue) | get_supervisors_of_ue(ue), is_admin=is_admin)

    context = {
        'ue': ue,
        'title': 'Cours',
        'prenom': "Matthys",
        'role': "Etudiant",
        "form": form,
        'is_admin': is_admin,
    }
    return render(request, 'otherRole/submitSubject.html', context)


@login_required(login_url="/polls")
@csrf_exempt
def ok(request) -> HttpResponse:
    return render(request, "otherRole/ok.html", context={ok: 'Votre sujet a été validé'})


@login_required(login_url='/polls')
@csrf_exempt
@is_owner_of_ue_or_admin
def gestion_etape(request, idue):
    ue = get_object_or_404(Ue, idue=idue)
    if request.method == 'POST':
        form = EtapeForm(request.POST)
        if form.is_valid():
            etape = form.save(commit=False)
            etape.idPeriode = ue.idprof.idperiode
            delivrable = Delivrable()
            if 'typeFichier' in request.POST and request.POST['typeFichier'].strip():
                typeFichier = request.POST['typeFichier']
                delivrable.typeFichier = typeFichier
            delivrable.save()
            etape.idDelivrable = delivrable
            etape.save()
            return redirect("topics", code=idue)
    else:
        form = EtapeForm()

    return render(request, 'otherRole/gestion_etape.html', {'form': form, 'ue': ue})


@login_required(login_url='/polls')
@csrf_exempt
def afficher_etapes_ue(request, idue)->HttpResponse:
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
        print(courses[0].nom, courses[1].nom)
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
def mycourses(request):
    user = request.user
    courses_query = find_course_for_student(user.idpersonne)
    courses_ue = []
    if courses_query:
        for cours in courses_query:
            courses_ue.append(cours.idue)
    print(courses_ue)
    context = {
        'courses': courses_ue
    }
    return render(request, "otherRole/home.html", context=context)


@login_required(login_url='polls')
@prof_or_superviseur_required
def reservation(request):
    user = request.user
    if "professeur" in user.role['role']:
        subjects_query = get_all_subjects_for_a_teacher(user.idpersonne)
        subjects = []
        for subject in subjects_query:
            subjects.append(subject)
        # permet de créer des champs qui sont faux pour le formulaire
        form_list = [SubjectReservationForm(instance=sujet, initial={'subject_id': sujet.idsujet}) for sujet in
                     subjects]
        context = {
            'subjects': form_list,
            'subject_title': ["Titre", "Descriptif", "Á réserver"]
        }
        return render(request, "otherRole/reservation.html", context)
    else:
        return redirect('/polls')


@login_required(login_url='polls')
@prof_or_superviseur_required
@csrf_exempt
# pas besoin de validation vu que le formulaire est supposé correcte suit à l'envoi précédent
def booking(request, idsujet):
    user = request.user
    if request.method == "POST" and 'professeur' in user.role['role']:
        initial_data = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'subject_id': idsujet,
            'students': get_students_by_teacher_without_subject(user.idpersonne)
        }
        form = ConfirmationSujetReservation(initial=initial_data)
        context = {
            'form': form,
            'idsujet': idsujet
        }
        return render(request, "otherRole/confirmationReservation.html", context=context)


    else:
        return redirect('../reservation')


def validation_booking(request, idsujet):
    user = request.user
    if request.method == "POST" and "professeur" in user.role['role']:
        idstudent = request.POST.get('students')
        etudiant = get_student_by_id_etudiant(int(idstudent))
        etudiant.idsujet_id = idsujet
        etudiant.save()
        sujet = get_subject(idsujet)
        sujet.estPris = True
        sujet.save()
        return redirect('../../../home')
    else:
        return redirect('../../../ok')


def vue_historique(request):
    queryset = (
        Cours.objects
        .values(
            annee_academique=F('sujet__idperiode__annee'),
            nom_cours=F('nom'),
            titre_sujet=F('sujet__titre'),
            description_sujet=F('sujet__descriptif'),
            nom_complet_etudiant=Concat('idetudiant__idpersonne__nom', 'idetudiant__idpersonne__prenom'),
            nom_complet_professeur=Concat('sujet__idprof__idpersonne__nom',
                                          'sujet__idprof__idpersonne__prenom'),
        )
        .order_by('sujet__idperiode__annee', 'nom')
    )
    queries = []
    for query in queryset:
        queries.append(query)
    return render(request, "otherRole/ok.html", context={'queryset': queries})


@login_required(login_url='polls')
def etape_view(request):
    etapes = Etape.objects.all().values('description', 'delai')
    return render(request, 'otherRole/commandTimeline.html', {'etapes': etapes})


@student_required
def reservation_subject_student(request, idue, idpersonne):
    etudiant = find_student_by_id_personne(idpersonne)
    if count_subject_for_one_student_and_one_ue(etudiant.idetudiant, idue) == 0:
        sujets_query = get_sujets_by_idue(idue)
        sujets = []
        for sujet in sujets_query:
            sujets.append(sujet)
        context = {
            'titles': ['Titre', 'Description', 'Professeur/Superviseur', 'Réserver'],
            'sujets': sujets,
            'idue': idue
        }

    else:
        context = {
            'failure': "Vous ne pouvez plus réserver de sujet pour ce cours"
        }
        print(context)
    return render(request, "otherRole/reservationSujet.html", context=context)


@student_required
@transaction.atomic
def confirmer_reservation_sujet(request, idue, idsujet):
    user = request.user
    etudiant = find_student_by_id_personne(user.idpersonne)
    sujet = get_subject_by_id(idsujet)
    sujet.estpris = True
    sujet.idetudiant = etudiant
    sujet.save()

    return redirect('/polls/course/mycourses')
