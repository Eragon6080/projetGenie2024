import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .forms import SubmitForm


# Create your views here.

@csrf_exempt
def index(request) -> HttpResponse:
    logger = logging.getLogger()
    print("cc")
    if request.method == 'POST':
        form = SubmitForm(request.POST)
        response = form.description
        logger.warning(response)

        if form.is_valid():
            logger.warning("cc")
            return HttpResponseRedirect("polls/ok")

    else:
        form = SubmitForm()

    context = {
        'prenom': "Matthys",
        'role': "Etudiant",
        "form": form
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


def ok(request) -> HttpResponse:
    context = {
        'response': "votre formulaire a bien été soumis"
    }
    return render(request, 'ok.html', context=context)
