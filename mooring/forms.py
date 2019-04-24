from django import forms
from ledger.address.models import Country
from mooring import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Fieldset, MultiField, Div
from django.forms import Form, ModelForm, ChoiceField, FileField, CharField, Textarea, ClearableFileInput, HiddenInput, Field, RadioSelect, ModelChoiceField, Select

class BaseFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
    field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)

VEHICLE_TYPES = (
    ('0', 'Vessel'),
#    ('1', 'Vehicle (concession)'),
#    ('2', 'Motorcycle')
)

class CancelGroupForm(forms.ModelForm):
    mooring_group = ChoiceField(choices=[],)

    class Meta:
        model = models.CancelGroup
        fields = ['name','cancel_period','mooring_group']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(CancelGroupForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.fields['mooring_group'].choices = []
        if 'mooring_group_choices' in self.initial:
            self.fields['mooring_group'].choices = self.initial['mooring_group_choices'] 

        self.helper.form_id = 'id_cancel_group_form'
        #self.helper.attrs = {'novalidate': ''}
        #self.helper.add_input(Submit('Continue', 'Continue', css_class='btn-lg'))


class DeleteBookingPeriodOptionForm(forms.ModelForm):
    class Meta:
        model = models.BookingPeriodOption
        fields = []

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(DeleteBookingPeriodOptionForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_delet_form'
        self.helper.add_input(Submit('Delete', 'Delete', css_class='btn-lg', style='margin-top: 15px;' ))


class BookingPeriodOptionForm(forms.ModelForm):
    #mooring_group = ChoiceField(choices=[],)
    class Meta:
        model = models.BookingPeriodOption
        fields = ['period_name','option_description','small_price','medium_price','large_price','start_time','finish_time','change_group','cancel_group','caption']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(BookingPeriodOptionForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.fields['change_group'].choices = []
        self.fields['cancel_group'].choices = []
        if 'change_group_choices'  in self.initial:
            self.fields['change_group'].choices = self.initial['change_group_choices']
        if 'cancel_group_choices'  in self.initial:
            self.fields['cancel_group'].choices = self.initial['cancel_group_choices']


        for f in self.fields:
           self.fields[f].widget.attrs.update({'class': 'form-control'})

        self.helper.form_id = 'id_change_group_form'
        if self.initial['action'] == 'edit':
           self.helper.add_input(Submit('Update', 'Update', css_class='btn-lg', style='margin-top: 15px;' ))
        else:
           self.helper.add_input(Submit('Create', 'Create', css_class='btn-lg', style='margin-top: 15px;' ))

class ChangeGroupForm(forms.ModelForm):

    class Meta:
        model = models.ChangeGroup 
        fields = ['name','change_period','mooring_group']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(ChangeGroupForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.fields['mooring_group'].choices = []
        if 'mooring_group_choices' in self.initial:
            self.fields['mooring_group'].choices = self.initial['mooring_group_choices']
        self.helper.form_id = 'id_change_group_form'
        #self.helper.attrs = {'novalidate': ''}
        #self.helper.add_input(Submit('Continue', 'Continue', css_class='btn-lg'))

class FailedRefundCompletedForm(forms.ModelForm):

    class Meta:
        model = models.RefundFailed
        fields = []

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(FailedRefundCompletedForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_refund_failed_form'
        #self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('Complete', 'Complete', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class='btn-lg'))

class BookingPeriodForm(forms.ModelForm):
    #mooring_group = ChoiceField(choices=[],)
    class Meta:
        model = models.BookingPeriod
        fields = ['name','mooring_group']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(BookingPeriodForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.fields['mooring_group'].choices = []
        if 'mooring_group_choices'  in self.initial:
            self.fields['mooring_group'].choices = self.initial['mooring_group_choices']
        for f in self.fields:
           self.fields[f].widget.attrs.update({'class': 'form-control'})

        self.helper.form_id = 'id_change_group_form'
        if self.initial['action'] == 'edit':
           self.helper.add_input(Submit('Update', 'Update', css_class='btn-lg', style='margin-top: 15px;' ))
        else:
           self.helper.add_input(Submit('Create', 'Create', css_class='btn-lg', style='margin-top: 15px;'))


class UpdateChangeGroupForm(forms.ModelForm):
    #mooring_group = ChoiceField(choices=[],)
    class Meta:
        model = models.ChangeGroup
        fields = ['name','mooring_group']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(UpdateChangeGroupForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.fields['mooring_group'].choices = []
        if 'mooring_group_choices'  in self.initial:
            self.fields['mooring_group'].choices = self.initial['mooring_group_choices']
        for f in self.fields:
           self.fields[f].widget.attrs.update({'class': 'form-control'})

        self.helper.form_id = 'id_change_group_form'
        if self.initial['action'] == 'edit':
           self.helper.add_input(Submit('Update', 'Update', css_class='btn-lg', style='margin-top: 15px;' ))
        else:
           self.helper.add_input(Submit('Create', 'Create', css_class='btn-lg', style='margin-top: 15px;' ))


class UpdateCancelGroupForm(forms.ModelForm):

    class Meta:
        model = models.CancelGroup
        fields = ['name','mooring_group']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(UpdateCancelGroupForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.fields['mooring_group'].choices = self.initial['mooring_group_choices']
#        self.fields['name'].class = 'form-control'
        for f in self.fields:
           self.fields[f].widget.attrs.update({'class': 'form-control'})

        self.helper.form_id = 'id_change_group_form'
        if self.initial['action'] == 'edit':
           self.helper.add_input(Submit('Update', 'Update', css_class='btn-lg', style='margin-top: 15px;' ))
        else:
           self.helper.add_input(Submit('Create', 'Create', css_class='btn-lg', style='margin-top: 15px;'))


class UpdateChangeOptionForm(forms.ModelForm):

    class Meta:
        model = models.ChangePricePeriod
        fields = ['calulation_type','percentage','amount','days']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(UpdateChangeOptionForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
#        self.fields['name'].class = 'form-control'
        for f in self.fields:
           self.fields[f].widget.attrs.update({'class': 'form-control'})

        self.fields['percentage'].required = False
        self.fields['amount'].required = False
        self.helper.form_id = 'id_change_group_form'
        if self.initial['action'] == 'edit':
           self.helper.add_input(Submit('Update', 'Update', css_class='btn-lg', style='margin-top: 15px;' ))
        else:
           self.helper.add_input(Submit('Create', 'Create', css_class='btn-lg', style='margin-top: 15px;' ))


class UpdateCancelOptionForm(forms.ModelForm):

    class Meta:
        model = models.CancelPricePeriod
        fields = ['calulation_type','percentage','amount','days']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(UpdateCancelOptionForm, self).__init__(*args, **kwargs)

        self.helper = BaseFormHelper()
#        self.fields['name'].class = 'form-control'
        for f in self.fields:
           self.fields[f].widget.attrs.update({'class': 'form-control'})

        self.fields['percentage'].required = False
        self.fields['amount'].required = False

        self.helper.form_id = 'id_cancel_group_form'
        if self.initial['action'] == 'edit': 
           self.helper.add_input(Submit('Update', 'Update', css_class='btn-lg', style='margin-top: 15px;' ))
        else:
           self.helper.add_input(Submit('Create', 'Create', css_class='btn-lg', style='margin-top: 15px;' ))
   


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
    last_name = forms.CharField(widget=forms.TextInput(attrs={'required':True}), label="Last Name")
    phone = forms.CharField(widget=forms.TextInput(attrs={'required':True}), label="Phone (mobile preferred)")
    postcode = forms.CharField(max_length=4, label="Post Code",widget=forms.TextInput(attrs={'required':True}))
    country = forms.ModelChoiceField(queryset=Country.objects.all(), to_field_name="iso_3166_1_a2")
    email = forms.EmailField(label="Email", widget=forms.TextInput(attrs={'required':True}))
    confirm_email = forms.EmailField(label ="Confirm Email", widget=forms.TextInput(attrs={'required':True}))

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
    email = forms.EmailField(label="Email", widget=forms.TextInput(attrs={'required':True}))
    confirm_email = forms.EmailField(label ="Confirm Email", widget=forms.TextInput(attrs={'required':True}))

    def clean(self):
        super(AnonymousMakeBookingsForm, self).clean()

        if ('email' in self.cleaned_data and 'confirm_email' in self.cleaned_data):
            if (self.cleaned_data.get('email') != self.cleaned_data.get('confirm_email')):
                raise forms.ValidationError('Email and confirmation email fields do not match.')

