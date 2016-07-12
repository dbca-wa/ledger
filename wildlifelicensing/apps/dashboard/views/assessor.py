from django.core.urlresolvers import reverse
from django.db.models import Q

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
        data['applications']['ajax']['url'] = reverse('wl_dashboard:data_application_assessor')
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
            'search': lambda self, search: DataTableApplicationAssessorView._search_lodgement_number(self, search),
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
        return '<a href="{0}">Assess</a>'.format(
            reverse('wl_applications:enter_conditions_assessor', args=[obj.application.pk, obj.pk])
        )

    @staticmethod
    def _search_lodgement_number(self, search):
        # testing to see if search term contains no spaces and two hyphens, meaning it's a lodgement number with a sequence
        if search and search.count(' ') == 0 and search.count('-') == 2:
            components = search.split('-')
            lodgement_number, lodgement_sequence = '-'.join(components[:2]), '-'.join(components[2:])

            return Q(application__lodgement_number__icontains=lodgement_number) & \
                Q(application__lodgement_sequence__icontains=lodgement_sequence)
        else:
            return Q(application__lodgement_number__icontains=search)

    def get_initial_queryset(self):
        groups = self.request.user.assessorgroup_set.all()
        assessments = Assessment.objects.filter(assessor_group__in=groups).filter(status='awaiting_assessment')
        return assessments
