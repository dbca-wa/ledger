from django import forms


class IdentityForm(forms.Form):
    identity_file = forms.ImageField(label='Image containing ID', help_text='E.g. drivers licence, passport')
