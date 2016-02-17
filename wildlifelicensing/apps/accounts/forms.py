from django import forms
from django.forms.models import fields_for_model

from addressbook.models import Address
from rollcall.models import EmailUser
from .models import Customer


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)


class CustomerCreateForm(forms.Form):
    user_fields = fields_for_model(
        EmailUser,
        fields=['first_name', 'last_name']
    )

    customer_fields = fields_for_model(
        Customer,
        fields=['title', 'dob', 'phone_number', 'mobile_number', 'fax_number', 'organisation']
    )

    address_fields = fields_for_model(
        Address,
        fields=['line1', 'locality', 'state', 'postcode'],
        labels={
            'line1': 'Address',
            'locality': 'Suburb'
        }
    )

    def __init__(self, *args, **kwargs):
        super(CustomerCreateForm, self).__init__(*args, **kwargs)
        self.fields.update(self.user_fields)
        self.fields.update(self.customer_fields)
        self.fields.update(self.address_fields)

        # set required fields
        for field_name in ['first_name', 'last_name',
                           'title', 'dob',
                           'line1', 'locality', 'state', 'postcode']:
            self.fields[field_name].required = True
            self.fields[field_name].widget.is_required = True
