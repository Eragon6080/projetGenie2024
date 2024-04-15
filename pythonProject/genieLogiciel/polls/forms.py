from typing import Any
from django import forms
from django.forms import BaseFormSet

from .models import Etape, Delivrable, Periode, Sujet


class EtapeForm(forms.ModelForm):
    NECESSITE_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]
    necessiteDelivrable = forms.ChoiceField(choices=NECESSITE_CHOICES, label='Nécessite un Delivrable',
                                            widget=forms.RadioSelect)

    class Meta:
        model = Etape
        fields = ['description', 'delai']
        widgets = {
            'delai': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class SubmitForm(forms.Form):
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
        label='File',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'type': 'file', 'placeholder': 'Fichier'})
    )


class ConnectForm(forms.Form):
    email = forms.CharField(label="email", max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
    password = forms.CharField(label="password", max_length=100, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}))


class AddAdminForm(forms.Form):
    email = forms.CharField(label="Enter user email", max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}))


class AdminRoleForm(forms.Form):
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
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['description'].required = False
        self.fields['destination'].required = False


class SubjectReservationForm(forms.ModelForm):
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre', 'readonly':'readonly','width':'100px'})
    )
    description = forms.CharField(
        label='Description',
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Sujet', 'height': '100px','readonly':'readonly'})
    )
    students = forms.ChoiceField(
        label='students',
        required=True,
        widget=forms.Select(

        )
    )
    subject_id = forms.IntegerField(label='id',required=False,widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ConfirmationSujetReservation, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            self.fields['title'].widget.attrs['value'] = kwargs['initial'].get('title', '')
            self.fields['description'].initial = kwargs['initial'].get('description', '')
            self.fields['subject_id'].widget.attrs['value'] = kwargs['initial'].get('subject_id', '')
            self.fields['students'].widget.choices = kwargs['initial'].get('students',[])
