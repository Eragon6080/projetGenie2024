from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms


from .queries import get_Professeur_People, get_Etudiant_People, get_All_People
from .forms import AdminRoleForm



@login_required(login_url='/polls')
def admin(request) -> HttpResponse:
    return render(request, 'admin/admin.html', {})


@login_required(login_url='/polls')
def role(request, view = "admin") -> HttpResponse:
    user = request.user  # nécessaire pour demander la variable user
    if 'admin' in user.role['role']:    
  
        list_admin = []
        list_professeur = []
        list_etudiant = []
        list_superviseur = []
        list_professeur_superviseur = []

        roles = ["admin", "professeur", "etudiant", "superviseur"]  # A priori, on a que 4 roles possibles

        admin_people = get_All_People()
        professeur_people = get_Professeur_People()
        etudiant_people = get_Etudiant_People()

        for i in admin_people:
            if 'admin' in i.role['role']:
                list_admin.append(i)
            if 'superviseur' in i.role['role']:
                list_superviseur.append(i)
            if "superviseur" in i.role['role'] or "professeur" in i.role['role']:
                list_professeur_superviseur.append([i])

        for i in professeur_people:
            list_professeur.append(i)
        for i in etudiant_people:
            list_etudiant.append(i)

        admin_and_superviseur_title = ["Nom", "Prenom", "Email", "Rôle"]
        etudiant_title = ["Nom", "Prenom", "Email", "Bloc", "Rôle"]
        professeur_title = ["Nom", "Prenom", "Email", "Specialité","Rôle"]
        manage_roles_title = ["Nom", "Prenom", "Email", "Professeur", "Superviseur"]

        

        
        for pers in list_professeur_superviseur :
            # persFields = {}
            # persFields['prof'] = forms.BooleanField(initial=False, required=False)
            # persFields['sup'] = forms.BooleanField(required=False)
            RoleForm = type('RoleForm'+str(pers[0].idpersonne), (AdminRoleForm,), {})
            roleForm = RoleForm()
            pers.append(roleForm)

        print(list_professeur_superviseur)

        
        if request.method == 'POST':
            for personne in list_professeur_superviseur:
                roleForm = RoleForm(request.POST)
                print(personne[0].idpersonne, roleForm['prof'].data)
            

        context = {
            "roles": roles,
            "current_view": view,
            "admin_people": list_admin,
            "professeur_people": list_professeur,
            "etudiant_people": etudiant_people,
            "superviseur_people": list_superviseur,
            "admin_and_superviseur_title": admin_and_superviseur_title,
            "professeur_superviseur_people" : list_professeur_superviseur,
            "etudiant_title": etudiant_title,
            "professeur_title": professeur_title,
            "manage_roles_title" : manage_roles_title
        }

        return render(request, 'admin/role.html', context)
    else:
        return HttpResponseRedirect(redirect_to="course/")

