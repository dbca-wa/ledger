from django import forms

from models import Address, Persona


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['line1', 'line2', 'line3', 'locality', 'state', 'postcode']


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['name', 'email', 'institution']
