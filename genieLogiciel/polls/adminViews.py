import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.forms.formsets import formset_factory
from django.contrib import messages


from .queries import *
from .forms import AdminRoleForm, BaseRoleFormSet, AddAdminForm
from .models import Personne, Professeur, Periode
from .restrictions import admin_required


@login_required(login_url='/polls')
@admin_required
def admin(request) -> HttpResponse:
    return render(request, 'admin/admin.html', {})


@login_required(login_url='/polls')
@admin_required
def role(request, view = "admin") -> HttpResponse:
    user = request.user  # nécessaire pour demander la variable user
    if 'admin' in user.role['role']:    
        
        # Get all people role
        list_admin = []
        list_professeur = []
        list_etudiant = []
        list_superviseur = []
        list_professeur_superviseur = []

        roles = ["admin", "professeur", "etudiant", "superviseur"]  # A priori, on a que 4 roles possibles

        admin_people = find_all_People()
        professeur_people = find_Professeur_People()
        etudiant_people = find_etudiant_People()

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

        # Create formset for professor/supervisor view

        RoleForm = formset_factory(AdminRoleForm, formset=BaseRoleFormSet, extra=len(list_professeur_superviseur))
        formset = RoleForm(form_kwargs={'list_id': [pers[0].idpersonne for pers in list_professeur_superviseur], 'list_pers': [pers[0] for pers in list_professeur_superviseur]})

        for form in formset:
            for pers in list_professeur_superviseur:
                if form.idpersonne == pers[0].idpersonne:
                    pers.append(form)
        
        # Create add new admin form

        addAdminForm = AddAdminForm()
        

        if request.method == 'POST':
            postFormSet = RoleForm(request.POST, form_kwargs={'list_id': [pers[0].idpersonne for pers in list_professeur_superviseur], 'list_pers': [pers[0] for pers in list_professeur_superviseur]})
            addAdminForm = AddAdminForm(request.POST)
            
            if postFormSet.is_valid():
                for form in postFormSet:
                    dbPerson = Personne.objects.get(idpersonne=form.idpersonne)

                    if form.cleaned_data != {}:
                        if form.cleaned_data['prof'] == True and "professeur" not in dbPerson.role['role']:
                            dbPerson.role['role'].append("professeur")
                            Professeur.objects.create(idpersonne=dbPerson, idperiode=Periode.objects.get(annee=datetime.date.today().year), specialite="Informatique")
                        if form.cleaned_data['sup'] == True and "superviseur" not in dbPerson.role['role']:
                            dbPerson.role['role'].append("superviseur")
                        if form.cleaned_data['prof'] == False and "professeur" in dbPerson.role['role']:
                            dbPerson.role['role'].remove("professeur")
                            Professeur.objects.get(idpersonne=dbPerson).delete()
                        if form.cleaned_data['sup'] == False and "superviseur" in dbPerson.role['role']:
                            dbPerson.role['role'].remove("superviseur")
                        dbPerson.save()
                    else:
                        print("No changes")
                        
                messages.success(request, 'Changes successfully saved.')
                return HttpResponseRedirect(redirect_to=view)
            
            elif addAdminForm.is_valid():
                try:
                    newAdmin = Personne.objects.get(mail=addAdminForm.cleaned_data['email'])
                except Personne.DoesNotExist:
                    messages.warning(request, 'User not found.')
                    return HttpResponseRedirect(redirect_to=view)
                
                if "admin" in newAdmin.role['role']:
                    messages.warning(request, 'User is already an admin.')
                    return HttpResponseRedirect(redirect_to=view)
                elif "professeur" in newAdmin.role['role'] or "superviseur" in newAdmin.role['role']:
                    messages.warning(request, 'User is already a professor or supervisor.')
                    return HttpResponseRedirect(redirect_to=view)
                elif "etudiant" in newAdmin.role['role']:
                    messages.warning(request, 'User is a student. Cannot be an admin')
                    return HttpResponseRedirect(redirect_to=view)

                newAdmin.role['role'] = ["admin"]
                newAdmin.role['view'] = "admin"
                newAdmin.save()
                messages.success(request, 'Admin successfully added.')
                return HttpResponseRedirect(redirect_to=view)
             
                    
            



        context = {
            "formset": formset,
            "addAdminForm": addAdminForm,
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
    
@login_required(login_url='/polls')
@admin_required
def courses(request) -> HttpResponse:
    context = {
        "title_table_courses": ["Code", "Nom", "Responsable"],
        "all_courses": find_all_ue(),
    }
    
    return render(request, 'admin/courses.html', context)




