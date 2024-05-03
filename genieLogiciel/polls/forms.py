
from django import forms
from django.forms import BaseFormSet, TextInput, EmailInput


from .models import Etape, Sujet, FichierDelivrable


class FichierDelivrableForm(forms.ModelForm):
    class Meta:
        model = FichierDelivrable
        fields = ['fichier','estconfidentiel']


class EtapeForm(forms.ModelForm):
    NECESSITE_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]
    necessiteDelivrable = forms.ChoiceField(choices=NECESSITE_CHOICES, label='Nécessite un Delivrable',
                                            widget=forms.RadioSelect)
    typeFichier = forms.CharField(label='Type de fichier', required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Type de fichier'}))

    class Meta:
        model = Etape
        fields = ['titre', 'description', 'datedebut', 'datefin']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'étape'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Consignes de l\'étape', 'rows': '3'}),
            'datedebut': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'datefin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class SubmitForm(forms.Form):
    nbPersonneMax = 2
    student_select = forms.ModelChoiceField(queryset=None, label='Lier le sujet à un étudiant', required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    
    referent_select = forms.ModelChoiceField(queryset=None, label='Lier le sujet à un professeur/superviseur', required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        list_students = kwargs.pop('list_students', None)
        list_referent = kwargs.pop('list_referent', None)
        is_admin = kwargs.pop('is_admin', False)
        super().__init__()
        self.fields['student_select'].queryset = list_students
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
    nb_personnes = forms.ChoiceField(choices=[(i, i) for i in range(1, nbPersonneMax+1)], label='Nombre de personnes', required=True, widget=forms.Select(attrs={'class': 'form-control'}))


class ConnectForm(forms.Form):
    email = forms.CharField(label="email", max_length=100, required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
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
        widget=forms.Select(

        )
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
        widget=TextInput(attrs={'class':'form-control','placeholder': 'Prenom'})
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
