from typing import Any

from django import forms
from django.forms import BaseFormSet, TextInput, EmailInput

from .models import Etape, Sujet, FichierDelivrable

"""
Cette page contient les différentes classes reflétant différents formulaires des pages html
"""


class FichierDelivrableForm(forms.ModelForm):
    """
    Formulaire permettant l'ajout des références d'un fichier en Bd en collaboration avec le stockage du fichier dans le système django.
    """
    class Meta:
        model:FichierDelivrable = FichierDelivrable
        fields:list[str] = ['fichier', 'estconfidentiel']
        labels:dict[str,str] = {
            'fichier': 'Fichier',
            'estconfidentiel': 'Confidentiel',
        }
        widgets = {
            'fichier': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Fichier'}),
            'estconfidentiel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EtapeForm(forms.ModelForm):
    """
    Définition du formulaire servant à créer des étapes pour une période donnée.
    """
    NECESSITE_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]
    necessiteDelivrable = forms.ChoiceField(choices=NECESSITE_CHOICES, label='Nécessite un Delivrable',
                                            widget=forms.RadioSelect)
    typeFichier = forms.CharField(label='Type de fichier', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Type de fichier'}))

    class Meta:
        model:Etape= Etape
        fields:list[str] = ['titre', 'description', 'datedebut', 'datefin']
        widgets:dict[str,Any] = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'étape'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Consignes de l\'étape', 'rows': '3'}),
            'datedebut': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'datefin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class SubmitForm(forms.Form):
    """
    Formulaire permettant d'encoder un nouveau sujet en base de données
    """
    nbPersonneMax:int = 2

    referent_select = forms.ModelChoiceField(queryset=None, label='Lier le sujet à un professeur/superviseur',
                                             required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        list_referent = kwargs.pop('list_referent', None)
        is_admin:bool = kwargs.pop('is_admin', False)
        super().__init__()
        self.fields['referent_select'].queryset = list_referent
        if is_admin:
            self.fields['referent_select'].required = True

    title = forms.CharField(
        label='Title',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre'})
    )
    description = forms.CharField(
        label='Description',
        max_length=1000,
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Sujet', 'height': '100px'})
    )
    destination = forms.CharField(
        label='Destination',
        max_length=100,
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Sujet', 'height': '100px'})
    )
    file = forms.FileField(
        label='Fichier',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'type': 'file', 'placeholder': 'Fichier'})
    )
    nb_personnes = forms.ChoiceField(choices=[(i, i) for i in range(1, nbPersonneMax + 1)], label='Nombre de personnes',
                                     required=True, widget=forms.Select(attrs={'class': 'form-control'}))


class ConnectForm(forms.Form):
    """
    Formulaire de connexion pour assurer l'authentification
    """
    email = forms.CharField(label="email", max_length=100, required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
    password = forms.CharField(label="password", max_length=100, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}))


class AddAdminForm(forms.Form):
    """
    Formulaire pour ajouter yn nouvel administrateur
    """
    email = forms.CharField(label="Enter user email", max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}))


class AdminRoleForm(forms.Form):
    """
    Formulaire permettant à l'administrateur d'encoder de nouveaux rôles ou d'en supprimer
    """
    # Dynamic form created in adminViews.py
    def __init__(self, idpersonne, pers, *args, **kwargs):
        self.idpersonne = idpersonne
        super().__init__(*args, **kwargs)

        if 'professeur' in pers.role['role']:
            self.fields['prof'] = forms.BooleanField(initial=True, required=False)
        else:
            self.fields['prof'] = forms.BooleanField(required=False)

        if 'superviseur' in pers.role['role']:
            self.fields['sup'] = forms.BooleanField(initial=True, required=False)
        else:
            self.fields['sup'] = forms.BooleanField(required=False)


class BaseRoleFormSet(BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        idpersonne = kwargs['list_id'][index]
        pers = kwargs['list_pers'][index]
        return {'idpersonne': idpersonne, 'pers': pers}


class UpdateForm(SubmitForm):

    def __init__(self, *args, **kwargs):
        list_students = kwargs.pop('list_students', None)
        list_referent = kwargs.pop('list_referent', None)
        is_admin = kwargs.pop('is_admin', False)
        initial_form = kwargs.pop('initial', None)
        super(UpdateForm, self).__init__(*args, **kwargs)

        self.fields['referent_select'].queryset = list_referent
        if initial_form is not None:
            self.fields['title'].required = False
            self.fields['title'].initial = initial_form['title']
            self.fields['description'].required = False
            self.fields['description'].initial = initial_form['description'] if initial_form[
                                                                                    'description'] != "NULL" else ""
            self.fields['destination'].required = False
            self.fields['destination'].initial = initial_form['destination'] if initial_form[
                                                                                    'destination'] != "NULL" else ""


class SubjectReservationForm(forms.ModelForm):
    """
    Formulaire permettant de réserver un sujet
    """
    # permet de récupérer des valeurs qui ne sont pas inclus dans le model
    subject_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Sujet
        fields = ['titre', 'descriptif', 'subject_id']


class ConfirmationSujetReservation(forms.Form):
    title = forms.CharField(
        label='Title',
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Titre', 'readonly': 'readonly', 'width': '100px'})
    )
    description = forms.CharField(
        label='Description',
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Sujet', 'height': '100px',
                                     'readonly': 'readonly'})
    )
    students = forms.ChoiceField(
        label='students',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subject_id = forms.IntegerField(label='id', required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ConfirmationSujetReservation, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            self.fields['title'].widget.attrs['value'] = kwargs['initial'].get('title', '')
            self.fields['description'].initial = kwargs['initial'].get('description', '')
            self.fields['subject_id'].widget.attrs['value'] = kwargs['initial'].get('subject_id', '')
            self.fields['students'].widget.choices = kwargs['initial'].get('students', [])


class SubscriptionForm(forms.Form):
    """
    Formulaire permettant à un nouvel étudiant de s'inscrire
    """
    nom = forms.CharField(
        label="Nom",
        max_length=100,
        required=True,
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'})
    )
    prenom = forms.CharField(
        label="Prenom",
        max_length=100,
        required=True,
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Prenom'})
    )
    mail = forms.EmailField(
        label="Email",
        max_length=100,
        required=True,
        widget=EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        label="Password",
        max_length=100,
        required=True,
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    bloc = forms.ChoiceField(
        label="Bloc",
        required=True,
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
