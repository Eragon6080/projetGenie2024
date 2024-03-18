from django import forms

from django import forms


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
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )


class ConnectForm(forms.Form):
    eid = forms.CharField(label="eid", max_length=100, required=True,
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eid'}))
    password = forms.CharField(label="password", max_length=100, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}))
