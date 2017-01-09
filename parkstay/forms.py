from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)

class MakeBookingsForm(forms.Form):
    arrival = forms.DateField()
    depature = forms.DateField()
    guests = forms.CharField()
    campsite = forms.ChoiceField()
    email = forms.EmailField()
    confirmEmail = forms.EmailField()
    firstName = forms.CharField()
    surname = forms.CharField()
    phone = forms.CharField()
    vehicleRego = forms.CharField()
    price = forms.DecimalField()
