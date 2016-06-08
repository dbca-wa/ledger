from django.core.urlresolvers import reverse

from wildlifelicensing.apps.applications.models import Assessment
from wildlifelicensing.apps.dashboard.views import base
from wildlifelicensing.apps.dashboard.views.officer import TableApplicationsOfficerView
from wildlifelicensing.apps.main.helpers import render_user_name
from wildlifelicensing.apps.main.mixins import OfficerOrAssessorRequiredMixin, \
    AssessorRequiredMixin


class TableAssessorView(AssessorRequiredMixin, TableApplicationsOfficerView):
    """
    Same table as officer with limited filters
    """
    template_name = 'wl/dash_tables_assessor.html'

    def _build_data(self):
        data = super(TableAssessorView, self)._build_data()
        data['applications']['columnDefinitions'] = [
            {
                'title': 'Lodge Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'User'
            },
            {
                'title': 'Lodged on'
            },
            {
                'title': 'Assigned Officer'
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['applications']['ajax']['url'] = reverse('dashboard:data_application_assessor')
        return data


class DataTableApplicationAssessorView(OfficerOrAssessorRequiredMixin, base.DataTableBaseView):
    """
    Model of this table is not Application but Assessment
     see: get_initial_queryset method
    """
    columns = [
        'application.lodgement_number',
        'application.licence_type.code',
        'application.applicant_profile.user',
        'application.lodgement_date',
        'application.assigned_officer',
        'action'
    ]
    order_columns = [
        'application.lodgement_number',
        'application.licence_type.code',
        ['application.applicant_profile.user.last_name', 'application.applicant_profile.user.first_name',
         'application.applicant_profile.user.email'],
        'application.lodgement_date',
        ['application.assigned_officer.first_name', 'application.assigned_officer.last_name',
         'application.assigned_officer.email'], ''
    ]

    columns_helpers = dict(**{
        'application.lodgement_number': {
            'render': lambda self, instance: base.render_lodgement_number(instance.application)
        },
        'application.applicant_profile.user': {
            'render': lambda self, instance: render_user_name(instance.application.applicant_profile.user),
            'search': lambda self, search: base.build_field_query(
                ['application__applicant_profile__user__last_name', 'application__applicant_profile__user__first_name'],
                search
            ),
        },
        'application.assigned_officer': {
            'render': lambda self, instance: render_user_name(instance.application.assigned_officer),
            'search': lambda self, search: base.build_field_query(
                ['application__assigned_officer__last_name', 'application__assigned_officer__first_name',
                 'application__assigned_officer__email'],
                search
            ),
        },
        'action': {
            'render': lambda self, instance: DataTableApplicationAssessorView.render_action_column(instance),
        },
        'application.lodgement_date': {
            'render': lambda self, instance: base.render_date(instance.application.lodgement_date),
        },
    })

    @staticmethod
    def render_action_column(obj):
        return '<a href="{0}">Review</a>'.format(
            reverse('applications:enter_conditions_assessor', args=[obj.application.pk, obj.pk])
        )

    def get_initial_queryset(self):
        groups = self.request.user.assessorgroup_set.all()
        assessments = Assessment.objects.filter(assessor_group__in=groups).filter(
            status='awaiting_assessment')
        return assessments
