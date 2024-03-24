import logging
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from .UE import get_all_course
from django.views.decorators.csrf import csrf_exempt
from .forms import ConnectForm



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
    if request.method == 'POST':
        form = ConnectForm(request.POST)
        if form.is_valid():

            user = authenticate(request, mail=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None and user.is_authenticated:
                auth_login(request, user)

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
