import logging
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from .queries import get_all_course, find_student_by_id_personne, find_professeur_by_id_personne
from django.views.decorators.csrf import csrf_exempt
from .forms import ConnectForm


# Create your views here.


# obliger de passer tous les élements nécessaires dans le context donc, attention aux id

@login_required(login_url='/polls')
def home(request) -> HttpResponse:
    courses_query = get_all_course()
    courses = []
    for cours in courses_query:
        print(cours)
        courses.append(cours)
    context = {
        'cours': courses,
        'noSideBar': 'true'
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
            print(user.role)
            if user is not None and user.is_authenticated:
                auth_login(request, user)
                if 'admin' in user.role['role']:
                    return HttpResponseRedirect(redirect_to="admin/")
                else:
                    return HttpResponseRedirect(redirect_to="course/")
            else:
                form = ConnectForm()
    else:
        form = ConnectForm()
    context = {
        'prenom': "Matthys",
        'role': "Etudiant",
        "form": form
    }
    return render(request, 'login.html', context)


def logout(request):
    auth_logout(request)
    return redirect('/polls')


def yes(request):
    return render(request, 'suivi.html', {})


@login_required(login_url='/polls')
def fiche(request):
    user = request.user
    student = find_student_by_id_personne(user.idpersonne)
    if student is None:
        personne = find_professeur_by_id_personne(user.idpersonne)
    else:
        personne = student
    context = {
        'user': user,
        'personne': personne,
        'noSideBar': 'true'
    }
    return render(request, 'otherRole/fiche.html', context)
