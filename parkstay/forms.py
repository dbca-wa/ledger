from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)

VEHICLE_TYPES = (
    ('0', 'Vehicle'),
    ('1', 'Vehicle (concession)'),
    ('2', 'Motorcycle')
)

class VehicleInfoForm(forms.Form):
    vehicle_rego = forms.CharField(label="Vehicle Registration", widget=forms.TextInput(attrs={'required':True}))
    vehicle_type = forms.ChoiceField(label="Vehicle Type", choices=VEHICLE_TYPES)

VehicleInfoFormset = forms.formset_factory(VehicleInfoForm, extra=1, max_num=8)


class MakeBookingsForm(forms.Form):
    num_adult = forms.IntegerField(min_value=0, max_value=16, label="Adults")
    num_child = forms.IntegerField(min_value=0, max_value=16, label="Children (ages 6-15)")
    num_concession = forms.IntegerField(min_value=0, max_value=16, label="Concessions")
    num_infant = forms.IntegerField(min_value=0, max_value=16, label="Infants (ages 0-5)")
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True}))
    confirm_email = forms.EmailField(label ="Confirm Email", widget=forms.TextInput(attrs={'required':True}))
    first_name = forms.CharField(label="Given Name(s)")
    surname = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    postcode =forms.CharField(max_length=4, label="Post Code",widget=forms.TextInput(attrs={'required':True}))
    country = forms.CharField(label="Country",widget=forms.TextInput(attrs={'required':True}))
    

    def __init__(self, *args, **kwargs):
        super(MakeBookingsForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['required'] = True

    def clean(self):
        super(MakeBookingsForm, self).clean()

        if (self.cleaned_data.get('num_adult')+self.cleaned_data.get('num_concession')) < 1:
            raise forms.ValidationError('Booking requires at least 1 guest that is an adult or concession.')

        if (self.cleaned_data.get('email') != self.cleaned_data.get('confirm_email')):
            raise forms.ValidationError('Email and confirmation email fields do not match.')

