from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .queries import get_Professeur_People, get_Etudiant_People, get_All_People


@login_required(login_url='/polls')
def admin(request) -> HttpResponse:
    return render(request, 'admin.html', {})


@login_required(login_url='/polls')
def role(request) -> HttpResponse:
    user = request.user  # nécessaire pour demander la variable user
    if 'admin' in user.role['role']:
        list_admin = []
        list_professeur = []
        list_etudiant = []
        list_superviseur = []

        roles = ["admin", "professeur", "etudiant", "superviseur"]  # A priori, on a que 4 roles possibles
        admin_people = get_All_People()
        professeur_people = get_Professeur_People()
        etudiant_people = get_Etudiant_People()

        for i in admin_people:
            if 'admin' in i.role['role']:
                list_admin.append(i)
            if 'superviseur' in i.role['role']:
                list_superviseur.append(i)

        for i in professeur_people:
            list_professeur.append(i)
        for i in etudiant_people:
            list_etudiant.append(i)

        admin_and_superviseur_title = ["Nom", "Prenom", "Email", "Rôle"]
        etudiant_title = ["Nom", "Prenom", "Email", "Bloc", "Rôle"]
        professeur_title = ["Nom", "Prenom", "Email", "Specialité","Rôle"]

        context = {
            "roles": roles,
            "admin_people": list_admin,
            "professeur_people": list_professeur,
            "etudiant_people": etudiant_people,
            "superviseur_people": list_superviseur,
            "admin_and_superviseur_title": admin_and_superviseur_title,
            "etudiant_title": etudiant_title,
            "professeur_title": professeur_title
        }

        return render(request, 'admin/role.html', context)
    else:
        return HttpResponseRedirect(redirect_to="course/")
