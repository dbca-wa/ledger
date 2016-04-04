from django import forms


class IdentificationForm(forms.Form):
    identification_file = forms.ImageField(label='Image containing ID', help_text='E.g. drivers licence, passport')
