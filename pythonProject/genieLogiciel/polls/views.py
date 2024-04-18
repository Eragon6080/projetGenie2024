from datetime import datetime
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import Delivrable, Etudiant, FichierDelivrable
from .queries import *
from django.views.decorators.csrf import csrf_exempt
from .forms import ConnectForm, FichierDelivrableForm
from .restrictions import *
from .utils.date import get_today_date
from .mailNotification import sendMail


# Create your views here.


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
    role = user.role["role"]
    if "professeur" in role or "superviseur" in role:
        get_courses = find_course_by_professeur_or_superviseur(user.idpersonne)
        courses = get_courses
    else:
        course = find_course_by_student(user.idpersonne)
        courses.append(course)
    sideBar = not ('professeur' in role or "superviseur" in role)
    context = {
        'courses': courses,
        'noSideBar': sideBar
    }

    return render(request, 'otherRole/home.html', context)


@login_required(login_url='/polls')
def course(request, code) -> HttpResponse:
    return render(request, 'otherRole/course.html', {})


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
    personne = get_personne_by_id(idpersonne)
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
def echeance(request):
    user = request.user
    if "etudiant" in user.role['role']:
        etudiant = get_student_by_id_personne(user.idpersonne)
        delais_query = get_delais(etudiant.idsujet.idperiode.idperiode)

        delais = []
        for delai in delais_query:
            delais.append(delai)
        context = {
            'cours': etudiant.idsujet.idcours,
            'periode': etudiant.idsujet.idperiode,
            'delais': delais,
            'current_date': datetime.now().date()


        }
        for delai in delais:
            print(delai.iddelivrable)
            print(context['current_date'])
        return render(request, 'otherRole/echeance.html', context)


@login_required(login_url='/polls')
def upload_delivrable(request, delivrable_id):
    delivrable = get_object_or_404(Delivrable, iddelivrable=delivrable_id)
    user = request.user
    if 'etudiant' in user.role['role']:
        etudiant = get_student_by_id_personne(user.idpersonne)

        if request.method == 'POST':
            form = FichierDelivrableForm(request.POST, request.FILES)
            if form.is_valid():
                fichier_delivrable = form.save(commit=False)
                fichier_delivrable.iddelivrable = delivrable
                fichier_delivrable.idetudiant = etudiant
                fichier_delivrable.nom_personne = etudiant.idpersonne.nom
                fichier_delivrable.nom_cours = etudiant.idsujet.idcours.idue.nom
                fichier_delivrable.annee_periode = etudiant.idsujet.idperiode.annee
                fichier_delivrable.rendu = True  # Marquer comme rendu
                fichier_delivrable.save()
                return redirect('echeance')
        else:
            form = FichierDelivrableForm()
        
        # Vérifier si le délivrable a déjà été rendu
        already_submitted = FichierDelivrable.objects.filter(iddelivrable=delivrable, idetudiant=etudiant, rendu=True).exists()

        return render(request, 'otherRole/delivrable.html', {'form': form, 'delivrable': delivrable,  'already_submitted': already_submitted})

@login_required(login_url='/polls')
def profile(request):
    user = personne = request.user
    context = {
        'user': user,
        'personne': personne,
        'noSideBar': 'true'
    }
    return render(request, 'otherRole/fiche.html', context)
