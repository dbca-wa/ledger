from django import forms

from wildlifelicensing.apps.main.utils.form_utils import SectionedForm

from models import Application
from bottle import FormsDict


class ApplicationForm(forms.Form):
    type = forms.CharField(label='Type', widget=forms.HiddenInput)


class Regulation17ApplicationForm(ApplicationForm, SectionedForm):
    PROJECT_TYPE = (('survey', 'Survey'), ('monitoring', 'Monitoring'), ('research', 'Research'),)

    YES_NO_UNSURE = (('yes', 'Yes'), ('no', 'No'), ('unsure', 'Unsure'),)

    FINANCIAL_BASIS = (('grant', 'Grant / Sponsored'), ('contract', 'Contract / Consulting'), ('other', 'Other - Please provide details'),)

    ASSOCIATION_TO_APPLICANT = (('volunteer', 'Volunteer'), ('contractor', 'Contractor'), ('staff', 'Staff / Employee'), ('student', 'Student'),
                                ('other', 'Other - Please provide details'),)

    ROLE = (('handler', 'Handler'), ('scribe', 'Scribe'), ('assistant', 'Assistant'),)

    HANDLER_TYPES = (('biopsy', 'Biopsy'), ('chipping', 'Chipping'), ('collaring', 'Collaring'), ('anasthaesia', 'Anasthaesia'), ('other', 'Other'))

    INSTITUTION = (('privateindividual', 'Private Individual'),
                   ('privateconsultingroup', 'Private Consulting Group'),
                   ('scientificteriaryinstution', 'Scientific instituion, university or other tertiary institution, etc'))

    project_type = forms.ChoiceField(label='Which of the following describes your project?', choices=PROJECT_TYPE, widget=forms.RadioSelect)

    requires_permits = forms.ChoiceField(label='Does this project require any other approvals, permits, licenses, etc under '
                                         'any other state or federal legislation?', choices=YES_NO_UNSURE, widget=forms.RadioSelect)
    permits = forms.FileField(label='Please provide detail and attach any applications made or permissions granted.')
    permits_acknowledgement = forms.BooleanField(label='I acknowledge that should other permissions/approvals be required it may affect'
                                                 'the processing time for this Regulation 17 licence')

    financial_basis = forms.ChoiceField(label='How is your project funded?', choices=FINANCIAL_BASIS, widget=forms.RadioSelect)
    financial_details = forms.CharField(label='Affiliated Organisation / Client / Sponsor', widget=forms.Textarea,
                                        help_text='Please provide name, address, contact person and contact details')

    project_title = forms.CharField(label='Project Title', max_length=200)
    project_proposal = forms.FileField(label='Please attach project proposal')
    background_summary = forms.CharField(label='Background Summary', max_length=1000, widget=forms.Textarea)
    main_objectives = forms.CharField(label='Main Objectives', max_length=1000, widget=forms.Textarea)
    conservation_outcomes = forms.CharField(label='Background Summary', max_length=1000, widget=forms.Textarea)

    qualifications = forms.CharField(label='Provide relevant qualifications and/or experience details specific to this project '
                                     '(if not already provided in your profile)', widget=forms.Textarea)

    qualification_attachment = forms.FileField('Qualification Attachment(s)')

    authorised_persons_acknowledgement = forms.BooleanField(label='I acknowledge that I am legally responsible for the actions of anyone involved in the '
                                                            'take of fauna activities under this licence.')
    authorised_person_surname = forms.CharField(label='Surname')
    authorised_person_givennames = forms.CharField(label='Given Names')
    authorised_person_dob = forms.DateField(label='Date of Birth')
    authorised_person_association = forms.ChoiceField(label='Association to applicant', choices=ASSOCIATION_TO_APPLICANT)
    authorised_person_association_other_details = forms.CharField(label='Details')
    authorised_person_role = forms.ChoiceField(label='Role', choices=ROLE)
    authorised_person_handler_type = forms.ChoiceField(label='Handler Type', choices=HANDLER_TYPES)
    authorised_person_qualification = forms.FileField(label='Provide relevant qualification / experience (relative to activity)')
    authorised_person_unavailable_explanation = forms.CharField(label='If a list of authorised persons is not currently available, please explain:',
                                                                widget=forms.Textarea)
    authorised_person_change_acknowledgement = forms.BooleanField('I acknowledge that I will make changes in this system to authorised persons '
                                                                  'throughout license duration if changes are required.')

    location = forms.CharField(label='Location')

    field_start_date = forms.DateField(label='Start Date')
    field_end_date = forms.DateField(label='End Date')

    location = forms.CharField(label='Location of Project', widget=forms.Textarea, help_text='Applications to collect in Nature Reserves or National Parks'
                               ' must be supported by full reasons and a separate Regulation 4 application form must be completed.')
    ultimate_fate = forms.CharField(label='Ultimate fate of fauna taken', widget=forms.Textarea,
                                    help_text='If any fauna are to be euthanized, provide details of the technique')
    fauna_holding = forms.CharField(label='Means, facilities and place of holding fauna', widget=forms.Textarea,
                                    help_text='Specify details of the facility where the fauna are to be held for your research work (if applicable)')
    animal_ethics_approval_number = forms.CharField(label="Relevant Institution Animal Ethics Approval Number from your organisation's AEC", widget=forms.Textarea,
                                                    help_text='Attach a copy of the AEC application and approval to this application (IF APPLICABLE)')
    project_proposal_attached = forms.BooleanField(label='Project proposal attached', help_text='(NOTE: Compulsory for HONS, Masters, PhD level projects and for organisations which do not have an animal'
                                                                                                'ethics committee)')
    institution = forms.ChoiceField(label='Institution', choices=INSTITUTION)

    written_permission = forms.BooleanField(label='Permission')
    anticipated_outcomes = forms.CharField(label='Anticipated outcomes and conservation / management benefits', widget=forms.Textarea)
    communication_of_results = forms.CharField(label='Communication of results', widget=forms.Textarea)
    referee_1_name = forms.CharField(label='Referee 1 Name')
    referee_1_qualification = forms.CharField(label='Referee 1 Qualification')
    referee_1_contact_details = forms.CharField(label='Referee 1 Contact Details')
    referee_2_name = forms.CharField(label='Referee 2 Name')
    referee_2_qualification = forms.CharField(label='Referee 2 Qualification')
    referee_2_contact_details = forms.CharField(label='Referee 2 Contact Details')

    sections = (
                {'name': 'Project Type',
                 'items': ('project_type',)
                 },
                {'name': 'Approvals and Permits',
                 'items': ('requires_permits', 'permits', 'permits_acknowledgement'),
                 'conditional_fields': (
                                        {'conditional_field': 'requires_permits', 'condition': 'yes',
                                         'target_fields': ('permits', 'permits_acknowledgement')
                                         },
                                        )
                 },
                {
                 'name': 'Financial Basis',
                 'items': ('financial_basis', 'financial_details'),
                 'conditional_fields': (
                                        {'conditional_field': 'financial_basis', 'condition': 'other',
                                         'target_fields': ('financial_details',)
                                         },
                                        )
                 },
                {
                 'name': 'Project Details',
                 'items': ('project_title', 'project_proposal', 'background_summary', 'main_objectives', 'conservation_outcomes',)
                 },
                {
                 'name': 'Personnel Details',
                 'items': ('qualifications', 'qualification_attachment', 'authorised_persons_acknowledgement', 'Authorised Person',
                           'authorised_person_unavailable_explanation', 'authorised_person_change_acknowledgement',),
                 'conditional_fields': (
                                        {'conditional_field': 'authorised_person_association', 'condition': 'other',
                                         'target_fields': ('authorised_person_association_other_details',)
                                         },
                                        {'conditional_field': 'authorised_person_role', 'condition': 'handler',
                                         'target_fields': ('authorised_person_handler_type',)
                                         },
                                        ),
                 'groups': {'Authorised Person':
                            {'fields': ('authorised_person_surname', 'authorised_person_givennames', 'authorised_person_dob',
                                        'authorised_person_association', 'authorised_person_association_other_details',
                                        'authorised_person_role', 'authorised_person_handler_type', 'authorised_person_qualification',),
                             'can_create_additional': True,
                             }
                            },
                 },
                )
