import json
from datetime import datetime
from typing import Type

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Delivrable, Etudiant, FichierDelivrable
from .queries import *
from django.views.decorators.csrf import csrf_exempt
from .forms import ConnectForm, FichierDelivrableForm, SubscriptionForm
from .restrictions import *


# Handle error pages
def page_not_found(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Page d'erreur 404
    :param request: La requête http courante
    :param exception: L'exception levée renvoyant à la page d'erreur appropriée
    :return: La page html de l'erreur 404
    """
    return render(request, 'errors/404.html', status=404)


def server_error(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Page d'erreur 500
    :param request: La requête http courante
    :param exception: L'exception levée renvoyant à la page d'erreur appropriée
    :return: La page html de l'erreur 500
    """
    return render(request, 'errors/500.html', status=500)


def permission_denied(request: HttpRequest, exception=None) -> HttpResponse:
    """
    Page d'erreur 403
    :param request: La requête http courante
    :param exception: L'exception renvoyant à la page d'erreur appropriée
    :return: La page html de l'erreur 403
    """
    return render(request, 'errors/403.html', status=403)


# obliger de passer tous les élements nécessaires dans le context donc, attention aux id
@login_required(login_url='/polls')
@prof_or_superviseur_or_student_required
def accueil(request) -> HttpResponse:
    """
    Page d'accueil de l'application
    :param request: La requête http courante
    :return: La page d'accueil quand l'utilisateur est connecté en fonction de son rôle
    """
    user = request.user
    if "professeur" in user.role["role"] or "superviseur" in user.role['role'] or "etudiant" in user.role['role']:
        context: dict[str, Any] = {
            'user': user
        }
        return render(request, "otherRole/otherRole.html", context=context)
    else:
        return redirect('/polls')


@login_required(login_url='/polls')
@prof_or_superviseur_or_student_required
def home(request) -> HttpResponse:
    """
    Page d'accueil de l'application qui affiche les différentes possibilités en fonction du rôle de l'utilisateur
    :param request: La requête http courante
    :return: La page html de l'accueil de l'application
    """
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
def course(request, idue: str) -> HttpResponse:
    """
    Page d'accueil d'un cours pour un professeur, superviseur ou admin
    :param request: La requête http courante
    :param idue: l'ue du cours concerné
    :return: La page html du cours
    """
    user = request.user
    ue: Ue = find_ue(idue)
    etapes, etapes_ue = find_etapes_of_ue(ue)
    is_owner: bool = False
    is_admin: bool = False
    if user == find_owner_of_ue(ue):
        is_owner = True
    elif 'admin' in user.role['role']:
        is_admin = True

    context: dict[str, Any] = {
        "user": user,
        "ue": ue,
        "is_owner": is_owner,
        "is_admin": is_admin,
        "etapes": etapes,
        "etapes_ue": etapes_ue
    }

    return render(request, 'course.html', context)


@csrf_exempt
def login(request: HttpRequest) -> HttpResponse:
    """
    Page contenant le formulaire de connexion, d'authentification
    :param request: La requête http courante
    :return: La page html de connexion
    """
    if request.method == 'POST':
        form: ConnectForm = ConnectForm(request.POST)
        if form.is_valid():
            user = authenticate(request, mail=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None and user.is_authenticated:
                auth_login(request, user)
                if 'admin' in user.role['role'] and user.role['view'] == 'admin':
                    return HttpResponseRedirect(redirect_to="admin/")
                else:
                    # sendMail("Connexion Réussie", f"Vous vous êtes connecté à la plateforme PIMS le {
                    # get_today_date()}")
                    return HttpResponseRedirect(redirect_to="home/")
            else:
                form = ConnectForm()
    else:
        form = ConnectForm()
    context: dict[str, ConnectForm] = {
        "form": form
    }
    return render(request, 'login.html', context)


@login_required(login_url='/polls')
def logout(request) -> HttpResponseRedirect:
    """
    Déconnexion de l'utilisateur
    :param request: La requête http courante
    :return: Redirection vers le formulaire de connexion
    """
    #user = request.user
    #sendMail("Déconnexion réussie", f"Vous vous êtes déconnecté de la plateforme PIMS le {get_today_date()}")

    auth_logout(request)
    return redirect('/polls')


@login_required(login_url='/polls')
@admin_or_professor_or_superviseur_required
def fiche(request, idpersonne: int) -> HttpResponse:
    """
    Page de fiche d'une personne
    :param request: Requête http courante
    :param idpersonne: l'id de la personne
    :return: La page html de la fiche de la personne
    """
    user = request.user
    personne: Personne = find_personne_by_id(idpersonne)
    if "professeur" in personne.role['role']:
        specific_role = find_professeur_by_id_personne(idpersonne)
    elif "etudiant" in personne.role['role']:
        specific_role = find_student_by_id_personne(idpersonne)
    context = {
        'user': user,
        'personne': personne,
        'specific_role': specific_role,
        'noSideBar': True
    }
    return render(request, 'otherRole/fiche.html', context)


@login_required(login_url='/polls')
@admin_or_professor_required
def switchRole(request, role: str) -> HttpResponseRedirect:
    """
    Fonction permettant de changer de rôle
    :param request: La requête http courante
    :param role: Le rôle à changer si la personne le possède.
    :return: La redirection vers la page correspondant au rôle
    """
    user = request.user
    redirect_url: str = ""
    if role == "admin":
        redirect_url = "/polls/admin/"
    elif role == "professeur" or role == "superviseur":
        redirect_url = "/polls/course/"

    user.role['view'] = role
    user.save()

    return HttpResponseRedirect(redirect_to=redirect_url)


@login_required(login_url='/polls')
def echeance_and_upload(request, idcours: int = None, idperiode: int = None, delivrable_id: int = None) -> HttpResponse:
    """
    Page d'échéance et d'upload de fichier
    :param request:
    :param idcours: l'id du cours concerné par l'échéance
    :param idperiode: l'id de la période concernée par l'échéance
    :param delivrable_id: l'id du devoir à rendre
    :return:
    """
    user = request.user
    if 'etudiant' not in user.role['role']:
        return HttpResponse("Unauthorized", status=401)

    etudiant: Etudiant = find_student_by_id_personne(user.idpersonne)
    sujets: list[Sujet] = find_sujet_by_id_etudiant(etudiant)
    courses: list[Cours] = find_course_by_student(user.idpersonne)
    elements = []

    for sujet, course in zip(sujets, courses):
        delais = []
        delais_query: list[Etape] = find_delais_by_sujet(sujet)
        for delai in delais_query:
            fichier_delivrable_instance: list[FichierDelivrable] = FichierDelivrable.objects.filter(
                iddelivrable=delai.iddelivrable,
                idetudiant=etudiant,
                rendu=True
            ).first()

            form: FichierDelivrableForm = FichierDelivrableForm(
                instance=fichier_delivrable_instance) if fichier_delivrable_instance else FichierDelivrableForm()

            if delivrable_id == delai.iddelivrable.iddelivrable and request.method == 'POST':
                form = FichierDelivrableForm(request.POST, request.FILES, instance=fichier_delivrable_instance)
                if form.is_valid():
                    fichier_delivrable = form.save(commit=False)
                    fichier_delivrable.iddelivrable = get_object_or_404(Delivrable, iddelivrable=delivrable_id)
                    fichier_delivrable.idetudiant = etudiant
                    fichier_delivrable.nom_personne = find_ue(course.idue).idprof.idpersonne.nom
                    fichier_delivrable.nom_cours = course.idue_id
                    fichier_delivrable.annee_periode = sujet.idperiode.annee
                    fichier_delivrable.rendu = True
                    fichier_delivrable.save()
                    return redirect('echeance_and_upload')

            already_submitted: bool = fichier_delivrable_instance is not None
            delais.append({
                'delai': delai,
                'form': form,
                'already_submitted': already_submitted,
            })

        elements.append({'periode': sujet.idperiode, 'course': course, 'delais': delais})

    context: dict[str, Any] = {
        'elements': elements,
        'current_date': datetime.now().date(),
    }
    return render(request, 'otherRole/echeance.html', context)


@login_required(login_url='/polls')
def profile(request) -> HttpResponse:
    """
    Page de profil de l'utilisateur
    :param request: La requête http courante
    :return: La page html du profil de l'utilisateur
    """
    user = personne = request.user
    context: dict[str, Any] = {
        'user': user,
        'personne': personne,
        'noSideBar': True
    }
    return render(request, 'otherRole/fiche.html', context)


@csrf_exempt
def subscription(request: HttpRequest) -> HttpResponse:
    """
    Page d'inscription pour un nouvel étudiant
    :param request: La requête http courante
    :return:
    """
    if request.method == 'POST':
        form: SubscriptionForm = SubscriptionForm(request.POST)
        if form.is_valid():
            mail: str = form.cleaned_data['mail']
            isUser: bool = is_existing_personne_by_email(mail)
            if isUser:
                return redirect("/polls/login")
            else:
                default_role: dict[str, str | list[str]] = {"role": ["etudiant"], "view": "etudiant"}
                hashedpassword: str = make_password(form.cleaned_data['password'])
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
        form: SubscriptionForm = SubscriptionForm()
    context: dict[str, SubscriptionForm | bool] = {
        "form": form,
        "noSideBar": True
    }
    return render(request, 'subscribe.html', context)


def create_personne(nom: str, prenom: str, email: str, password: str, role) -> Personne:
    """
    Fonction permettant de créer une personne
    :param nom: Le nom de la personne
    :param prenom: Le prénom de la personne
    :param email: L'email de la personne
    :param password: Le mot de passe
    :param role: Le rôle de la personne
    :return: Une personne conforme aux models de django
    """
    personne = Personne(nom=nom, prenom=prenom, mail=email, password=password, role=role)
    return personne


def create_etudiant(bloc: str, personne: Personne) -> Etudiant:
    """
    Fonction permettant de créer un étudiant
    :param bloc: Le bloc de l'étudiant
    :param personne: Représentation de la clé étrangère de la classe personne associée à l'étudiant
    :return: L'étudiant conforme aux models de django
    """
    etudiant = Etudiant(bloc=bloc, idpersonne=personne)
    return etudiant


@login_required(login_url='/polls')
def desinscription_course(request) -> HttpResponse:
    """
    Page de désinscription d'un étudiant
    :param request: La requête http courante
    :return: Renvoi la page permettant de se désinscrire d'un cours
    """
    user = request.user
    if "etudiant" in user.role['role']:
        courses_query: list[Cours] = find_course_for_student(user.idpersonne)
        courses: list[Cours] = []
        for course in courses_query:
            courses.append(course)
        if len(courses) == 0:
            context = {
                'failure': 'Vous n\'êtes inscrit à aucun cours, donc ce n\'est pas possible de vous désinscrire'
            }
        else:
            context = {
                'courses': courses,
                'desinscription_course': True
            }
        return render(request, 'otherRole/home.html', context)
    else:
        return redirect('/polls/home')


@login_required(login_url='/polls')
@student_required
def desinscription_validation(request, idcours: int) -> HttpResponse:
    """
    Validation de la désinscription d'un étudiant
    :param request: La requête http courante
    :param idcours: le cours auquel l'étudiant veut se désinscrire
    :return: Redirection vers l'url de la page d'accueil
    """
    user = request.user
    if "etudiant" in user.role['role']:
        cours: Cours = find_course_by_id(idcours)
        student: Etudiant = find_student_by_id_personne(user.idpersonne)
        selections: list[SelectionSujet] = find_selection_by_id_etudiant(student.idetudiant)

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
def desinscription_etudiant_from_course(request: HttpRequest, idpersonne: int, idue: str) -> HttpResponse:
    """
    Désinscription d'un étudiant d'un cours par un prof ou un admin
    :param request: La requête http courante
    :param idpersonne: id de la personne à désinscrire d'un cours
    :param idue: l'id de l'ue du cours
    :return:
    """
    etudiant: Etudiant = find_student_by_id_personne(idpersonne)
    sujets: list[Sujet] = find_sujets_of_student_of_ue(idpersonne, idue)
    cours: Cours = Cours.objects.get(idetudiant=etudiant, idue=idue)
    # On libère les sujets réservés par l'étudiant
    if sujets is not None:
        for sujet in sujets:
            sujet.estpris = False
            selections: list[SelectionSujet] = find_selection_by_id_sujet(sujet)
            for selection in selections:
                selection.delete()
            sujet.save()

    cours.delete()
    return redirect('/polls/course/' + idue + '/participants/')


@login_required(login_url='/polls')
def deliverable_file(request: HttpRequest, path: str) -> FileResponse:
    """
    Obtention d'un fichier délivrable
    :param request:La requête http courante
    :param path: Le chemin d'accès au fichier
    :return: Le fichier en question si celui-ci exite
    """
    base_path = 'C:\\Users\\matth\\Desktop\\genieproj\\genieLogiciel'
    relative_path = path.replace(base_path, '')
    deliverable = get_object_or_404(FichierDelivrable, fichier=relative_path)
    return FileResponse(deliverable.fichier)
