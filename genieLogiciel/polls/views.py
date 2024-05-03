import json
from datetime import datetime
from typing import Type

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from .models import Delivrable, Etudiant, FichierDelivrable
from .queries import *
from django.views.decorators.csrf import csrf_exempt
from .forms import ConnectForm, FichierDelivrableForm, SubscriptionForm
from .restrictions import *
from .utils.date import get_today_date
from .mailNotification import sendMail


# Handle error pages
def page_not_found(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def server_error(request, exception=None):
    return render(request, 'errors/500.html', status=500)

def permission_denied(request, exception=None):
    return render(request, 'errors/403.html', status=403)


# obliger de passer tous les élements nécessaires dans le context donc, attention aux id
@login_required(login_url='/polls')
@prof_or_superviseur_or_student_required
def accueil(request) -> HttpResponse:
    user = request.user
    if "professeur" in user.role["role"] or "superviseur" in user.role['role'] or "etudiant" in user.role['role']:
        context = {
            'user': user
        }
        return render(request, "otherRole/otherRole.html", context=context)
    else:
        return redirect('/polls')


@login_required(login_url='/polls')
@prof_or_superviseur_or_student_required
def home(request) -> HttpResponse:
    user = request.user
    courses = []
    role = user.role['view']
    if role == "professeur":
        get_courses = find_courses_by_professeur(user.idpersonne)
        courses = get_courses
    elif role == "superviseur":
        get_courses = find_courses_by_supervisor(user.idpersonne)
        courses = get_courses
    else:
        course = find_course_for_student(user.idpersonne)
        courses.append(course)
    sideBar = not ('professeur' in role or "superviseur" in role)
    context = {
        'courses': courses,
        'noSideBar': sideBar
    }

    return render(request, 'otherRole/home.html', context)


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
def course(request, idue) -> HttpResponse:
    user = request.user
    ue = find_ue(idue)
    print(idue)
    etapes, etapes_ue = find_etapes_of_ue(ue)
    is_owner = False
    is_admin = False
    if user == find_owner_of_ue(ue):
        is_owner = True
    elif 'admin' in user.role['role']:
        is_admin = True

    context = {
        "user": user,
        "ue": ue,
        "is_owner": is_owner,
        "is_admin": is_admin,
        "etapes": etapes,
        "etapes_ue": etapes_ue
    }

    return render(request, 'course.html', context)


@csrf_exempt
def login(request) -> HttpResponse:
    if request.method == 'POST':
        form = ConnectForm(request.POST)
        if form.is_valid():
            user = authenticate(request, mail=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None and user.is_authenticated:
                auth_login(request, user)
                if 'admin' in user.role['role'] and user.role['view'] == 'admin':
                    return HttpResponseRedirect(redirect_to="admin/")
                else:
                    #sendMail("Connexion Réussie", f"Vous vous êtes connecté à la plateforme PIMS le {get_today_date()}")
                    return HttpResponseRedirect(redirect_to="home/")
            else:
                form = ConnectForm()
    else:
        form = ConnectForm()
    context = {
        "form": form
    }
    return render(request, 'login.html', context)


@login_required(login_url='/polls')
def logout(request):
    #user = request.user
    #sendMail("Déconnexion réussie", f"Vous vous êtes déconnecté de la plateforme PIMS le {get_today_date()}")

    auth_logout(request)
    return redirect('/polls')


def yes(request):
    return render(request, 'suivi.html', {})


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
def fiche(request, idpersonne):
    user = request.user
    personne = find_personne_by_id(idpersonne)
    if "professeur" in personne.role['role']:
        specific_role = find_professeur_by_id_personne(idpersonne)
    elif "etudiant" in personne.role['role']:
        specific_role = find_student_by_id_personne(idpersonne)
    context = {
        'user': user,
        'personne': personne,
        'specific_role': specific_role,
        'noSideBar': 'true'
    }
    return render(request, 'otherRole/fiche.html', context)


@login_required(login_url='/polls')
@admin_or_professor_required
def switchRole(request, role):
    user = request.user
    redirect_url = ""
    if role == "admin":
        redirect_url = "/polls/admin/"
    elif role == "professeur" or role == "superviseur":
        redirect_url = "/polls/course/"

    user.role['view'] = role
    user.save()

    return HttpResponseRedirect(redirect_to=redirect_url)


@login_required(login_url='/polls')
def echeance_and_upload(request, idcours=None, idperiode=None, delivrable_id=None):
    user = request.user
    if 'etudiant' not in user.role['role']:
        return HttpResponse("Unauthorized", status=401)

    etudiant = find_student_by_id_personne(user.idpersonne)
    sujets = find_sujet_by_id_etudiant(etudiant)
    courses = find_course_by_student(user.idpersonne)
    elements = []

    for sujet, course in zip(sujets, courses):
        delais = []
        delais_query = find_delais_by_sujet(sujet)
        for delai in delais_query:
            fichier_delivrable_instance = FichierDelivrable.objects.filter(
                iddelivrable=delai.iddelivrable,
                idetudiant=etudiant,
                rendu=True
            ).first()

            form = FichierDelivrableForm(instance=fichier_delivrable_instance) if fichier_delivrable_instance else FichierDelivrableForm()

            if delivrable_id == delai.iddelivrable.iddelivrable and request.method == 'POST':
                form = FichierDelivrableForm(request.POST, request.FILES, instance=fichier_delivrable_instance)
                if form.is_valid():
                    fichier_delivrable = form.save(commit=False)
                    fichier_delivrable.iddelivrable = get_object_or_404(Delivrable, iddelivrable=delivrable_id)
                    fichier_delivrable.idetudiant = etudiant
                    fichier_delivrable.nom_personne = etudiant.idpersonne.nom
                    fichier_delivrable.nom_cours = course.idue_id
                    fichier_delivrable.annee_periode = sujet.idperiode.annee
                    fichier_delivrable.rendu = True
                    fichier_delivrable.save()
                    return redirect('echeance_and_upload')

            already_submitted = fichier_delivrable_instance is not None
            delais.append({
                'delai': delai,
                'form': form,
                'already_submitted': already_submitted,
            })

        elements.append({'periode': sujet.idperiode, 'course': course, 'delais': delais})

    context = {
        'elements': elements,
        'current_date': datetime.now().date(),
    }
    return render(request, 'otherRole/echeance.html', context)



@login_required(login_url='/polls')
def profile(request):
    user = personne = request.user
    context = {
        'user': user,
        'personne': personne,
        'noSideBar': 'true'
    }
    return render(request, 'otherRole/fiche.html', context)


@csrf_exempt
def subscription(request) -> HttpRequest:
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            mail = form.cleaned_data['mail']
            isUser = is_existing_personne_by_email(mail)
            if isUser:
                return redirect("/polls/login")
            else:
                default_role = {"role": ["etudiant"], "view": "etudiant"}
                hashedpassword = make_password(form.cleaned_data['password'])
                personne = create_personne(
                    nom=form.cleaned_data['nom'],
                    prenom=form.cleaned_data['prenom'],
                    email=mail,
                    password=hashedpassword,
                    role=default_role
                )
                personne.save()
                etudiant = create_etudiant(
                    form.cleaned_data['bloc'],
                    personne
                )
                etudiant.save()
                authenticate(request, mail=mail, password=form.cleaned_data['password'])
                auth_login(request, personne)
                return redirect("/polls/home")


    else:
        form = SubscriptionForm()
    context = {
        "form": form,
        "noSideBar": "true"
    }
    return render(request, 'subscribe.html', context)


def create_personne(nom: str, prenom: str, email: str, password: str, role) -> Personne:
    personne = Personne(nom=nom, prenom=prenom, mail=email, password=password, role=role)
    return personne


def create_etudiant(bloc: str, personne: Personne) -> Etudiant:
    etudiant = Etudiant(bloc=bloc, idpersonne=personne)
    return etudiant


@login_required(login_url='/polls')
def desinscription(request) -> HttpResponse:
    user = request.user
    if "etudiant" in user.role['role']:
        courses_query = find_course_for_student(user.idpersonne)
        courses = []
        for course in courses_query:
            courses.append(course)
        if len(courses) == 0:
            context = {
                'failure': 'Vous n\'êtes inscrit à aucun cours, donc ce n\'est pas possible de vous désinscrire'
            }
        else:
            context = {
                'courses': courses,
                'desinscription': True
            }
        return render(request, 'otherRole/home.html', context)
    else:
        return redirect('/polls/home')


@login_required(login_url='/polls')
@student_required
def desinscription_validation(request, idcours: int) -> HttpResponse:
    user = request.user
    print("cc")
    if "etudiant" in user.role['role']:
        cours = find_course_by_id(idcours)
        student = find_student_by_id_personne(user.idpersonne)
        selections = find_selection_by_id_etudiant(student.idetudiant)

        if selections is not None:
            for selection in selections:
                if count_selection_for_one_subject(selection.idsujet_id) == 0:
                    selections.idsujet.estpris = False
                selection.delete()

        cours.delete()
        return redirect('/polls/home')
    else:
        return redirect('/polls/home')

@login_required(login_url='/polls')
@is_owner_of_ue_or_admin
def desinscription_etudiant(request, idpersonne, idue) -> HttpResponse:
    etudiant = find_student_by_id_personne(idpersonne)
    sujets = find_sujets_of_student_of_ue(idpersonne, idue)
    cours = Cours.objects.get(idetudiant=etudiant, idue=idue)
    # On libère les sujets réservés par l'étudiant
    if sujets is not None:
        for sujet in sujets:
            sujet.estpris = False
            selections = find_selection_by_id_sujet(sujet)
            for selection in selections:
                selection.delete()
            sujet.save()

    cours.delete()
    return redirect('/polls/course/' + idue + '/participants/')


