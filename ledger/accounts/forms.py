from django import forms

from .models import Address, Persona, EmailUser



class FirstTimeForm(forms.Form):
    redirect_url = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(input_formats=['%d/%m/%Y'])
    

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['line1', 'line2', 'line3', 'locality', 'state', 'postcode']


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['name', 'email', 'institution']

    def __init__(self, *args, **kwargs):
        initial_display_name = kwargs.pop('initial_display_name', None)
        initial_email = kwargs.pop('initial_email', None)

        super(PersonaForm, self).__init__(*args, **kwargs)

        if initial_display_name is not None:
            self.fields['name'].initial = initial_display_name

        if initial_email is not None:
            self.fields['email'].initial = initial_email
