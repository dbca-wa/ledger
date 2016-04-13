from django import forms

from django_countries.widgets import CountrySelectWidget

from .models import Address, Profile, EmailUser


class FirstTimeForm(forms.Form):
    redirect_url = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(input_formats=['%d/%m/%Y'])


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['line1', 'line2', 'line3', 'locality', 'state', 'country', 'postcode']
        widgets = {'country': CountrySelectWidget()}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'email', 'institution']

    def __init__(self, *args, **kwargs):
        initial_display_name = kwargs.pop('initial_display_name', None)
        initial_email = kwargs.pop('initial_email', None)

        super(ProfileForm, self).__init__(*args, **kwargs)

        if initial_display_name is not None:
            self.fields['name'].initial = initial_display_name

        if initial_email is not None:
            self.fields['email'].initial = initial_email
