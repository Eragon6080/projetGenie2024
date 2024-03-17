from django import forms


class SubmitForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100, required=True)
    description = forms.Textarea()
    destination = forms.Textarea()
    file = forms.FileField(label='File', required=False)


