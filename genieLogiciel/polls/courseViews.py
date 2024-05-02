import logging, json
from multiprocessing import Value
from multiprocessing.managers import BaseManager

from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .forms import SubmitForm, UpdateForm, EtapeForm, SubjectReservationForm, ConfirmationSujetReservation
from .models import Sujet, Etudiant, Ue, Cours, Etape, Delivrable
from .queries import *

from .restrictions import *
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
            'etudiants': [],
            'estPris': sujet.estpris
        }

        if sujet.estpris:
            etudiants = SelectionSujet.objects.filter(idsujet=sujet.idsujet)
            etudiants_noms = [f"{etudiant.idetudiant.idpersonne.nom} {etudiant.idetudiant.idpersonne.prenom}" for etudiant in etudiants]
            sujet_info['etudiants'] = etudiants_noms
            print(etudiants_noms)



        sujet_infos.append(sujet_info)
        print(sujet_info['estPris'])

    return render(request, "otherRole/topic.html", {'sujet_infos': sujet_infos, 'ue': ue})

@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_or_superviseur_required
def new(request, idue) -> HttpResponse:
    ue = find_ue(idue=idue)
    # Récupérer tous les sujets associés à cette ue
    sujets = Sujet.objects.filter(idue=ue)
    # exemple of years: [(2023,[[S1],[S2]]),(2024,[S3])]
    years = []
    for sujet in sujets:
        if not sujet.estpris:
            sujet_info = [
                sujet.titre,
                sujet.descriptif]
            year_sujet = Periode.objects.filter(idperiode=sujet.idperiode.idperiode).values()[0].get('annee')
            is_year = False
            for year in years:
                if year_sujet == year[0]:
                    year[1].append([sujet_info])
                    is_year = True
                    break
            if not is_year:
                years.append((year_sujet,[[sujet_info]]))
    return render(request, "otherRole/ReuseSubject.html", {'years' : years, 'ue' : ue})

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
    selections = find_selection_by_id_sujet(sujet)
    for selection in selections:
        selection.delete()
    sujet.delete()
    return redirect("topics", code=id_ue)





@login_required(login_url='/polls')
@csrf_exempt
@admin_or_professor_or_superviseur_required
def add_topic(request, idue) -> HttpResponse:
    logger = logging.getLogger()
    user = request.user
    is_admin = is_user_admin(user.idpersonne)
    ue = find_ue(idue)
    if request.method == 'POST':
        form = SubmitForm(request.POST, request.FILES, list_students=find_students_of_ue(ue), list_referent=find_supervisors_of_ue(ue).union(Personne.objects.filter(idpersonne = find_owner_of_ue(ue).idpersonne)), is_admin=is_admin)

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
                sujet = Sujet(titre=titre, descriptif=descriptif, destination=destination, fichier=fichier, idprof=prof, estpris=subject_is_taken, nbpersonnes=nb_personnes, idue=ue)
            else:
                sup = find_superviseur_by_id_personne(referent_id)
                sujet = Sujet(titre=titre, descriptif=descriptif, destination=destination, fichier=fichier, idsuperviseur=sup, estpris=subject_is_taken, nbpersonnes=nb_personnes, idue=ue)

        elif 'professeur' in user.role['role']:
            prof = find_prof_by_id_personne(user.idpersonne)
            sujet = Sujet(titre=titre, descriptif=descriptif,
                          destination=destination, fichier=fichier,
                          idprof=prof, estpris=subject_is_taken, nbpersonnes=nb_personnes, idue=ue)
        else:
            superviseur = find_superviseur_by_id_personne(user.idpersonne)
            sujet = Sujet(titre=titre, descriptif=descriptif,
                          destination=destination, fichier=fichier,
                          idsuperviseur=superviseur,estpris=subject_is_taken,nbpersonnes=nb_personnes,idue=ue)

        sujet.save()

        if subject_is_taken :
            SelectionSujet(idetudiant=find_student_by_id_personne(student_id), idsujet=sujet).save()

        return HttpResponseRedirect("../")

    else:
        form = SubmitForm(list_students=find_students_of_ue(ue), list_referent=find_supervisors_of_ue(ue).union(Personne.objects.filter(idpersonne = find_owner_of_ue(ue).idpersonne)), is_admin=is_admin)

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
    ue = find_ue(idue)
    etapes, etapes_ue = find_etapes_of_ue(ue)
    current_etape = find_current_etape_of_ue(ue)

    # on part du principe que quand une étape ne contient pas de délivrable, c'est que c'est une étape de choix de sujet
    context_reservation = None
    if current_etape is not None and current_etape.iddelivrable_id is None:
        context_reservation = reservation_subject_student(idue, user.idpersonne)

    context = {
        'ue': ue,
        'is_student': True,
        'etapes': etapes,
        'etapes_ue': etapes_ue,
        'current_etape': current_etape,
        'context_reservation': context_reservation
        }
    return render(request, "course.html", context=context)


