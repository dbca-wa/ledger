from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)


class VehicleInfoForm(forms.Form):
    vehicle_rego = forms.CharField(label = "Vehicle Registration",required=False)


class MakeBookingsForm(forms.Form):
    num_adult = forms.IntegerField(min_value=0, max_value=16, label="Adults")
    num_child = forms.IntegerField(min_value=0, max_value=16, label="Children (ages 6-15)")
    num_concession = forms.IntegerField(min_value=0, max_value=16, label="Concessions")
    num_infant = forms.IntegerField(min_value=0, max_value=16, label="Infants (ages 0-5)")
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True}))
    confirm_email = forms.EmailField(label ="Confirm Email",required=False)
    first_name = forms.CharField(label="First Name")
    surname = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    postcode =forms.CharField(max_length=4, label="Post Code",widget=forms.TextInput(attrs={'required':True}))
    country = forms.ChoiceField(label="Country",widget=forms.TextInput(attrs={'required':True}))
    
    vehicles = forms.formset_factory(VehicleInfoForm, extra=3)

    cc_number = forms.CharField(max_length=16, widget=forms.TextInput(attrs={'required':True, 'placeholder': 'Card number'}))
    cc_expiry = forms.CharField(max_length=7, widget=forms.TextInput(attrs={'required':True, 'placeholder': 'MM/YY'}))
    cc_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'required':True, 'placeholder': 'Name on card'}))
    cc_cvc = forms.CharField(max_length=3, widget=forms.TextInput(attrs={'required':True, 'placeholder': 'CVC'}))

    def __init__(self, *args, **kwargs):
        super(MakeBookingsForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['required'] = True


