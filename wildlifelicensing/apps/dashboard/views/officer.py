import datetime
import logging

from dateutil.parser import parse as date_parse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.http.response import HttpResponse

from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.dashboard.views import base
from wildlifelicensing.apps.dashboard.views.customer import DataTableReturnsCustomerView, \
    DataTableApplicationCustomerView
from wildlifelicensing.apps.main.helpers import get_all_officers
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.main.pdf import bulk_licence_renewal_pdf_bytes
from wildlifelicensing.apps.returns.models import Return
from wildlifelicensing.apps.returns.utils import is_return_overdue, is_return_due_soon

logger = logging.getLogger(__name__)


def _render_cover_letter_document(licence):
    if licence is not None and licence.cover_letter_document is not None:
        return '<a href="{0}" target="_blank">View PDF</a><img height="20" src="{1}"></img>'.format(
            licence.cover_letter_document.file.url, static('wl/img/pdf.png'))
    else:
        return ''


class DashboardOfficerTreeView(OfficerRequiredMixin, base.DashboardTreeViewBase):
    template_name = 'wl/dash_tree.html'
    title = 'Officer Dashboard'

    def _build_tree_nodes(self):
        # Applications
        # The draft status is excluded from the officer status list
        url = reverse_lazy('wl_dashboard:tables_applications_officer')
        result = []
        statuses = base.get_processing_statuses_but_draft()
        all_applications = Application.objects.filter(processing_status__in=[s[0] for s in statuses])
        # the next query param is necessary to avoid loading parameters from the session.
        query = {
            'show': 'applications'
        }
        all_applications_node = self._create_node('All applications', href=base.build_url(url, query),
                                                  count=all_applications.count())
        all_applications_node['state']['expanded'] = False
        for s_value, s_title in statuses:
            applications = all_applications.filter(processing_status=s_value)
            if applications.count() > 0:
                query = {
                    'application_status': s_value,
                }
                href = base.build_url(url, query)
                node = self._create_node(s_title, href=href, count=applications.count())
                self._add_node(all_applications_node, node)

        assigned_applications = all_applications.filter(assigned_officer=self.request.user)
        query = {
            'application_assignee': self.request.user.pk
        }
        assigned_applications_node = self._create_node('My assigned applications',
                                                       href=base.build_url(url, query),
                                                       count=assigned_applications.count())
        assigned_applications_node['state']['expanded'] = True
        for s_value, s_title in statuses:
            applications = assigned_applications.filter(processing_status=s_value)
            if applications.count() > 0:
                query.update({
                    'application_status': s_value
                })
                href = base.build_url(url, query)
                node = self._create_node(s_title, href=href, count=applications.count())
                self._add_node(assigned_applications_node, node)
        result.append(assigned_applications_node)

        on_behalf_pending_applications_count = \
            DataTableApplicationsOfficerOnBehalfView._get_proxy_applications(self.request.user).filter(
                DataTableApplicationsOfficerOnBehalfView.filter_status(
                    TablesApplicationsOfficerView.STATUS_PENDING)).count()

        on_behalf_overdue_returns_count = DataTableReturnsOfficerOnBehalfView._get_proxy_returns(
            self.request.user).filter(
            DataTableReturnsOfficerOnBehalfView.filter_status(TablesReturnsOfficerView.OVERDUE_FILTER)).count()

        total_on_behalf = on_behalf_pending_applications_count + on_behalf_overdue_returns_count
        if total_on_behalf > 0:
            url = reverse_lazy('wl_dashboard:tables_officer_onbehalf')
            # to disable session data we pass a query parameter
            query = {
                'session': False
            }
            url = base.build_url(url, query)
            on_behalf_node = self._create_node('My proxy page', href=url, count=total_on_behalf)
            query = {
                'show': 'applications',
                'application_status': 'pending'
            }
            href = base.build_url(url, query)
            on_behalf_applications_node = self._create_node('Pending Applications',
                                                            href=href,
                                                            count=on_behalf_pending_applications_count)

            query = {
                'show': 'returns',
            }
            href = base.build_url(url, query)
            on_behalf_returns_node = self._create_node('Overdue Returns',
                                                       href=href,
                                                       count=on_behalf_overdue_returns_count)
            self._add_node(on_behalf_node, on_behalf_applications_node)
            self._add_node(on_behalf_node, on_behalf_returns_node)
            on_behalf_node['state']['expanded'] = False
            result.append(on_behalf_node)

        result.append(all_applications_node)

        # Licences
        url = reverse_lazy('wl_dashboard:tables_licences_officer')
        query = {
            'show': 'licences'
        }
        url = base.build_url(url, query)
        all_licences_node = self._create_node('All licences', href=url, count=WildlifeLicence.objects.count())
        result.append(all_licences_node)

        # Returns
        url = reverse_lazy('wl_dashboard:tables_returns_officer')
        query = {
            'show': 'returns'
        }
        url = base.build_url(url, query)
        all_returns_node = self._create_node('All returns', href=url,
                                             count=Return.objects.exclude(status__in=['draft', 'future']).count())
        result.append(all_returns_node)

        return result


