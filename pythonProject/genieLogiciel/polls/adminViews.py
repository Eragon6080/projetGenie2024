from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.forms.formsets import formset_factory


from .queries import get_Professeur_People, get_Etudiant_People, get_All_People
from .forms import AdminRoleForm, BaseRoleFormSet
from .models import Personne



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

        admin_and_superviseur_title = ["Nom Prénom", "Email", "Rôle"]
        etudiant_title = ["Nom Prénom", "Email", "Bloc", "Rôle"]
        professeur_title = ["Nom Prénom", "Email", "Specialité","Rôle"]
        manage_roles_title = ["Nom Prénom", "Email", "Professeur", "Superviseur"]

        
        RoleForm = formset_factory(AdminRoleForm, formset=BaseRoleFormSet, extra=len(list_professeur_superviseur))
        formset = RoleForm(form_kwargs={'list_id': [pers[0].idpersonne for pers in list_professeur_superviseur], 'list_pers': [pers[0] for pers in list_professeur_superviseur]})

        for form in formset:
            for pers in list_professeur_superviseur:
                if form.idpersonne == pers[0].idpersonne:
                    pers.append(form)
        
        print(list_professeur_superviseur)


        
        if request.method == 'POST':
            postFormSet = RoleForm(request.POST, form_kwargs={'list_id': [pers[0].idpersonne for pers in list_professeur_superviseur], 'list_pers': [pers[0] for pers in list_professeur_superviseur]})
            if postFormSet.is_valid():
                for form in postFormSet:
                    dbPerson = Personne.objects.get(idpersonne=form.idpersonne)
                    if form.cleaned_data != {}:
                        print(form.idpersonne, form.cleaned_data)
                        if form.cleaned_data['prof'] == True and "professeur" not in dbPerson.role['role']:
                            dbPerson.role['role'].append("professeur")
                        if form.cleaned_data['sup'] == True and "superviseur" not in dbPerson.role['role']:
                            dbPerson.role['role'].append("superviseur")
                        if form.cleaned_data['prof'] == False and "professeur" in dbPerson.role['role']:
                            dbPerson.role['role'].remove("professeur")
                        if form.cleaned_data['sup'] == False and "superviseur" in dbPerson.role['role']:
                            dbPerson.role['role'].remove("superviseur")
                        dbPerson.save()
                    else:
                        print("No change")

                return HttpResponseRedirect(redirect_to=view)        
                    
            



        context = {
            "formset": formset,
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

