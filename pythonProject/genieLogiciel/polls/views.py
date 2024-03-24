import logging
from django.contrib.auth import login as auth_login

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .UE import get_all_course
from django.views.decorators.csrf import csrf_exempt
from .forms import ConnectForm
from .models import Personne


# Create your views here.


# obliger de passer tous les élements nécessaires dans le context donc, attention aux id

@login_required(login_url='/polls')
def home(request) -> HttpResponse:
    courses_query = get_all_course()
    courses = []
    for cours in courses_query:
        courses.append(cours)
    context = {
        'cours': courses,
        'title': 'Cours',
        'prenom': "Matthys",
        'role': "Etudiant",
        'noSideBar': 'true'
    }
    print(context['cours'])

    return render(request, 'home.html', context)


@login_required(login_url='/polls')
def course(request, code) -> HttpResponse:
    return render(request, 'course.html', {})


@login_required(login_url='/polls')
def ok(request) -> HttpResponse:
    context = {
        'response': "votre formulaire a bien été soumis"
    }
    return render(request, 'ok.html', context=context)


@csrf_exempt
def login(request) -> HttpResponse:
    logger = logging.getLogger()
    if request.method == 'POST':
        form = ConnectForm(request.POST)
        if form.is_valid():
            logger.info("form is valid")
            user = authenticate(request, mail=form.cleaned_data['email'], password=form.cleaned_data['password'])
            print(form.cleaned_data['email'], form.cleaned_data['password'])
            if user is not None:
                logger.info("user is not None")
                personne = Personne.objects.get(mail=form.cleaned_data['email'], password=make_password(form.cleaned_data['password']))
                context = {
                    'prenom': personne.prenom,
                    'nom' : personne.nom,
                    'role': personne.role
                }
                auth_login(request,user)
                return HttpResponseRedirect(redirect_to="course/", context=context)
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
