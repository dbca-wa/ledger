import datetime
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q

from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.dashboard.views import base
from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.returns.models import Return
from wildlifelicensing.apps.returns.utils import is_return_overdue, is_return_due_soon

logger = logging.getLogger(__name__)


def _get_user_applications(user):
    return Application.objects.filter(applicant_profile__user=user).exclude(customer_status__in=['temp', 'discarded'])


class TableCustomerView(LoginRequiredMixin, base.TablesBaseView):
    """
    This view includes the table definitions and filters for applications, licences and returns for the customers
    as it is displayed on the same page.
    """
    template_name = 'wl/dash_tables_customer.html'

    applications_data_url_lazy = reverse_lazy('wl_dashboard:data_application_customer')
    licences_data_url_lazy = reverse_lazy('wl_dashboard:data_licences_customer')
    returns_data_url_lazy = reverse_lazy('wl_dashboard:data_returns_customer')

    #############
    # Applications
    #############
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
                'title': 'Profile'
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
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]

    @property
    def applications_table_options(self):
        return {
            'pageLength': 25,
            'order': [[0, 'desc'], [4, 'desc']]
        }

    @property
    def applications_data_url(self):
        return str(self.applications_data_url_lazy)

    @property
    def applications_filters(self):
        # no filters
        return {}

    @property
    def get_applications_session_data(self):
        # no session
        return {}

    #############
    # Licences
    #############
    @property
    def licences_columns(self):
        return [
            {
                'title': 'Licence Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'Issue Date'
            },
            {
                'title': 'Start Date'
            },
            {
                'title': 'Expiry Date'
            },
            {
                'title': 'Licence',
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Status'
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]

    @property
    def licences_table_options(self):
        return {
            'pageLength': 10,
            'order': [[4, 'desc']]
        }

    @property
    def licences_data_url(self):
        return str(self.licences_data_url_lazy)

    @property
    def licences_filters(self):
        # no filters
        return {}

    @property
    def get_licences_session_data(self):
        # no session
        return {}

    #############
    # Returns
    #############
    @property
    def returns_columns(self):
        return [
            {
                'title': 'Lodgement Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'Lodged On'
            },
            {
                'title': 'Due On'
            },
            {
                'title': 'Status'
            },
            {
                'title': 'Licence',
                'orderable': False
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]

    @property
    def returns_table_options(self):
        return {
            'pageLength': 10,
            'order': [[3, 'desc']]
        }

    @property
    def returns_data_url(self):
        return str(self.returns_data_url_lazy)

    @property
    def returns_filters(self):
        # no filters
        return {}

    @property
    def get_returns_session_data(self):
        return {}


class DataTableApplicationCustomerView(base.DataTableApplicationBaseView):
    columns = [
        'lodgement_number',
        'licence_type',
        'applicant_profile',
        'application_type',
        'customer_status',
        'lodgement_date',
        'action'
    ]
    order_columns = [
        'lodgement_number',
        ['licence_type.short_name', 'licence_type.name'],
        'applicant_profile',
        'application_type',
        'customer_status',
        'lodgement_date',
        '']

    columns_helpers = dict(base.DataTableApplicationBaseView.columns_helpers.items(), **{
        'lodgement_number': {
            'search': lambda self, search: DataTableApplicationCustomerView._search_lodgement_number(search),
            'render': lambda self, instance: base.render_lodgement_number(instance)
        },
        'action': {
            'render': lambda self, instance: DataTableApplicationCustomerView.render_action_column(instance),
        },
        'lodgement_date': {
            'render': lambda self, instance: base.render_date(instance.lodgement_date)
        },
    })

    @staticmethod
    def _search_lodgement_number(search):
        # testing to see if search term contains no spaces and two hyphens,
        # meaning it's a lodgement number with a sequence
        if search and search.count(' ') == 0 and search.count('-') == 2:
            components = search.split('-')
            lodgement_number, lodgement_sequence = '-'.join(components[:2]), '-'.join(components[2:])

            return Q(lodgement_number__icontains=lodgement_number) & Q(lodgement_sequence__icontains=lodgement_sequence)
        else:
            return Q(lodgement_number__icontains=search)

    @staticmethod
    def render_action_column(obj):
        status = obj.customer_status
        if status == 'draft':
            result = '<a href="{0}">{1}</a>'.format(
                reverse('wl_applications:edit_application', args=[obj.pk]),
                'Continue'
            )
        elif status == 'amendment_required' or status == 'id_and_amendment_required':
            result = '<a href="{0}">{1}</a>'.format(
                reverse('wl_applications:edit_application', args=[obj.pk]),
                'Amend application'
            )
        elif status == 'id_required' and obj.id_check_status == 'awaiting_update':
            result = '<a href="{0}">{1}</a>'.format(
                reverse('wl_main:identification'),
                'Update ID')
        else:
            result = '<a href="{0}"">{1}</a>'.format(
                reverse('wl_applications:view_application', args=[obj.pk]),
                'View application (read-only)'
            )
        # Add discard action
        if obj.is_discardable:
            result += ' / <a href="{}">{}</a>'.format(
                reverse('wl_applications:discard_application', args=[obj.pk]),
                'Discard'
            )
        return result

    def get_initial_queryset(self):
        return _get_user_applications(self.request.user)


class DataTableLicencesCustomerView(base.DataTableBaseView):
    model = WildlifeLicence
    columns = [
        'licence_number',
        'licence_type',
        'issue_date',
        'start_date',
        'end_date',
        'licence',
        'status',
        'action']
    order_columns = [
        'licence_number',
        ['licence_type.short_name', 'licence_type.name'],
        'issue_date',
        'start_date',
        'end_date',
        '',
        '']

    columns_helpers = dict(base.DataTableBaseView.columns_helpers.items(), **{
        'licence_number': {
            'search': lambda self, search: DataTableLicencesCustomerView._search_licence_number(search),
            'render': lambda self, instance: base.render_licence_number(instance)
        },
        'issue_date': {
            'render': lambda self, instance: base.render_date(instance.issue_date)
        },
        'start_date': {
            'render': lambda self, instance: base.render_date(instance.start_date)
        },
        'end_date': {
            'render': lambda self, instance: base.render_date(instance.end_date)
        },
        'licence': {
            'render': lambda self, instance: base.render_licence_document(instance)
        },
        'status': {
            'render': lambda self, instance: self._render_status(instance)
        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        }
    })

    @staticmethod
    def _render_status(instance):
        try:
            application = Application.objects.get(licence=instance)
            replacing_application = Application.objects.get(previous_application=application)

            if replacing_application.licence is not None and replacing_application.licence.is_issued:
                if replacing_application.application_type == 'amendment':
                    return 'Amended'
                else:
                    return 'Renewed'
        except Application.DoesNotExist:
            pass

        if instance.end_date is not None:
            expiry_days = (instance.end_date - datetime.date.today()).days
            if instance.end_date < datetime.date.today():
                return '<span class="label label-danger">Expired</span>'
            elif expiry_days <= 30 and instance.is_renewable:
                return '<span class="label label-warning">Due for renewal</span>'
            else:
                return 'Current'
        else:
            # should not happen
            message = "The licence ref:{ref} pk:{pk} has no end date!".format(
                ref=instance.reference,
                pk=instance.pk
            )
            logger.exception(Exception(message))
            return 'Current'

    @staticmethod
    def _render_action(instance):
        try:
            application = Application.objects.get(licence=instance)
            replacing_application = Application.objects.get(previous_application=application)
            if replacing_application.licence is None or not replacing_application.licence.is_issued:
                if replacing_application.application_type == 'amendment':
                    return 'Amendment Pending'
                else:
                    return 'Renewal Pending'
            else:
                return 'N/A'
        except Application.DoesNotExist:
            pass

        renew_url = reverse('wl_applications:renew_licence', args=(instance.pk,))
        amend_url = reverse('wl_applications:amend_licence', args=(instance.pk,))

        if instance.end_date is not None:
            expiry_days = (instance.end_date - datetime.date.today()).days
            if instance.is_renewable:
                if 30 >= expiry_days > 0:
                    return '<a href="{0}">Amend</a> / <a href="{1}">Renew</a>'.format(amend_url, renew_url)
                elif expiry_days <= 0:
                    return '<a href="{0}">Renew</a>'.format(renew_url)
            if instance.end_date >= datetime.date.today():
                return '<a href="{0}">Amend</a>'.format(amend_url)
            else:
                return 'N/A'
        else:
            # should not happen
            message = "The licence ref:{ref} pk:{pk} has no end date!".format(
                ref=instance.reference,
                pk=instance.pk
            )
            logger.exception(Exception(message))
            return 'N/A'

    @staticmethod
    def _search_licence_number(search):
        # testing to see if search term contains no spaces and two hyphens,
        # meaning it's a lodgement number with a sequence
        if search and search.count(' ') == 0 and search.count('-') == 2:
            components = search.split('-')
            licence_number, licence_sequence = '-'.join(components[:2]), '-'.join(components[2:])

            return Q(licence_number__icontains=licence_number) & Q(licence_sequence__icontains=licence_sequence)
        else:
            return Q(licence_number__icontains=search)

    def get_initial_queryset(self):
        # should only see the issued customer's licence
        return WildlifeLicence.objects.filter(holder=self.request.user).filter(licence_number__isnull=False)


class DataTableReturnsCustomerView(base.DataTableBaseView):
    model = Return
    columns = [
        'lodgement_number',
        'licence.licence_type',
        'lodgement_date',
        'due_date',
        'status',
        'licence',
        'action'
    ]
    order_columns = [
        'lodgement_number',
        ['licence.licence_type.short_name', 'licence.licence_type.name'],
        'lodgement_date',
        'due_date',
        'status',
        '',
        ''
    ]
    columns_helpers = {
        'lodgement_number': {
            'render': lambda self, instance: instance.lodgement_number
        },
        'licence.licence_type': {
            'render': lambda self, instance: instance.licence.licence_type.display_name,
            'search': lambda self, search: base.build_field_query(
                ['licence__licence_type__short_name', 'licence__licence_type__name', 'licence__licence_type__version'],
                search)
        },
        'lodgement_date': {
            'render': lambda self, instance: base.render_date(instance.lodgement_date)
        },
        'due_date': {
            'render': lambda self, instance: base.render_date(instance.due_date)
        },
        'licence': {
            'render': lambda self, instance: base.render_licence_number(instance.licence),
            'search': lambda self, search: DataTableReturnsCustomerView._search_licence_number(search)
        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        },
        'status': {
            'render': lambda self, instance: self._render_status(instance)
        }
    }

    @staticmethod
    def _render_action(instance):
        if instance.status == 'current':
            url = reverse('wl_returns:enter_return', args=(instance.pk,))
            return '<a href="{0}">Enter Return</a>'.format(url)
        elif instance.status == 'draft':
            url = reverse('wl_returns:enter_return', args=(instance.pk,))
            return '<a href="{0}">Edit Return</a>'.format(url)
        elif instance.status == 'amendment_required':
            url = reverse('wl_returns:enter_return', args=(instance.pk,))
            return '<a href="{0}">Amend Return</a>'.format(url)
        else:
            url = reverse('wl_returns:view_return', args=(instance.pk,))
            return '<a href="{0}">View Return (read-only)</a>'.format(url)

    @staticmethod
    def _render_status(instance):
        status = instance.status
        if status == 'current':
            if is_return_overdue(instance):
                return '<span class="label label-danger">Overdue</span>'
            elif is_return_due_soon(instance):
                return '<span class="label label-warning">Due soon</span>'
            else:
                return 'Current'
        else:
            suffix = ' (Nil)' if status == 'submitted' and instance.nil_return else ''
            return dict(Return.STATUS_CHOICES)[status] + suffix

    @staticmethod
    def _search_licence_number(search):
        # testing to see if search term contains no spaces and two hyphens,
        # meaning it's a lodgement number with a sequence
        if search and search.count(' ') == 0 and search.count('-') == 2:
            components = search.split('-')
            licence_number, licence_sequence = '-'.join(components[:2]), '-'.join(components[2:])

            return Q(licence__licence_number__icontains=licence_number) & Q(
                licence__licence_sequence__icontains=licence_sequence)
        else:
            return Q(licence__licence_number__icontains=search)

    def get_initial_queryset(self):
        return Return.objects.filter(licence__holder=self.request.user).exclude(status='future')
