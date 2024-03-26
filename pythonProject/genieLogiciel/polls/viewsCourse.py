import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .forms import SubmitForm, ConnectForm
from .models import Sujet


@login_required(login_url='/polls')
def topics(request, code) -> HttpResponse:
    context = {
        'topics': [
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


@login_required(login_url='/polls')
@csrf_exempt
def addTopic(request, code) -> HttpResponse:
    logger = logging.getLogger()
    
    if request.method == 'POST':
        
        form = SubmitForm(request.POST, request.FILES)

        if form.is_valid():
            logger.info("form is valid")
            sujet = Sujet(titre=form.cleaned_data['title'], descriptif=form.cleaned_data['description'],
                          destination=form.cleaned_data['destination'], fichier=form.cleaned_data['file'])


            sujet.save()

            return HttpResponseRedirect("../../ok")
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


@login_required(login_url="/polls")
@csrf_exempt
def ok(request) -> HttpResponse:
    return render(request, "ok.html", context={ok: 'Votre sujet a été validé'})