class TablesApplicationsOfficerView(OfficerRequiredMixin, base.TablesBaseView):
    template_name = 'wl/dash_tables_applications_officer.html'

    STATUS_PENDING = 'pending'

    applications_data_url_lazy = reverse_lazy('wl_dashboard:data_application_officer')

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
                'title': 'Status',
            },
            {
                'title': 'Lodged on'
            },
            {
                'title': 'Assignee'
            },
            {
                'title': 'Payment',
                'searchable': False,
                'orderable': False
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
        status_filter_values = \
            [('all', 'All')] + [(self.STATUS_PENDING, self.STATUS_PENDING.capitalize())] + \
            base.get_processing_statuses_but_draft()

        assignee_filter_values = [('all', 'All')] + [(user.pk, base.render_user_name(user),) for user in
                                                     get_all_officers()]
        return {
            'licence_type': self.get_licence_types_values(),
            'status': status_filter_values,
            'assignee': assignee_filter_values
        }

    @property
    def get_applications_session_data(self):
        return DataTableApplicationsOfficerView.get_session_data(self.request)


class DataTableApplicationsOfficerView(OfficerRequiredMixin, base.DataTableApplicationBaseView):
    columns = [
        'lodgement_number',
        'licence_type',
        'applicant',
        'application_type',
        'processing_status',
        'lodgement_date',
        'assigned_officer',
        'payment',
        'application_pdf',
        'action'
    ]
    order_columns = [
        'lodgement_number',
        ['licence_type.short_name', 'licence_type.name'],
        ['applicant.last_name', 'applicant.first_name', 'applicant.email'],
        'application_type',
        'processing_status',
        'lodgement_date',
        ['assigned_officer.first_name', 'assigned_officer.last_name', 'assigned_officer.email'],
        ''
        ''
    ]

    columns_helpers = dict(base.DataTableApplicationBaseView.columns_helpers.items(), **{
        'lodgement_number': {
            'search': lambda self, search: DataTableApplicationsOfficerView._search_lodgement_number(search),
            'render': lambda self, instance: base.render_lodgement_number(instance),
        },
        'lodgement_date': {
            'render': lambda self, instance: base.render_date(instance.lodgement_date)
        },
        'assigned_officer': {
            'search': lambda self, search: base.build_field_query(
                ['assigned_officer__last_name', 'assigned_officer__first_name'],
                search
            ),
            'render': lambda self, instance: base.render_user_name(instance.assigned_officer)
        },
        'payment': {
            'render': lambda self, instance: base.render_payment(instance, self.request.build_absolute_uri(
                reverse('wl_dashboard:tables_applications_officer')))
        },
        'application_pdf': {
            'render': lambda self, instance: base.render_application_document(instance)
        },
        'action': {
            'render': lambda self, instance: DataTableApplicationsOfficerView._render_action_column(instance),
        }
    })

    SESSION_SAVE_SETTINGS = True

    @staticmethod
    def _get_pending_processing_statuses():
        return [s[0] for s in Application.PROCESSING_STATUS_CHOICES
                if s[0] != 'draft' and s[0] != 'issued' and s[0] != 'declined']

    @staticmethod
    def filter_status(value):
        # officers should not see applications in draft mode.
        if value.lower() == TablesApplicationsOfficerView.STATUS_PENDING:
            return Q(processing_status__in=DataTableApplicationsOfficerView._get_pending_processing_statuses())
        return Q(processing_status=value) if value != 'all' else ~Q(customer_status='draft')

    @staticmethod
    def _search_lodgement_number(search):
        # testing to see if search term contains no spaces and two hyphens, meaning it's a lodgement number with a sequence
        if search and search.count(' ') == 0 and search.count('-') == 2:
            components = search.split('-')
            lodgement_number, lodgement_sequence = '-'.join(components[:2]), '-'.join(components[2:])

            return Q(lodgement_number__icontains=lodgement_number) & Q(lodgement_sequence__icontains=lodgement_sequence)
        else:
            return Q(lodgement_number__icontains=search)

    @staticmethod
    def _render_action_column(obj):
        issued = obj.processing_status == 'issued' and obj.licence is not None and obj.licence.licence_document is not None
        discarded = obj.processing_status == 'discarded'
        declined = obj.processing_status == 'declined'

        action = ''
        if obj.processing_status == 'ready_for_conditions':
            action += '<a href="{0}">Enter Conditions</a>'.format(
                reverse('wl_applications:enter_conditions', args=[obj.pk]),
            )
        elif obj.processing_status == 'ready_to_issue':
            action += '<a href="{0}">Issue Licence</a>'.format(
                reverse('wl_applications:issue_licence', args=[obj.pk]),
            )
        elif any([issued, discarded, declined]):
            action += '<a href="{0}">{1}</a>'.format(
                reverse('wl_applications:view_application_officer', args=[obj.pk]),
                'View (read-only)'
            )
        else:
            action += '<a href="{0}">Process</a>'.format(
                reverse('wl_applications:process', args=[obj.pk]),
            )

        if obj.invoice_reference:
            url = '{}?invoice={}'.format(reverse('payments:invoice-payment'),obj.invoice_reference)
            action += '<br \><a target="_blank" href="{0}"> View Payment</a>'.format(
                url
            )

        return action

    def get_initial_queryset(self):
        return Application.objects.exclude(processing_status__in=['draft', 'temp']).exclude(customer_status='temp')


class TablesOfficerOnBehalfView(OfficerRequiredMixin, base.TablesBaseView):
    template_name = 'wl/dash_tables_officer_onbehalf.html'

    applications_data_url_lazy = reverse_lazy('wl_dashboard:data_application_officer_onbehalf')
    returns_data_url_lazy = reverse_lazy('wl_dashboard:data_returns_officer_onbehalf')

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
        status_filter_values = \
            [('all', 'All'),
             (
                TablesApplicationsOfficerView.STATUS_PENDING,
                TablesApplicationsOfficerView.STATUS_PENDING.capitalize()
             ),
             ] + \
            [s for s in Application.PROCESSING_STATUS_CHOICES]

        return {
            'licence_type': self.get_licence_types_values(),
            'status': status_filter_values,
        }

    @property
    def get_applications_session_data(self):
        return DataTableApplicationsOfficerOnBehalfView.get_session_data(self.request)

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
                'title': 'User'
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
            'pageLength': 25,
            'order': [[0, 'asc']]
        }

    @property
    def returns_data_url(self):
        return str(self.returns_data_url_lazy)

    @property
    def returns_filters(self):
        status_filter_values = \
            [
                (TablesReturnsOfficerView.STATUS_FILTER_ALL_BUT_DRAFT_OR_FUTURE, 'All (but draft or future)'),
                (TablesReturnsOfficerView.OVERDUE_FILTER, TablesReturnsOfficerView.OVERDUE_FILTER.capitalize())
            ] + list(Return.STATUS_CHOICES)
        return {
            'licence_type': self.get_licence_types_values(),
            'status': status_filter_values,
        }

    @property
    def get_returns_session_data(self):
        return DataTableReturnsOfficerOnBehalfView.get_session_data(self.request)


