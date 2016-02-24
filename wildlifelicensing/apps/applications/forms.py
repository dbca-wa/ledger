from django import forms

from wildlifelicensing.apps.main.utils.form_utils import StackedForm

from models import Application


class ApplicationForm(forms.Form):
    type = forms.CharField(label='Type', widget=forms.HiddenInput)


class Regulation17ApplicationForm(ApplicationForm, StackedForm):
    FINANCIAL_BASIS_CHOICES = (('directfinancialgain', 'Direct financial gain (e.g. consulting fees)'),
                               ('indirectfinancialgain', 'Indirect financial gain (e.g. grants or funding)'),
                               ('nofinancialgain', 'No financial gain of any form'),
                               ('commercialgain', 'Commercial gain from sale of information derived from the research'))

    INSTITUTION = (('privateindividual', 'Private Individual'),
                   ('privateconsultingroup', 'Private Consulting Group'),
                   ('scientificteriaryinstution', 'Scientific instituion, university or other tertiary institution, etc'))

    qualifications = forms.CharField(label='Relevant Qualifications', widget=forms.Textarea)
    project_name = forms.CharField(label='Project Name')

    intro_and_background = forms.CharField(label='Introduction and background', widget=forms.Textarea)
    objectives = forms.CharField(label='Objectives', widget=forms.Textarea)
    client_organisation_sponsor = forms.CharField(label='Client Organisation (for consultants) or Sponsor (for students)', widget=forms.Textarea)
    methods_procedure = forms.CharField(label='Methods / Procedures', widget=forms.Textarea)

    large_cage_traps = forms.CharField(label='Large Cage traps')
    small_cage_traps = forms.CharField(label='Small Cage traps')
    elliot_traps = forms.CharField(label='Elliot traps')
    dry_pit_traps = forms.CharField(label='Dry pit traps')
    wet_pit_traps = forms.CharField(label='Wet pit traps')
    other_traps = forms.CharField(label='Other traps (specify)')
    other_techniques = forms.CharField(label='Other techniques (specify)')
    field_start_date = forms.DateField(label='Start Date')
    field_end_date = forms.DateField(label='End Date')
    location = forms.CharField(label='Location of Project', widget=forms.Textarea)
    ultimate_fate = forms.CharField(label='Ultimate fate of fauna taken', widget=forms.Textarea)
    fauna_holding = forms.CharField(label='Means, facilities and place of holding fauna', widget=forms.Textarea)
    animal_ethics_approval_number = forms.CharField(label="Relevant Institution Animal Ethics Approval Number from your organisation's AEC", widget=forms.Textarea)
    project_proposal_attached = forms.BooleanField(label='Project proposal attached')
    financial_basis = forms.ChoiceField(label='Financial Basis', choices=FINANCIAL_BASIS_CHOICES)
    institution = forms.ChoiceField(label='Institution', choices=INSTITUTION)
    additional_personnel_1_name = forms.CharField(label='Name')
    additional_personnel_1_address = forms.CharField(label='Residential Address')
    additional_personnel_1_qualification = forms.CharField(label='Qualification') 
    additional_personnel_2_name = forms.CharField(label='Name')
    additional_personnel_2_address = forms.CharField(label='Residential Address')
    additional_personnel_2_qualification = forms.CharField(label='Qualification') 
    written_permission = forms.BooleanField(label='Permission')
    anticipated_outcomes = forms.CharField(label='Anticipated outcomes and conservation / management benefits', widget=forms.Textarea)
    communication_of_results = forms.CharField(label='Communication of results', widget=forms.Textarea)
    referee_1_name = forms.CharField(label='Referee 1 Name')
    referee_1_qualification = forms.CharField(label='Referee 1 Qualification')
    referee_1_contact_details = forms.CharField(label='Referee 1 Contact Details')
    referee_2_name = forms.CharField(label='Referee 2 Name')
    referee_2_qualification = forms.CharField(label='Referee 2 Qualification')
    referee_2_contact_details = forms.CharField(label='Referee 2 Contact Details')

    class Stack:
        stack = (
                 dict(
                      type = 'field',
                      field = 'qualifications',
                 ),
                 dict(
                      type = 'field',
                      field = 'project_name',
                 ),
                 dict(
                      type = 'group',
                      label = 'Project Details',
                      fields = ('intro_and_background','objectives', 'client_organisation_sponsor', 'methods_procedure',),
                 ),
                 dict(
                      type = 'conditional_group',
                      label = 'Collecting will be done by additional personnel',
                      fields = ('additional_personnel_1_name','additional_personnel_1_address', 'additional_personnel_1_qualification',
                                'additional_personnel_2_name','additional_personnel_2_address', 'additional_personnel_2_qualification'),
                 ),
                )
