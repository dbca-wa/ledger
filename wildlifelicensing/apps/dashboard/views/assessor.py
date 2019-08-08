from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q

from wildlifelicensing.apps.applications.models import Assessment, Application
from wildlifelicensing.apps.dashboard.views import base
from wildlifelicensing.apps.main.helpers import render_user_name
from wildlifelicensing.apps.main.mixins import OfficerOrAssessorRequiredMixin, \
    AssessorRequiredMixin


class TableAssessorView(AssessorRequiredMixin, base.TablesBaseView):
    """
    Same table as officer with limited filters
    """
    template_name = 'wl/dash_tables_assessor.html'

    STATUS_PENDING = 'pending'

    applications_data_url_lazy = reverse_lazy('wl_dashboard:data_application_assessor')

    @property
    def applications_columns(self):
        return [
            {
                'title': 'Lodgement Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'User'
            },
            {
                'title': 'Type'
            },
            {
                'title': 'Status'
            },
            {
                'title': 'Lodged on'
            },
            {
                'title': 'Assigned Officer'
            },
            {
                'title': 'Assigned Assessor'
            },
            {
                'title': 'Application PDF',
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]

    @property
    def applications_table_options(self):
        return {
            'pageLength': 25,
            'order': [[4, 'desc'], [0, 'desc']]
        }

    @property
    def applications_data_url(self):
        return str(self.applications_data_url_lazy)

    @property
    def applications_filters(self):
        status_filter_values = [('all', 'All')] + [(v, l) for v, l in Assessment.STATUS_CHOICES]
        return {
            'licence_type': self.get_licence_types_values(),
            'status': status_filter_values,
        }

    @property
    def get_applications_session_data(self):
        return DataTableApplicationAssessorView.get_session_data(self.request)


class DataTableApplicationAssessorView(OfficerOrAssessorRequiredMixin, base.DataTableBaseView):
    """
    The model of this table is not Application but Assessment.
    """
    APPLICATION_TYPES = dict(Application.APPLICATION_TYPE_CHOICES)
    model = Assessment
    columns = [
        'application.lodgement_number',
        'licence_type',
        'application.applicant',
        'application.application_type',
        'status',
        'application.lodgement_date',
        'application.assigned_officer',
        'assigned_assessor',
        'application_pdf',
        'action'
    ]
    order_columns = [
        'application.lodgement_number',
        ['application.licence_type.short_name', 'application.licence_type.name'],
        ['application.applicant.last_name', 'application.applicant.first_name',
         'application.applicant.email'],
        'application.application_type',
        'status',
        'application.lodgement_date',
        ['application.assigned_officer.first_name', 'application.assigned_officer.last_name',
         'application.assigned_officer.email'],
        ['assigned_assessor.first_name', 'assigned_assessor.last_name', 'assigned_assessor.email'],
        ''
    ]

    columns_helpers = dict(**{
        'licence_type': {
            'render': lambda self, instance: instance.application.licence_type.display_name,
            'search': lambda self, search: base.build_field_query(
                ['application__licence_type__short_name', 'application__licence_type__name',
                 'application__licence_type__version'],
                search)
        },
        'application.lodgement_number': {
            'search': lambda self, search: DataTableApplicationAssessorView._search_lodgement_number(search),
            'render': lambda self, instance: base.render_lodgement_number(instance.application)
        },
        'application.applicant': {
            'render': lambda self, instance: render_user_name(instance.application.applicant),
            'search': lambda self, search: base.build_field_query(
                ['application__applicant_profile__user__last_name', 'application__applicant_profile__user__first_name'],
                search
            ),
        },
        'application.application_type': {
            'render': lambda self, instance: self.APPLICATION_TYPES[instance.application.application_type]
        },
        'application.assigned_officer': {
            'render': lambda self, instance: render_user_name(instance.application.assigned_officer),
            'search': lambda self, search: base.build_field_query(
                ['application__assigned_officer__last_name', 'application__assigned_officer__first_name',
                 'application__assigned_officer__email'],
                search
            ),
        },
        'assigned_assessor': {
            'render': lambda self, instance: render_user_name(instance.assigned_assessor),
            'search': lambda self, search: base.build_field_query(
                ['assigned_assessor__last_name', 'assigned_assessor__first_name', 'assigned_assessor__email'],
                search
            ),
        },
        'application.lodgement_date': {
            'render': lambda self, instance: base.render_date(instance.application.lodgement_date),
        },
        'application_pdf': {
            'render': lambda self, instance: base.render_application_document(instance.application)
        },
        'action': {
            'render': lambda self, instance: DataTableApplicationAssessorView.render_action_column(instance),
        },
    })

    @staticmethod
    def render_action_column(obj):
        if obj.status == 'awaiting_assessment':
            return '<a href="{0}">Assess</a>'.format(
                reverse('wl_applications:enter_conditions_assessor', args=[obj.application.pk, obj.pk])
            )
        else:
            return '<a href="{0}">View (read-only)</a>'.format(
                reverse('wl_applications:view_assessment', args=[obj.application.pk, obj.pk])
            )

    @staticmethod
    def _search_lodgement_number(search):
        # testing to see if search term contains no spaces and two hyphens, meaning it's a lodgement number with a sequence
        if search and search.count(' ') == 0 and search.count('-') == 2:
            components = search.split('-')
            lodgement_number, lodgement_sequence = '-'.join(components[:2]), '-'.join(components[2:])

            return Q(application__lodgement_number__icontains=lodgement_number) & \
                   Q(application__lodgement_sequence__icontains=lodgement_sequence)
        else:
            return Q(application__lodgement_number__icontains=search)

    @staticmethod
    def filter_licence_type(value):
        return Q(application__licence_type__pk=value) if value.lower() != 'all' else None

    @staticmethod
    def filter_status(value):
        return Q(status=value) if value.lower() != 'all' else None

    def get_initial_queryset(self):
        groups = self.request.user.assessorgroup_set.all()
        assessments = self.model.objects.filter(assessor_group__in=groups).all()
        return assessments