@login_required(login_url='polls')
@prof_or_superviseur_required
def reservation(request):
    user = request.user
    if "professeur" in user.role['role']:
        subjects_query = find_all_subjects_for_a_teacher(user.idpersonne)
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
            'students': find_students_by_teacher_without_subject(user.idpersonne)
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
        etudiant = find_student_by_id_etudiant(int(idstudent))
        selectionSujet = SelectionSujet(idsujet=idsujet, idetudiant=etudiant)
        selectionSujet.save()
        sujet = find_sujet_by_id(idsujet)
        sujet.estPris = True
        sujet.save()
        return redirect('../../../home')
    else:
        return redirect('../../../ok')


from django.db.models import CharField, Value  # cet import, pour gérer l'espace entre pnom et nom


@login_required(login_url='/polls')
def vue_historique(request):
    queryset = (
        Cours.objects.values(
            annee_academique=F('idue__idprof__idperiode__annee'),
            nom_cours=F('nom'),
            titre_sujet=F('idue__sujet__titre'),
            description_sujet=F('idue__sujet__descriptif'),
            nom_complet_etudiant=Concat('idetudiant__idpersonne__nom', Value(' '), 'idetudiant__idpersonne__prenom',
                                        output_field=CharField()),
            nom_complet_professeur=Concat('idue__idprof__idpersonne__nom', Value(' '),
                                          'idue__idprof__idpersonne__prenom', output_field=CharField()),
        ).order_by('idue__idprof__idperiode__annee')
    )
    queries = []
    for query in queryset:
        queries.append(query)
    annees = []
    for query in queryset:
        annees.append(int(query['annee_academique']))
    annees = remove_duplicates(annees)

    return render(request, "otherRole/historique.html", context={'queryset': queries, 'annees': annees})


@login_required(login_url='/polls')
def vue_historique_annee(request, annee):
    queryset = (
        Cours.objects.filter(
            idue__idprof__idperiode__annee=annee
        ).values(
            annee_academique=F('idue__idprof__idperiode__annee'),
            nom_cours=F('nom'),
            titre_sujet=F('idue__sujet__titre'),
            description_sujet=F('idue__sujet__descriptif'),
            nom_complet_etudiant=Concat('idetudiant__idpersonne__nom', Value(' '), 'idetudiant__idpersonne__prenom',
                                        output_field=CharField()),
            nom_complet_professeur=Concat('idue__idprof__idpersonne__nom', Value(' '),
                                          'idue__idprof__idpersonne__prenom', output_field=CharField()),
        ).order_by('idue__idprof__idperiode__annee'))
    querries = []
    for querry in queryset:
        querries.append(querry)
    return render(request, "otherRole/historique.html", context={'queryset': querries})
@login_required(login_url='polls')
@is_owner_of_ue_or_admin
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

    return render(request, 'otherRole/commandTimeline.html', {'form': form, 'etapes': etapes, 'ue': ue, 'etapes_ue': etapes_ue})


# @student_required
# def reservation_subject_student(request, idue, idpersonne):
#     etudiant = find_student_by_id_personne(idpersonne)
#     if count_subject_for_one_student_and_one_ue(etudiant.idetudiant, idue) == 0:
#         sujets_query = find_sujets_by_idue(idue)
#         sujets = []
#         for sujet in sujets_query:
#             nbPersonnesRestantes = nb_people_keeping_for_a_sujet(sujet)
#             sujets.append({'sujet':sujet, 'nbPersonnesRestantes':nbPersonnesRestantes, 'nbPersonnes':sujet.nbpersonnes})
#         if len(sujets) > 0:
#             context = {
#                 'titles': ['Titre', 'Description', 'Professeur/Superviseur', 'Nombre de personnes','Réserver'],
#                 'sujets': sujets,
#                 'idue': idue
#             }
#         else:
#             context = {
#                 'failure': "Vous ne pouvez plus réserver de sujet pour ce cours"
#             }
#     else:
#         context = {
#             'failure': "Vous ne pouvez plus réserver de sujet pour ce cours"
#         }
#     return render(request, "otherRole/reservationSujet.html", context=context)


def reservation_subject_student(idue, idpersonne):
    etudiant = find_student_by_id_personne(idpersonne)
    if count_subject_for_one_student_and_one_ue(etudiant.idetudiant, idue) == 0:
        sujets_query = find_sujets_by_idue(idue)
        sujets = []
        for sujet in sujets_query:
            nbPersonnesRestantes = nb_people_keeping_for_a_sujet(sujet)
            sujets.append({'sujet':sujet, 'nbPersonnesRestantes':nbPersonnesRestantes, 'nbPersonnes':sujet.nbpersonnes})
        if len(sujets) > 0:
            context = {
                'titles': ['Titre', 'Description', 'Professeur/Superviseur', 'Nombre de personnes','Réserver'],
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

    return redirect('/polls/course/mycourses')

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
def changeAccess(request, idue, val:bool):
    ue = find_ue(idue)
    ue.isopen = val
    ue.save()
    return JsonResponse({'succes': "ok"})

@login_required(login_url='/polls')
def back(request):
    return HttpResponseRedirect("../")