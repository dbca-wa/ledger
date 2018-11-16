from django import forms
from ledger.address.models import Country


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)

VEHICLE_TYPES = (
    ('0', 'Vessel'),
#    ('1', 'Vehicle (concession)'),
#    ('2', 'Motorcycle')
)

class VehicleInfoForm(forms.Form):
    vehicle_rego = forms.CharField(label="Vessel Registration", widget=forms.TextInput(attrs={'required':True}))
    vehicle_type = forms.ChoiceField(label="Vessel Type", choices=VEHICLE_TYPES)
    entry_fee = forms.BooleanField(required=False, label="Entry fee")

VehicleInfoFormset = forms.formset_factory(VehicleInfoForm, extra=1, max_num=8)




class MakeBookingsForm(forms.Form):
    num_adult = forms.IntegerField(min_value=0, max_value=16, label="Adults (non-concessions)")
    num_child = forms.IntegerField(min_value=0, max_value=16, label="Children (ages 6-15)")
    num_concession = forms.IntegerField(min_value=0, max_value=16, label="Concessions")
    num_infant = forms.IntegerField(min_value=0, max_value=16, label="Infants (ages 0-5)")
    first_name = forms.CharField(label="Given Name(s)")
    last_name = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    postcode = forms.CharField(max_length=4, label="Post Code",widget=forms.TextInput(attrs={'required':True}))
    country = forms.ModelChoiceField(queryset=Country.objects.all(), to_field_name="iso_3166_1_a2")


    def __init__(self, *args, **kwargs):
        super(MakeBookingsForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['required'] = True

    def clean(self):
        super(MakeBookingsForm, self).clean()

#        if ('num_adult' in self.cleaned_data and 'num_concession' in self.cleaned_data):
        if ('num_mooring' in self.cleaned_data):
            if (self.cleaned_data.get('num_mooring')) < 1:
                raise forms.ValidationError('Booking requires at least 1 guest that is an adult or concession.')



class AnonymousMakeBookingsForm(MakeBookingsForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True}))
    confirm_email = forms.EmailField(label ="Confirm Email", widget=forms.TextInput(attrs={'required':True}))

    def clean(self):
        super(AnonymousMakeBookingsForm, self).clean()

        if ('email' in self.cleaned_data and 'confirm_email' in self.cleaned_data):
            if (self.cleaned_data.get('email') != self.cleaned_data.get('confirm_email')):
                raise forms.ValidationError('Email and confirmation email fields do not match.')

