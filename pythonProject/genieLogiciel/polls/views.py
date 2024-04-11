import logging
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from .queries import get_all_course, find_student_by_id_personne, find_professeur_by_id_personne, \
    find_course_by_student, find_course_by_professeur_or_superviseur
from django.views.decorators.csrf import csrf_exempt
from .forms import ConnectForm
from .restrictions import etudiant_required, prof_or_superviseur_required, prof_or_superviseur_or_student_required, admin_or_professor_required


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
        course = find_course_by_professeur_or_superviseur(user.idpersonne)
        courses.append(course)
    else:
        course = find_course_by_student(user.idpersonne)
        courses.append(course)
    sideBar = not('professeur' in role or "superviseur" in role)
    context = {
        'cours': courses,
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
                if 'admin' in user.role['role']:
                    return HttpResponseRedirect(redirect_to="admin/")
                else:
                    return HttpResponseRedirect(redirect_to="home/")
            else:
                form = ConnectForm()
    else:
        form = ConnectForm()
    context = {
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
