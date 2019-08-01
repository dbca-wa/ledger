from django import forms

from django_countries.widgets import CountrySelectWidget

from .models import Address, Profile, EmailUser, Document


class FirstTimeForm(forms.Form):
    redirect_url = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    dob = forms.DateField(input_formats=['%d/%m/%Y'])


class AddressForm(forms.ModelForm):
    update = forms.BooleanField(required=False,label='Check this to update all linked profiles.')
    class Meta:
        model = Address
        fields = ['update','line1', 'line2', 'line3', 'locality', 'state', 'country', 'postcode','user']
        widgets = {'country': CountrySelectWidget(),'user': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.profiles = None
        super(AddressForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.profiles = Profile.objects.filter(postal_address=self.instance)
            if len(self.profiles) == 1:
                self.fields.pop('update')
        else:
            self.fields.pop('update')

        if user is not None:
            self.fields['user'].initial = user

    def save(self, commit=True):
        try:
            if 'update' in self.fields:
                if self.cleaned_data['update']:
                    address = Address.objects.get(user=self.instance.user,hash=self.instance.generate_hash())
                    self.profiles.update(postal_address=address)
                    return address
                else:
                    address = Address.objects.get(user=self.instance.user,hash=self.instance.generate_hash())
                    return address

            address = Address.objects.get(user=self.instance.user,hash=self.instance.generate_hash())
            return address
        except Address.DoesNotExist:
            if 'update' in self.fields and not self.cleaned_data['update']:
                self.instance.id = None
            return super(AddressForm, self).save(commit)

class ProfileBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileBaseForm, self).__init__(*args, **kwargs)

        """
        instance = kwargs.get("instance")
        if instance and instance.pk:
            self.fields['auth_identity'].initial = kwargs["instance"].auth_identity
            if instance.user and instance.user.email == instance.email:
                #the profile's email is the same as the user account email, it must be an email identity;
                self.fields['auth_identity'].widget.attrs['disabled'] = True
        """

    def clean(self):
        super(ProfileBaseForm, self).clean()
        # always create a email identity for profile email
        self.cleaned_data["auth_identity"] = True

    '''
    def clean_auth_identity(self):
        if not self.cleaned_data.get("auth_identity", False):
            if self.instance.user and self.instance.user.email == self.cleaned_data["email"]:
                # the profile's email is the same as the user account email, it must be an email identity;
                return True
        return self.cleaned_data.get("auth_identity")
    '''

    def save(self, commit=True):
        setattr(self.instance, "auth_identity", self.cleaned_data.get("auth_identity", False))
        return super(ProfileBaseForm, self).save(commit)

    class Meta:
        model = Profile
        fields = '__all__'


class ProfileAdminForm(ProfileBaseForm):
    pass


class ProfileForm(ProfileBaseForm):
    # auth_identity = forms.BooleanField(required=False)
    class Meta:
        model = Profile
        fields = ['user', 'name', 'email', 'institution']
        widgets = {'user': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        initial_display_name = kwargs.pop('initial_display_name', None)
        initial_email = kwargs.pop('initial_email', None)

        super(ProfileForm, self).__init__(*args, **kwargs)

        if user is not None:
            self.fields['user'].initial = user

        if initial_display_name is not None:
            self.fields['name'].initial = initial_display_name

        if initial_email is not None:
            self.fields['email'].initial = initial_email


class EmailUserForm(forms.ModelForm):
    class Meta:
        model = EmailUser
        fields = ['email', 'first_name', 'last_name', 'title', 'dob', 'phone_number', 'mobile_number', 'fax_number']

    def __init__(self, *args, **kwargs):
        email_required = kwargs.pop('email_required', True)

        super(EmailUserForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = email_required

        # some form renderers use widget's is_required field to set required attribute for input element
        self.fields['email'].widget.is_required = email_required


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'description', 'file']

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
