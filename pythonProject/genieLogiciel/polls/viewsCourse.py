import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .forms import SubmitForm, ConnectForm


def topics(request, code) -> HttpResponse:

    context = {
        'topics' : [
            {
                'title': 'Topic 1',
                'description': 'Content 1',
                'student': 'Student 1'},
            {
                'title': 'Topic 2',
                'description': 'Content 2',
                'student': 'Student 2'},
            {
                'title': 'Topic 3',
                'description': 'Content 3',
                'student': 'Student 3'},
            {
                'title': 'Topic 4',
                'description': 'Content 4',
                'student': 'Student 4'
            }
        ],
        'UE': code,
        'title': 'Cours',
        'prenom': "Matthys",
        'role': "Etudiant"
    }
    return render(request, "topic.html", context)

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
        'UE': code,
        'title': 'Cours',
        'prenom': "Matthys",
        'role': "Etudiant",
        "form": form
    }
    return render(request, 'submitSubject.html', context)
