from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)

class MakeBookingsForm(forms.Form):
    arrival = forms.DateField(widget=forms.TextInput(attrs={'required':True}))
    depature = forms.DateField(widget=forms.TextInput(attrs={'required':True}))
    guests = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    campsite = forms.ChoiceField()
    email = forms.EmailField(widget=forms.TextInput(attrs={'required':True}))
    confirmEmail = forms.EmailField(label ="Confirm Email",required=False)
    firstName = forms.CharField(label="First Name")
    surname = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    vehicleRego = forms.CharField(label = "Vehicle Registration",required=False)
    price = forms.DecimalField(widget=forms.TextInput(attrs={'required':True}))
    postcode =forms.CharField(max_length=4, label="Post Code",widget=forms.TextInput(attrs={'required':True}))
    country = forms.ChoiceField(label="Country",widget=forms.TextInput(attrs={'required':True}))

    def __init__(self, *args, **kwargs):
        campsites = None
        if len(kwargs) > 0:
            campsites = kwargs['campsites']
            kwargs.pop('campsites')
        super(MakeBookingsForm, self).__init__(*args, **kwargs)
        self.fields['arrival'].widget.attrs['readonly'] = True
        self.fields['depature'].widget.attrs['readonly'] = True
        self.fields['guests'].widget.attrs['readonly'] = True
        self.fields['firstName'].widget.attrs['required'] = True
        self.fields['campsite'].choices = campsites
