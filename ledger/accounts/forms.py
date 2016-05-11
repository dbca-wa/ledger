from django import forms

from django_countries.widgets import CountrySelectWidget

from .models import EmailUser, Address, Profile


class FirstTimeForm(forms.Form):
    redirect_url = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(input_formats=['%d/%m/%Y'])


class EmailUserForm(forms.ModelForm):
    email = forms.EmailField(required=False, help_text='If no email address is available, leave blank and a placeholder '
                             'email will be generated for the customer')
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(input_formats=['%d/%m/%Y'])

    class Meta:
        model = EmailUser
        fields = ['email', 'first_name', 'last_name', 'dob']

    def save(self, force_insert=False, force_update=False, commit=True):
        email_user = super(EmailUserForm, self).save(commit=False)

        if not email_user.email:
            email_user.email = '%s.%s.%s@ledger.dpaw.wa.gov.au' % (email_user.first_name, email_user.last_name, email_user.dob)

        if commit:
            email_user.save()

        return email_user


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