class DataTableApplicationsOfficerOnBehalfView(OfficerRequiredMixin, base.DataTableApplicationBaseView):
    columns = [
        'lodgement_number',
        'licence_type',
        'applicant',
        'application_type',
        'processing_status',
        'lodgement_date',
        'action'
    ]
    order_columns = [
        'lodgement_number',
        ['licence_type.short_name', 'licence_type.name'],
        ['applicant.last_name', 'applicant.first_name', 'applicant.email'],
        'application_type',
        'processing_status',
        'lodgement_date',
        '']

    columns_helpers = dict(base.DataTableApplicationBaseView.columns_helpers.items(), **{
        'lodgement_number': {
            'render': lambda self, instance: base.render_lodgement_number(instance)
        },
        'lodgement_date': {
            'render': lambda self, instance: base.render_date(instance.lodgement_date)
        },
        'action': {
            'render': lambda self, instance: self._render_action_column(instance),
        },
    })

    @staticmethod
    def _get_pending_processing_statuses():
        return [s[0] for s in Application.PROCESSING_STATUS_CHOICES
                if s[0] != 'issued' and s[0] != 'declined' and s[0] != 'temp']

    @staticmethod
    def _render_action_column(obj):
        # same as a customer
        return DataTableApplicationCustomerView.render_action_column(obj)

    @staticmethod
    def _get_proxy_applications(user):
        return Application.objects.filter(proxy_applicant=user).exclude(customer_status='temp')

    @staticmethod
    def filter_status(value):
        if value.lower() == TablesApplicationsOfficerView.STATUS_PENDING:
            return Q(processing_status__in=DataTableApplicationsOfficerOnBehalfView._get_pending_processing_statuses())
        else:
            return base.DataTableApplicationBaseView.filter_status(value)

    def get_initial_queryset(self):
        return self._get_proxy_applications(self.request.user)


