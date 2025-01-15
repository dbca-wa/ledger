from django import forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Layout, Submit, HTML, Fieldset, MultiField, Div
from django.forms import Form, ModelForm, ChoiceField, FileField, CharField, Textarea, ClearableFileInput, HiddenInput, Field, RadioSelect, ModelChoiceField, Select
from ledger.widgets import ClearableMultipleFileInput, RadioSelectWithCaptions, AjaxFileUploader
from django_countries.widgets import CountrySelectWidget
from .models import Address, Profile, EmailUser, Document

class BaseFormHelper(FormHelper):
    form_class = 'form-control formlabels'
    label_class = 'form-label'
    #label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
    #field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'
    field_class = 'form-control'

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


class EmailUserLegacyForm(forms.ModelForm):
    class Meta:
        model = EmailUser
        fields = ['email', 'first_name', 'last_name', 'title', 'dob', 'phone_number', 'mobile_number', 'fax_number']

    def __init__(self, *args, **kwargs):
        email_required = kwargs.pop('email_required', True)

        super(EmailUserLegacyForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = email_required

        # some form renderers use widget's is_required field to set required attribute for input element
        self.fields['email'].widget.is_required = email_required

class EmailUserForm(forms.ModelForm):
    
    identification2 = FileField(label='Upload Identification', required=False, max_length=128, widget=AjaxFileUploader(attrs={'single':'single'})) 

    class Meta:
        model = EmailUser
        fields = ['email', 'first_name', 'last_name','legal_first_name','legal_last_name', 'title','position_title','manager_name','manager_email', 'dob', 'legal_dob', 'phone_number', 'mobile_number', 'fax_number','identification2','is_staff','is_active']

    def __init__(self, *args, **kwargs):
        
        email_required = kwargs.pop('email_required', True)

        super(EmailUserForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        crispy_boxes = Div()


        for f in self.fields:            
            self.fields[f].widget.attrs['class'] = 'form-control'
            self.fields[f].widget.attrs['label_class'] = 'form-control'
            if f == 'first_name':                
                self.fields[f].widget = HiddenInput()
            if f == 'last_name':
                self.fields[f].widget = HiddenInput()
            if f == 'email':                
                self.fields[f].widget = HiddenInput()
            if f == 'position_title':
                self.fields[f].widget = HiddenInput()
            if f == 'manager_name':
                self.fields[f].widget = HiddenInput()    
            if f == 'manager_email':
                self.fields[f].widget = HiddenInput()
            if f == 'is_active':
                self.fields[f].widget.attrs['class'] = 'form-check-input'
                self.fields[f].help_text = ''
            if f == 'is_staff':
                self.fields[f].widget.attrs['class'] = 'form-check-input'
                self.fields[f].help_text = ''

                

        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel', css_class='btn-lg btn-danger'))

        person_id = self.initial['id']
        self.fields['email'].required = email_required

        # some form renderers use widget's is_required field to set required attribute for input element
        self.fields['email'].widget.is_required = email_required

        crispy_boxes.append(HTML("<label>Email</label><div class='p-1'>{}</div>".format(self.initial['email'])))
        crispy_boxes.append(HTML("<label>Given Name(s)</label><div class='p-1'>{}</div>".format(self.initial['first_name'])))
        crispy_boxes.append(HTML("<label>Last Name</label><div class='p-1'>{}</div>".format(self.initial['last_name'])))
        crispy_boxes.append(HTML("<input type='hidden' value='{}' name='file_group' id='file_group'>".format('1')))
        crispy_boxes.append(HTML("<input type='hidden' value='{}' name='file_group_ref_id' id='file_group_ref_id'>".format(str(person_id))))

        crispy_boxes.append('first_name')
        crispy_boxes.append('last_name')

        if self.initial['position_title']:
            if len(self.initial['position_title']) > 0:
                crispy_boxes.append(HTML("<label>Position Title</label><div class='p-1'>{}</div>".format(self.initial['position_title'])))
        if self.initial['manager_name']:
            if len(self.initial['manager_name']) > 0:
                crispy_boxes.append(HTML("<label>Manager Name</label><div class='p-1'>{}</div>".format(self.initial['manager_name'])))
        if self.initial['manager_email']:
            if len(self.initial['manager_email']) > 0:
                crispy_boxes.append(HTML("<label>Manager Email</label><div class='p-1'>{}</div>".format(self.initial['manager_email'])))                

        crispy_boxes.append('position_title')    
        crispy_boxes.append('manager_name')  
        crispy_boxes.append('manager_email')  
        crispy_boxes.append('email')
        crispy_boxes.append('legal_first_name')
        crispy_boxes.append('legal_last_name')
        crispy_boxes.append('title')
        crispy_boxes.append('dob')
        crispy_boxes.append('legal_dob')
        crispy_boxes.append('phone_number')
        crispy_boxes.append('mobile_number')
        crispy_boxes.append('fax_number')
        crispy_boxes.append('identification2')
        crispy_boxes.append(HTML("<BR>"))
        crispy_boxes.append('is_staff')
        crispy_boxes.append('is_active')
        
        crispy_boxes.append(HTML("<BR>"))

        self.helper.layout = Layout(crispy_boxes)

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'description', 'file']

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
