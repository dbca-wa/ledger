from django import forms

from models import Application


class ApplicationForm(forms.Form):
    type = forms.CharField(label='Type', widget=forms.HiddenInput)
    