class TablesLicencesOfficerView(OfficerRequiredMixin, base.TablesBaseView):
    template_name = 'wl/dash_tables_licences_officer.html'

    STATUS_FILTER_ACTIVE = 'active'
    STATUS_FILTER_RENEWABLE = 'renewable'
    STATUS_FILTER_EXPIRED = 'expired'
    STATUS_FILTER_ALL = 'all'

    licences_data_url_lazy = reverse_lazy('wl_dashboard:data_licences_officer')

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
                'title': 'User'
            },
            {
                'title': 'Issue Date'
            },
            {
                'title': 'Expiry Date'
            },
            {
                'title': 'Licence PDF',
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Cover Letter',
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Renewal Letter',
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Status',
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
    def licences_table_options(self):
        return {
            'pageLength': 25,
            'order': [[3, 'desc'], [0, 'desc']]
        }

    @property
    def licences_data_url(self):
        return str(self.licences_data_url_lazy)

    @property
    def licences_filters(self):
        status_filter_values = [
            (self.STATUS_FILTER_ALL, self.STATUS_FILTER_ALL.capitalize()),
            (self.STATUS_FILTER_ACTIVE, self.STATUS_FILTER_ACTIVE.capitalize()),
            (self.STATUS_FILTER_RENEWABLE,
             self.STATUS_FILTER_RENEWABLE.capitalize() + ' (expires within 30 days)'),
            (self.STATUS_FILTER_EXPIRED, self.STATUS_FILTER_EXPIRED.capitalize()),
        ]
        return {
            'licence_type': self.get_licence_types_values(),
            'status': status_filter_values,
            'expiry_after': None,
            'expiry_before': None
        }

    @property
    def get_licences_session_data(self):
        return DataTableLicencesOfficerView.get_session_data(self.request)

    def get_licences_context_data(self):
        result = super(TablesLicencesOfficerView, self).get_licences_context_data()
        # specific stuff
        result['bulkRenewalURL'] = reverse('wl_dashboard:bulk_licence_renewal_pdf')
        return result


class DataTableLicencesOfficerView(OfficerRequiredMixin, base.DataTableBaseView):
    model = WildlifeLicence
    columns = [
        'licence_number',
        'licence_type',
        'profile.user',
        'issue_date',
        'end_date',
        'licence',
        'cover_letter',
        'renewal_letter',
        'status',
        'action']
    order_columns = [
        'licence_number',
        ['licence_type.short_name', 'licence_type.name'],
        ['profile.user.last_name', 'profile.user.first_name'],
        'issue_date',
        'end_date',
        '',
        '']

    columns_helpers = dict(base.DataTableBaseView.columns_helpers.items(), **{
        'licence_number': {
            'search': lambda self, search: DataTableLicencesOfficerView._search_licence_number(search),
            'render': lambda self, instance: base.render_licence_number(instance)
        },
        'profile.user': {
            'render': lambda self, instance: base.render_user_name(instance.profile.user, first_name_first=False),
            'search': lambda self, search: base.build_field_query([
                'profile__user__last_name', 'profile__user__first_name'],
                search),
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
        'cover_letter': {
            'render': lambda self, instance: _render_cover_letter_document(instance)
        },
        'renewal_letter': {
            'render': lambda self, instance: self._render_renewal_letter(instance)
        },
        'status': {
            'render': lambda self, instance: self._render_status(instance)
        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        }
    })

    @staticmethod
    def filter_status(value):
        today = datetime.date.today()
        if value == TablesLicencesOfficerView.STATUS_FILTER_ACTIVE:
            return Q(start_date__lte=today) & Q(end_date__gte=today)
        elif value == TablesLicencesOfficerView.STATUS_FILTER_RENEWABLE:
            return Q(is_renewable=True) & Q(end_date__gte=today) & Q(end_date__lte=today + datetime.timedelta(days=30))
        elif value == TablesLicencesOfficerView.STATUS_FILTER_EXPIRED:
            return Q(end_date__lt=today)
        else:
            return None

    @staticmethod
    def filter_licence_type(value):
        if value.lower() != 'all':
            return Q(licence_type__pk=value)
        else:
            return None

    @staticmethod
    def filter_expiry_after(value):
        if value:
            try:
                date = date_parse(value, dayfirst=True).date()
                return Q(end_date__gte=date)
            except:
                pass
        return None

    @staticmethod
    def filter_expiry_before(value):
        if value:
            try:
                date = date_parse(value, dayfirst=True).date()
                return Q(end_date__lte=date)
            except:
                pass
        return None

    @staticmethod
    def _search_licence_number(search):
        # testing to see if search term contains no spaces and two hyphens,
        #  meaning it's a lodgement number with a sequence
        if search and search.count(' ') == 0 and search.count('-') == 2:
            components = search.split('-')
            licence_number, licence_sequence = '-'.join(components[:2]), '-'.join(components[2:])

            return Q(licence_number__icontains=licence_number) & Q(licence_sequence__icontains=licence_sequence)
        else:
            return Q(licence_number__icontains=search)

    @staticmethod
    def _render_renewal_letter(instance):
        if instance.is_renewable:
            return '<a href="{0}" target="_blank">Create PDF</a><img height="20" src="{1}"></img>'. \
                format(reverse('wl_main:licence_renewal_pdf', args=(instance.pk,)), static('wl/img/pdf.png'))
        else:
            return 'Not renewable'

    @staticmethod
    def _render_status(instance):
        if not instance.is_issued:
            return 'Unissued'

        try:
            application = Application.objects.get(licence=instance)
            replacing_application = Application.objects.get(previous_application=application)

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
            return 'Unissued'

    @staticmethod
    def _render_action(instance):
        try:
            application = Application.objects.get(licence=instance)
            if Application.objects.filter(previous_application=application).exists():
                return 'N/A'
        except Application.DoesNotExist:
            application = None

        if not instance.is_issued:
            return '<a href="{0}">Issue</a>'.format(reverse('wl_applications:issue_licence', args=(application.pk,)))

        amend_url = reverse('wl_applications:amend_licence', args=(instance.pk,))
        renew_url = reverse('wl_applications:renew_licence', args=(instance.pk,))
        reissue_url = reverse('wl_applications:reissue_licence', args=(instance.pk,))

        if instance.end_date is not None:
            expiry_days = (instance.end_date - datetime.date.today()).days
            if instance.is_renewable:
                if 30 >= expiry_days > 0:
                    return '<a href="{0}">Amend</a> / <a href="{1}">Renew</a> / <a href="{2}">Reissue</a>'.\
                        format(amend_url, renew_url, reissue_url)
                elif expiry_days <= 30:
                    return '<a href="{0}">Renew</a>'.format(renew_url)
            if instance.end_date >= datetime.date.today():
                return '<a href="{0}">Amend</a> / <a href="{1}">Reissue</a>'.format(amend_url, reissue_url)
            else:
                return 'N/A'
        else:
            return '<a href="{0}">Issue</a>'.format(reverse('wl_applications:issue_licence', args=(application.pk,)))

    def get_initial_queryset(self):
        return WildlifeLicence.objects.all()


class TablesReturnsOfficerView(OfficerRequiredMixin, base.TablesBaseView):
    template_name = 'wl/dash_tables_returns_officer.html'

    STATUS_FILTER_ALL_BUT_DRAFT_OR_FUTURE = 'all_but_draft_or_future'
    OVERDUE_FILTER = 'overdue'

    returns_data_url_lazy = reverse_lazy('wl_dashboard:data_returns_officer')

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
                'title': 'User'
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
            'pageLength': 25,
            'order': [[0, 'asc']]
        }

    @property
    def returns_data_url(self):
        return str(self.returns_data_url_lazy)

    @property
    def returns_filters(self):
        status_filter_values = \
            [
                (self.STATUS_FILTER_ALL_BUT_DRAFT_OR_FUTURE, 'All (but draft or future)'),
                (self.OVERDUE_FILTER, self.OVERDUE_FILTER.capitalize())
            ] + list(Return.STATUS_CHOICES)
        return {
            'licence_type': self.get_licence_types_values(),
            'status': status_filter_values,
        }

    @property
    def get_returns_session_data(self):
        return DataTableReturnsOfficerView.get_session_data(self.request)


class DataTableReturnsOfficerView(OfficerRequiredMixin, base.DataTableBaseView):
    model = Return
    columns = [
        'lodgement_number',
        'licence.licence_type',
        'licence.profile.user',
        'lodgement_date',
        'due_date',
        'status',
        'licence_number',
        'action',
    ]
    order_columns = [
        'lodgement_number',
        'licence.licence_type',
        ['licence.profile.user.last_name', 'licence.profile.user.first_name'],
        'lodgement_date',
        'due_date',
        'status',
        '',
        '']
    columns_helpers = dict(base.DataTableBaseView.columns_helpers.items(), **{
        'licence.licence_type': {
            'render': lambda self, instance: instance.licence.licence_type.display_name,
            'search': lambda self, search: base.build_field_query(
                ['licence__licence_type__short_name', 'licence__licence_type__name', 'licence__licence_type__version'],
                search)
        },
        'lodgement_number': {
            'render': lambda self, instance: instance.lodgement_number
        },
        'lodgement_date': {
            'render': lambda self, instance: base.render_date(instance.lodgement_date)
        },
        'licence.profile.user': {
            'render': lambda self, instance: base.render_user_name(instance.licence.profile.user,
                                                                   first_name_first=False),
            'search': lambda self, search: base.build_field_query([
                'licence__profile__user__last_name', 'licence__profile__user__first_name'],
                search),
        },
        'due_date': {
            'render': lambda self, instance: base.render_date(instance.due_date)
        },
        'status': {
            'render': lambda self, instance: self._render_status(instance)
        },
        'licence_number': {
            'render': lambda self, instance: base.render_licence_number(instance.licence),
            'search': lambda self, search: DataTableReturnsOfficerView._search_licence_number(search),

        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        }
    })

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
    def _render_action(instance):
        if instance.status == 'current' or instance.status == 'future':
            url = reverse('wl_returns:enter_return', args=(instance.pk,))
            return '<a href="{0}">Enter Return</a>'.format(url)
        elif instance.status == 'draft':
            url = reverse('wl_returns:enter_return', args=(instance.pk,))
            return '<a href="{0}">Edit Return</a>'.format(url)
        elif instance.status in ['submitted', 'amended', 'amendment_required']:
            text = 'Curate Return'
            url = reverse('wl_returns:curate_return', args=(instance.pk,))
            return '<a href="{0}">{1}</a>'.format(url, text)
        else:
            url = reverse('wl_returns:view_return', args=(instance.pk,))
            return '<a href="{0}">View Return (read-only)</a>'.format(url)

    @staticmethod
    def filter_licence_type(value):
        if value.lower() != 'all':
            return Q(return_type__licence_type__pk=value)
        else:
            return None

    @staticmethod
    def filter_status(value):
        if value == TablesReturnsOfficerView.STATUS_FILTER_ALL_BUT_DRAFT_OR_FUTURE:
            return ~Q(status__in=['draft', 'future'])
        elif value == TablesReturnsOfficerView.OVERDUE_FILTER:
            return Q(due_date__lt=datetime.date.today()) & ~Q(
                status__in=['future', 'submitted', 'accepted', 'declined'])
        elif value == 'all':
            return None
        else:
            return Q(status=value)

    @staticmethod
    def _search_licence_number(search):
        # testing to see if search term contains no spaces and two hyphens,
        # meaning it's a licence number with a sequence
        if search and search.count(' ') == 0 and search.count('-') == 2:
            components = search.split('-')
            licence_number, licence_sequence = '-'.join(components[:2]), '-'.join(components[2:])

            return Q(licence__licence_number__icontains=licence_number) & Q(
                licence__licence_sequence__icontains=licence_sequence)
        else:
            return Q(licence__licence_number__icontains=search)

    def get_initial_queryset(self):
        return Return.objects.all()


class DataTableReturnsOfficerOnBehalfView(DataTableReturnsOfficerView):
    @staticmethod
    def _render_action(instance):
        # same actions as a customer
        return DataTableReturnsCustomerView._render_action(instance)

    @staticmethod
    def _get_proxy_returns(user):
        return Return.objects.filter(
            licence__in=WildlifeLicence.objects.filter(application__proxy_applicant=user))

    def get_initial_queryset(self):
        return self._get_proxy_returns(self.request.user)


class BulkLicenceRenewalPDFView(DataTableLicencesOfficerView):
    def filter_queryset(self, qs):
        qs = super(BulkLicenceRenewalPDFView, self).filter_queryset(qs)
        self.qs = qs
        return qs

    def get(self, request, *args, **kwargs):
        super(BulkLicenceRenewalPDFView, self).get(request, *args, **kwargs)
        licences = WildlifeLicence.objects.none()
        if self.qs:
            licences = self.qs
        response = HttpResponse(content_type='application/pdf')
        response.write(bulk_licence_renewal_pdf_bytes(licences, request.build_absolute_uri(reverse('home'))))
        if licences:
            licences.update(renewal_sent=True)
        return response
