from django import forms

from models import Application


class ApplicationForm(forms.Form):
    type = forms.CharField(label='Type', widget=forms.HiddenInput)
    
    structure = {
                 'heading': 'Application form',
                 'hasMenu': True,
                 'childrenAnchorPointID': 'baseChildrenAnchorPoint',
                 'children': (
                              {
                               'type': 'section',
                               'context': {
                                           'id': 'projectTypeSection',
                                           'label': 'Project Type',
                               },
                               'childrenAnchorPointID': 'projectTypeChildren',
                               'children': (
                                            {'type': 'select_field',
                                             'context': {
                                                         'id': 'projectType',
                                                         'label': 'Which of the following describes your project?',
                                                         'name': 'project_type',
                                                         'options': [{'value': 'survey', 'label': 'Survey'}, {'value': 'monitoring', 'label': 'Monitorying'},
                                                                     {'value': 'research', 'label': 'Research'}],
                                                         }
                                             },
                                            ) 
                               },
                              {
                               'type': 'section',
                               'context': {
                                           'id': 'financialBasisSection',
                                           'label': 'Financial Basis',
                                           'children': (
                                                        
                                                        ) 
                                },
                               'childrenAnchorPointID': 'financialBasisSectionChildren',
                               'children': (
                                            {'type': 'select_field',
                                             'context': {
                                                         'id': 'financialBasis',
                                                         'label': 'How is your project funded?',
                                                         'name': 'project_type',
                                                         'options': [{'value': 'grant', 'label': 'Grant / Sponsored'},
                                                                     {'value': 'contract', 'label': 'Contract / Consulting'},
                                                                     {'value': 'other', 'label': 'Other - Please provide details'}],
                                                         },
                                             'childrenAnchorPointID': 'financialBasisChildren',
                                             'condition': 'other',
                                             'children': (
                                                          {
                                                           'type': 'text_area_field',
                                                           'context': {
                                                                       'id': 'financialDetails',
                                                                       'label': 'Affiliated Organisation / Client / Sponsor',
                                                                       'name': 'financial_details',
                                                            },
                                                           },
                                                          )
                                             },
                                            )
                               },
                              {
                               'type': 'section',
                               'context': {
                                           'id': 'projectDetails',
                                           'label': 'Project Details',
                                           'children': (
                                                        
                                                        ) 
                                           }
                               },
                              )
    }