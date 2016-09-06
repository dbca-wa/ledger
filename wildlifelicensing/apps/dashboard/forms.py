from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)
