import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .forms import SubmitForm , UpdateForm , EtapeForm
from .models import Sujet, Etudiant, Ue, Cours, Professeur, Etape, Delivrable
from .restrictions import prof_or_superviseur_required


@login_required(login_url='/polls')
@prof_or_superviseur_required
def topics(request, code):
     # Récupère tous les cours associés à une UE particulière
    cours_ids = Cours.objects.filter(idue_id=code).values_list('idcours', flat=True)
    print(cours_ids, "ok")
    # Récupèrer tous les sujets associés à ces cours
    sujets = Sujet.objects.filter(idCours__in=cours_ids)
    print(sujets, 'oki')
    sujet_infos = []
    for sujet in sujets:
        sujet_info = {
            'id': sujet.idsujet ,
            'titre': sujet.titre,
            'description': sujet.descriptif,
            'etudiants': [],
            'estPris': sujet.estPris,
        }

        if sujet.estPris:
            etudiants = Etudiant.objects.filter(idsujet=sujet)
            print(etudiants, "yess")
            etudiants_noms = [f"{etudiant.idpersonne.nom} {etudiant.idpersonne.prenom}" for etudiant in etudiants]
            sujet_info['etudiants'] = etudiants_noms

        sujet_infos.append(sujet_info)

    return render(request, "otherRole/topic.html", {'sujet_infos': sujet_infos, 'UE':code})



@login_required(login_url='/polls')
@csrf_exempt
def editTopic(request, sujet_id):
    sujet = get_object_or_404(Sujet, idsujet=sujet_id)
    id_ue = sujet.idCours.idue.idue
    if request.method == 'POST':
        form = UpdateForm(request.POST, request.FILES)
        if form.is_valid():
            sujet.titre = form.cleaned_data['title']
            sujet.descriptif = form.cleaned_data['description']
            sujet.destination = form.cleaned_data['destination']
            if 'file' in request.FILES:
                sujet.file = request.FILES['file']
            sujet.save()
            return redirect("topics",code = id_ue)
    else:
         form_data = {
            'title': sujet.titre,
            'description': sujet.descriptif,
            'destination': sujet.destination,
        }
        
         form = UpdateForm(initial=form_data)
    
    
    return render(request, 'otherRole/edit_sujet.html', {'form': form})


@login_required(login_url='/polls')
@csrf_exempt
def deleteTopic(request, sujet_id):
    sujet = get_object_or_404(Sujet, idsujet=sujet_id)
    id_ue = sujet.idCours.idue.idue
    sujet.delete()
    return redirect("topics",code = id_ue)  

@login_required(login_url='/polls')
@csrf_exempt
@prof_or_superviseur_required
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
    return render(request, 'otherRole/submitSubject.html', context)

@login_required(login_url="/polls")
@csrf_exempt
def ok(request) -> HttpResponse:
    return render(request, "ohterRole/ok.html", context={ok: 'Votre sujet a été validé'})



@login_required(login_url='/polls')
@csrf_exempt
def gestion_etape(request, idue):
    ue = get_object_or_404(Ue, idue=idue)
    if request.method == 'POST':
        form = EtapeForm(request.POST)
        if form.is_valid():
            etape = form.save(commit=False)
            etape.idPeriode = ue.idprof.idperiode  
            delivrable = Delivrable()
            if 'typeFichier' in request.POST and request.POST['typeFichier'].strip():
                typeFichier = request.POST['typeFichier']
                delivrable.typeFichier= typeFichier
            delivrable.save()
            etape.idDelivrable = delivrable
            etape.save()
            return redirect("topics",code = idue)
    else:
        form = EtapeForm()

    return render(request, 'otherRole/gestion_etape.html', {'form': form, 'ue': ue})

@login_required(login_url='/polls')
@csrf_exempt
def afficher_etapes_ue(request, idue):
    ue = get_object_or_404(Ue, idue=idue) 
    professeur = ue.idprof 
    periode = professeur.idperiode
    etapes = Etape.objects.filter(idPeriode=periode).order_by('delai')
    print(etapes)

    return render(request, 'otherRole/afficher_etapes_ue.html', {'etapes': etapes, 'ue': ue})
