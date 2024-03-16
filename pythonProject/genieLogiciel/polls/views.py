from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader


# Create your views here.

def index(request) -> HttpResponse:
    context = {
        'prenom': "Matthys",
        'role': "Etudiant"
    }
    return render(request, 'submitSubject.html', context)


def cours(request) -> HttpResponse:
    context = {
        'cours1': "IDS",
        'description1':"INFOB331",
        'cours2': "Mémoire",
        'description2': "INFOB332",
        'title': 'Cours'
    }
    return render(request, 'cours.html', context)
