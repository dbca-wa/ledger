from django import forms

from ledger.accounts.models import Profile

from models import IDRequest, AmendmentRequest


class ProfileSelectionForm(forms.Form):
    profile = forms.ModelChoiceField(queryset=Profile.objects.none(), empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')

        selected_profile = None
        if 'selected_profile' in kwargs:
            selected_profile = kwargs.pop('selected_profile')

        super(ProfileSelectionForm, self).__init__(*args, **kwargs)

        self.fields['profile'].queryset = user.profile_set.all()

        if selected_profile is not None:
            self.fields['profile'].initial = selected_profile
        else:
            self.fields['profile'].initial = user.profile_set.first()


class IDRequestForm(forms.ModelForm):
    class Meta:
        model = IDRequest
        fields = ['application', 'user', 'reason', 'text']
        widgets = {'application': forms.HiddenInput(), 'user': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        application = kwargs.pop('application', None)
        user = kwargs.pop('user', None)

        super(IDRequestForm, self).__init__(*args, **kwargs)

        if application is not None:
            self.fields['application'].initial = application

        if user is not None:
            self.fields['user'].initial = user


class AmendmentRequestForm(forms.ModelForm):
    class Meta:
        model = AmendmentRequest
        fields = ['application', 'user', 'reason', 'text']
        widgets = {'application': forms.HiddenInput(), 'user': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        application = kwargs.pop('application', None)
        user = kwargs.pop('user', None)

        super(AmendmentRequestForm, self).__init__(*args, **kwargs)

        if application is not None:
            self.fields['application'].initial = application

        if user is not None:
            self.fields['user'].initial = user
