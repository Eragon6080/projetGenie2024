
from django import forms
from .models import Etape, Delivrable, Periode


class EtapeForm(forms.ModelForm):
    NECESSITE_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]
    necessiteDelivrable = forms.ChoiceField(choices=NECESSITE_CHOICES, label='Nécessite un Delivrable', widget=forms.RadioSelect)

    class Meta:
        model = Etape
        fields = ['description','delai']
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
        widget=forms.FileInput(attrs={'class': 'form-control','type':'file','placeholder': 'Fichier'})
    )


class ConnectForm(forms.Form):
    email = forms.CharField(label="email", max_length=100, required=True,
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
    password = forms.CharField(label="password", max_length=100, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}))


class UpdateForm(SubmitForm):
   
    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['description'].required = False
        self.fields['destination'].required = False
        
