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


# obliger de passer tous les élements nécessaires dans le context donc, attention aux id

def cours(request) -> HttpResponse:
    context = {
        'cours1': "IDS",
        'description1': "INFOB331",
        'cours2': "Mémoire",
        'description2': "INFOB332",
        'title': 'Cours',
        'prenom': "Matthys",
        'role': "Etudiant"
    }
    return render(request, 'cours.html', context)
