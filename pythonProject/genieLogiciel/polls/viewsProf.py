from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout

from .forms import SubmitForm
from .queries import get_all_subjects, get_subject


@login_required(login_url='/polls')
def modifyList(request) -> HttpResponse:
    user = request.user
    if 'professeur' in user.role['role']:
        subjects_results = get_all_subjects()
        subject_titles = ['UE', 'Titre', 'Descriptif', 'Fichier']
        subjects = []
        for subject in subjects_results:
            subjects.append(subject)

        context = {
            'subjects': subjects,
            'subjects_titles': subject_titles
        }
        return render(request, "otherRole/modifyList.html", context)
    else:
        auth_logout(request)
        return redirect("/polls")


@login_required(login_url="polls/")
def modifySubject(request, idSujet) -> HttpResponse:
    user = request.user
    if 'professeur' in user.role['role']:
        querried_subjects = get_subject(idSujet)
        if querried_subjects is not None:

            subject_form = SubmitForm()
            context = {
                'sujet' : querried_subjects,
                'form' : subject_form
            }
            return render(request,"otherRole/modifySubject.html",context)
        else:
            redirect("/polls/modify/list")
