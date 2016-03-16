from django import forms
from django.forms.models import fields_for_model

from accounts.models import EmailUser, Address


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)
