from django import forms
from django.forms.models import fields_for_model

from customers.models import Customer, Address



class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)


class CustomerCreateForm(forms.Form):

    customer_fields = fields_for_model(
        Customer,
        fields=['first_name', 'last_name', 'title', 'dob', 'phone_number', 'mobile_number', 'fax_number', 'organisation']
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
        self.fields.update(self.customer_fields)
        self.fields.update(self.address_fields)

        # set required fields
        for field_name in ['first_name', 'last_name',
                           'title', 'dob',
                           'line1', 'locality', 'state', 'postcode']:
            self.fields[field_name].required = True
            self.fields[field_name].widget.is_required = True

    def _get_cleaned_data_for_fields(self, field_dict):
        return {k: v for (k, v) in self.cleaned_data.items() if k in field_dict.keys()}

    def get_customer_data(self):
        return self._get_cleaned_data_for_fields(self.customer_fields)

    def get_address_data(self):
        return self._get_cleaned_data_for_fields(self.address_fields)
