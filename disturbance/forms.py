from __future__ import unicode_literals
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.contrib.auth import get_user_model
from django.forms import Form, ModelForm, CharField, ValidationError, EmailField

from ledger.accounts.models import Profile, Address, Organisation


User = get_user_model()


class LoginForm(Form):
    email = EmailField(max_length=254)

class PersonalForm(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_emailuserprofile_update'
        self.helper.attrs = {'novalidate': ''}
        # Define the form layout.
        self.helper.layout = Layout(
            'first_name', 'last_name', 
            FormActions(
                Submit('save', 'Save', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )

class ContactForm(ModelForm):

    class Meta:
        model = User
        fields = ['email', 'phone_number','mobile_number']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_emailuserprofile_update'
        self.helper.attrs = {'novalidate': ''}
        # Define the form layout.
        self.helper.layout = Layout(
            'phone_number', 'mobile_number','email', 
            FormActions(
                Submit('save', 'Save', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class AddressForm(ModelForm):

    class Meta:
        model = Address
        fields = ['line1', 'line2', 'locality', 'state', 'postcode']

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_address'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class OrganisationAdminForm(ModelForm):
    """ModelForm that is used in the Django admin site.
    """
    model = Organisation

    def clean_abn(self):
        data = self.cleaned_data['abn']
        # If it's changed, check for any existing organisations with the same ABN.
        if data and self.instance.abn != data and Organisation.objects.filter(abn=data).exists():
            raise ValidationError('An organisation with this ABN already exists.')
        return data


class OrganisationForm(OrganisationAdminForm):

    class Meta:
        model = Organisation
        fields = ['name', 'abn', 'identification']

    def __init__(self, *args, **kwargs):
        super(OrganisationForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Company name'
        self.fields['identification'].label = 'Certificate of incorporation'
        self.fields['identification'].help_text = 'Electronic copy of current certificate (e.g. image/PDF)'
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_organisation'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class DelegateAccessForm(Form):

    def __init__(self, *args, **kwargs):
        super(DelegateAccessForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.add_input(Submit('confirm', 'Confirm', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class UnlinkDelegateForm(ModelForm):

    class Meta:
        model = Organisation
        exclude = ['name', 'abn', 'identification', 'postal_address', 'billing_address', 'delegates']

    def __init__(self, *args, **kwargs):
        super(UnlinkDelegateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.add_input(Submit('unlink', 'Unlink user', css_class='btn-lg btn-danger'))
        self.helper.add_input(Submit('cancel', 'Cancel'))
