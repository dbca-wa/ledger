from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)

class MakeBookingsForm(forms.Form):
    arrival = forms.DateField()
    depature = forms.DateField()
    guests = forms.CharField()
    campsite = forms.ChoiceField()
    email = forms.EmailField()
    confirmEmail = forms.EmailField(label ="Confirm Email")
    firstName = forms.CharField(label="First Name")
    surname = forms.CharField()
    phone = forms.CharField()
    vehicleRego = forms.CharField(label = "Vehicle Registration")
    price = forms.DecimalField()
    postcode =forms.CharField(max_length=4, label="Post Code")
    country = forms.ChoiceField(label="Country")
