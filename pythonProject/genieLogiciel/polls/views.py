import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .forms import SubmitForm, ConnectForm


# Create your views here.

@csrf_exempt
def addTopic(request, code) -> HttpResponse:
    logger = logging.getLogger()
    if request.method == 'POST':
        form = SubmitForm(request.POST)
        if form.is_valid():
            logger.info("form is valid")
            return HttpResponseRedirect("ok/")
    else:
        form = SubmitForm()
    context = {
        'prenom': "Matthys",
        'role': "Etudiant",
        "form": form
    }
    return render(request, 'submitSubject.html', context)


# obliger de passer tous les élements nécessaires dans le context donc, attention aux id

def home(request) -> HttpResponse:
    context = {
        'cours': [
            {
                'title': "IDS",
                'UE': "INFOB331"},
            {
                'title': "Mémoire",
                'UE': "INFOB332"
            }

        ],
        'title': 'Cours',
        'prenom': "Matthys",
        'role': "Etudiant"
    }
    return render(request, 'home.html', context)

def course(request, code) -> HttpResponse:
    return render(request, 'course.html', {})


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
            return HttpResponseRedirect("cours/")
    else:
        form = ConnectForm()
    context = {
        'prenom': "Matthys",
        'role': "Etudiant",
        "form": form
    }
    return render(request, 'login.html', context)
