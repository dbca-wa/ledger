from __future__ import unicode_literals
import json
import urllib
import logging
import datetime

from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.db.models.query import EmptyQuerySet
from django.contrib.staticfiles.templatetags.staticfiles import static

from django.contrib.auth.mixins import LoginRequiredMixin

from ledger.licence.models import LicenceType
from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.applications.models import Application, Assessment
from wildlifelicensing.apps.returns.models import Return
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrAssessorRequiredMixin, \
    AssessorRequiredMixin
from wildlifelicensing.apps.main.helpers import is_officer, is_assessor, get_all_officers, render_user_name
from wildlifelicensing.apps.dashboard.forms import LoginForm

logger = logging.getLogger(__name__)


def _build_url(base, query):
    return base + '?' + urllib.urlencode(query)


def _get_user_applications(user):
    return Application.objects.filter(applicant_profile__user=user)


def _get_current_onbehalf_applications(officer):
    return Application.objects.filter(proxy_applicant=officer)


def _get_processing_statuses_but_draft():
    return [s for s in Application.PROCESSING_STATUS_CHOICES if s[0] != 'draft']


# render date in dd/mm/yyyy format
def _render_date(date):
    if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
        return date.strftime("%d/%m/%Y")
    if not date:
        return ''
    return 'not a valid date object'


def _render_lodgement_number(application):
    if application is not None and application.lodgement_number and application.lodgement_sequence:
        return '%s-%d' % (application.lodgement_number, application.lodgement_sequence)
    else:
        return ''


def _render_licence_number(licence):
    if licence is not None and licence.licence_number and licence.licence_sequence:
        return '%s-%d' % (licence.licence_number, licence.licence_sequence)
    else:
        return ''


def _render_return_number(instance):
    if instance is not None and instance.lodgement_number and instance.lodgement_sequence:
        return '%s-%d' % (instance.lodgement_number, instance.lodgement_sequence)
    else:
        return ''


def _render_licence_document(licence):
    if licence is not None and licence.document is not None:
        return '<a href="{0}" target="_blank">View PDF</a><img height="20" src="{1}"></img>'.format(
            licence.document.file.url,
            static('wl/img/pdf.png')
        )
    else:
        return ''


class DashBoardRoutingView(TemplateView):
    template_name = 'wl/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_officer(self.request.user):
                return redirect('dashboard:tree_officer')
            elif is_assessor(self.request.user):
                return redirect('dashboard:tables_assessor')

            return redirect('dashboard:tables_customer')
        else:
            kwargs['form'] = LoginForm
            return super(DashBoardRoutingView, self).get(*args, **kwargs)


class DashboardTreeViewBase(TemplateView):
    template_name = 'wl/dash_tree.html'
    url = reverse_lazy('dashboard:tables_applications_officer')

    @staticmethod
    def _create_node(title, href=None, count=None):
        node_template = {
            'text': 'Title',
            'href': '#',
            'tags': [],
            'nodes': None,
            'state': {
                'expanded': True
            }
        }
        result = {}
        result.update(node_template)
        result['text'] = str(title)
        if href is not None:
            result['href'] = str(href)
        if count is not None:
            result['tags'].append(str(count))

        return result

    @staticmethod
    def _add_node(parent, child):
        if 'nodes' not in parent or type(parent['nodes']) != list:
            parent['nodes'] = [child]
        else:
            parent['nodes'].append(child)
        return parent

    def _build_tree_nodes(self):
        """
        Subclass should implement the nodes with the help of _create_node and _build_node
        """
        parent_node = self._create_node('Parent node', href='#', count=2)
        child1 = self._create_node('Child#1', href='#', count=1)
        self._add_node(parent_node, child1)
        child2 = self._create_node('Child#2', href='#', count=1)
        self._add_node(parent_node, child2)
        return [parent_node]

    def get_context_data(self, **kwargs):
        if 'dataJSON' not in kwargs:
            kwargs['dataJSON'] = json.dumps(self._build_tree_nodes())
        if 'title' not in kwargs and hasattr(self, 'title'):
            kwargs['title'] = self.title
        return super(DashboardTreeViewBase, self).get_context_data(**kwargs)


class TableBaseView(TemplateView):
    template_name = 'wl/dash_tables.html'

    def _build_data(self):
        """
        Build data skeleton for all the tables definitions, filters....
        :return:
        """
        licence_types = [('all', 'All')] + [(lt.pk, lt.code) for lt in LicenceType.objects.all()]
        data = {
            'applications': {
                'columnDefinitions': [],
                'filters': {
                    'licenceType': {
                        'values': licence_types,
                    },
                    'status': {
                        'values': [],
                    }
                },
                'ajax': {
                    'url': ''
                }
            },
            'licences': {
                'columnDefinitions': [],
                'filters': {
                    'licenceType': {
                        'values': licence_types,
                    },
                },
                'ajax': {
                    'url': ''
                }
            },
            'returns': {
                'columnDefinitions': [],
                'filters': {
                    'licenceType': {
                        'values': licence_types,
                    },
                },
                'ajax': {
                    'url': ''
                }
            }
        }
        return data

    def get_context_data(self, **kwargs):
        if 'dataJSON' not in kwargs:
            data = self._build_data()
            # add the request query to the data
            data['query'] = self.request.GET.dict()
            kwargs['dataJSON'] = json.dumps(data)
        return super(TableBaseView, self).get_context_data(**kwargs)


def _build_field_query(fields_to_search, search):
    """
    Build a OR __icontains query
    :param fields_to_search:
    :param search:
    :return:
    """
    query = Q()
    for field in fields_to_search:
        query |= Q(**{"{0}__icontains".format(field): search})
    return query


class DataTableBaseView(LoginRequiredMixin, BaseDatatableView):
    """
    View to handle datatable server-side processing
    It is extension of the BaseDatatableView at
     https://bitbucket.org/pigletto/django-datatables-view
    It just provides a configurable way to define render and search functions for each defined columns through the
    column_helpers = {
       'column': {
            'search': callable(search_term)
            'render': callable(model_instance)
       }
    }

    """
    model = None
    columns_helpers = {
    }

    def _build_global_search_query(self, search):
        query = Q()
        col_data = super(DataTableBaseView, self).extract_datatables_column_data()
        for col_no, col in enumerate(col_data):
            if col['searchable']:
                col_name = self.columns[col_no]
                # special cases
                if col_name in self.columns_helpers and 'search' in self.columns_helpers[col_name]:
                    func = self.columns_helpers[col_name]['search']
                    if callable(func):
                        q = func(self, search)
                        query |= q
                else:
                    query |= Q(**{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): search})
        return query

    def _parse_filters(self):
        """
        The additional filters are sent in the query param with the following form (example):
        'filters[0][name]': '['licence_type']'
        'filters[0][value]: ['all']'
        'filters[1][name]': '['status']'
        'filters[1][value]: ['draft']'
        .....
        :return: a dict {
            'licence_type': 'all',
            'status': 'draft',
            ....
        }
        """
        result = {}
        querydict = self._querydict
        counter = 0
        filter_key = 'filters[{0}][name]'.format(counter)
        while filter_key in querydict:
            result[querydict.get(filter_key)] = querydict.get('filters[{0}][value]'.format(counter))
            counter += 1
            filter_key = 'filters[{0}][name]'.format(counter)
        return result

    def filter_queryset(self, qs):
        """
        Two level of filtering:
        1- The filters included in the query (see _parse_filter)
        2- The data table search filter
        :param qs:
        :return:
        """
        query = Q()
        # part 1: filter from top level filters
        filters = self._parse_filters()
        for filter_name, filter_value in filters.items():
            # look for a filter_<filter_name> method and call it with the filter value
            # the method must return a Q instance, if it returns None or anything else it will be ignored
            filter_method = getattr(self, 'filter_' + filter_name.lower(), None)
            if callable(filter_method):
                q_filter = filter_method(filter_value)
                if isinstance(q_filter, Q):
                    query &= q_filter

        search = self.request.GET.get('search[value]', None)
        if search:
            query &= self._build_global_search_query(search)
        return qs.filter(query)

    def render_column(self, instance, column):
        if column in self.columns_helpers and 'render' in self.columns_helpers[column]:
            func = self.columns_helpers[column]['render']
            if callable(func):
                return func(self, instance)
            else:
                return 'render is not a function'
        else:
            result = super(DataTableBaseView, self).render_column(instance, column)
        return result

    def get_initial_queryset(self):
        if self.model:
            return self.model.objects.all()
        else:
            return EmptyQuerySet()


class DataTableApplicationBaseView(DataTableBaseView):
    model = Application
    columns = ['licence_type.code', 'applicant_profile.user', 'applicant_profile', 'processing_status']
    order_columns = ['licence_type.code', 'applicant_profile.user', 'applicant_profile', 'processing_status']

    columns_helpers = {
        'applicant_profile.user': {
            'render': lambda self, instance: render_user_name(instance.applicant_profile.user, first_name_first=False),
            'search': lambda self, search: _build_field_query(
                ['applicant_profile__user__last_name', 'applicant_profile__user__first_name'], search)
        },
        'applicant_profile': {
            'render': lambda self, instance: '{}'.format(instance.applicant_profile),
            'search': lambda self, search: _build_field_query(
                ['applicant_profile__email', 'applicant_profile__name'], search)
        }
    }

    @staticmethod
    def filter_status(value):
        return Q(processing_status=value) if value.lower() != 'all' else None

    @staticmethod
    def filter_assignee(value):
        return Q(assigned_officer__pk=value) if value.lower() != 'all' else None

    @staticmethod
    def filter_licence_type(value):
        return Q(licence_type__pk=value) if value.lower() != 'all' else None


########################
#    Officers
########################

class DashboardOfficerTreeView(OfficerRequiredMixin, DashboardTreeViewBase):
    template_name = 'wl/dash_tree.html'
    title = 'Officer Dashboard'
    url = reverse_lazy('dashboard:tables_applications_officer')

    def _build_tree_nodes(self):
        """
            +Applications assigned to me
              - status
            +All applications
              - status
        """
        # The draft status is excluded from the officer status list
        result = []
        statuses = _get_processing_statuses_but_draft()
        all_applications = Application.objects.filter(processing_status__in=[s[0] for s in statuses])
        all_applications_node = self._create_node('All applications', href=self.url,
                                                  count=all_applications.count())
        all_applications_node['state']['expanded'] = False
        for s_value, s_title in statuses:
            applications = all_applications.filter(processing_status=s_value)
            if applications.count() > 0:
                query = {
                    'application_status': s_value,
                }
                href = _build_url(self.url, query)
                node = self._create_node(s_title, href=href, count=applications.count())
                self._add_node(all_applications_node, node)

        assigned_applications = all_applications.filter(assigned_officer=self.request.user)
        query = {
            'application_assignee': self.request.user.pk
        }
        assigned_applications_node = self._create_node('My assigned applications', href=_build_url(self.url, query),
                                                       count=assigned_applications.count())
        assigned_applications_node['state']['expanded'] = True
        for s_value, s_title in statuses:
            applications = assigned_applications.filter(processing_status=s_value)
            if applications.count() > 0:
                query.update({
                    'application_status': s_value
                })
                href = _build_url(self.url, query)
                node = self._create_node(s_title, href=href, count=applications.count())
                self._add_node(assigned_applications_node, node)
        result.append(assigned_applications_node)

        on_behalf_applications = _get_current_onbehalf_applications(self.request.user)
        if on_behalf_applications.count() > 0:
            url = reverse_lazy('dashboard:tables_applications_officer_onbehalf')
            on_behalf_applications_node = self._create_node('My current proxied applications', href=url,
                                                            count=on_behalf_applications.count())
            result.append(on_behalf_applications_node)

        result.append(all_applications_node)

        # Licences
        url = reverse_lazy('dashboard:tables_licences_officer')
        all_licences_node = self._create_node('All licences', href=url, count=WildlifeLicence.objects.count())
        result.append(all_licences_node)

        # Returns
        url = reverse_lazy('dashboard:tables_returns_officer')
        all_returns_node = self._create_node('All returns', href=url, count=WildlifeLicence.objects.count())
        result.append(all_returns_node)

        return result


class TableApplicationsOfficerView(OfficerRequiredMixin, TableBaseView):
    template_name = 'wl/dash_tables_applications_officer.html'

    STATUS_PENDING = 'pending'

    def _build_data(self):
        data = super(TableApplicationsOfficerView, self)._build_data()
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
                'title': 'Status',
            },
            {
                'title': 'Lodged on'
            },
            {
                'title': 'Assignee'
            },
            {
                'title': 'Proxy'
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['applications']['filters']['status']['values'] = \
            [('all', 'All')] + [(self.STATUS_PENDING, self.STATUS_PENDING.capitalize())] + \
            _get_processing_statuses_but_draft()
        data['applications']['filters']['assignee'] = {
            'values': [('all', 'All')] + [(user.pk, render_user_name(user),) for user in get_all_officers()]
        }
        data['applications']['ajax']['url'] = reverse('dashboard:data_application_officer')
        # global table options
        data['applications']['tableOptions'] = {
            'pageLength': 25
        }
        return data


class DataTableApplicationsOfficerView(OfficerRequiredMixin, DataTableApplicationBaseView):
    columns = ['lodgement_number', 'licence_type.code', 'applicant_profile.user', 'processing_status', 'lodgement_date',
               'assigned_officer', 'proxy_applicant', 'action']
    order_columns = ['lodgement_number', 'licence_type.code',
                     ['applicant_profile.user.last_name', 'applicant_profile.user.first_name',
                      'applicant_profile.user.email'],
                     'processing_status', 'lodgement_date',
                     ['assigned_officer.first_name', 'assigned_officer.last_name', 'assigned_officer.email'],
                     ['proxy_applicant.first_name', 'proxy_applicant.last_name', 'proxy_applicant.email'],
                     '']

    columns_helpers = dict(DataTableApplicationBaseView.columns_helpers.items(), **{
        'lodgement_number': {
            'render': lambda self, instance: _render_lodgement_number(instance)
        },
        'assigned_officer': {
            'search': lambda self, search: _build_field_query(
                ['assigned_officer__last_name', 'assigned_officer__first_name'],
                search
            ),
            'render': lambda self, instance: render_user_name(instance.assigned_officer)
        },
        'proxy_applicant': {
            'search': lambda self, search: _build_field_query([
                'proxy_applicant__last_name', 'proxy_applicant__first_name'],
                search),
            'render': lambda self, obj: render_user_name(obj.proxy_applicant)
        },
        'action': {
            'render': lambda self, instance: DataTableApplicationsOfficerView._render_action_column(instance),
        },
        'lodgement_date': {
            'render': lambda self, instance: _render_date(instance.lodgement_date)
        },
    })

    @staticmethod
    def _get_pending_processing_statuses():
        return [s[0] for s in Application.PROCESSING_STATUS_CHOICES
                if s[0] != 'draft' and s[0] != 'issued' and s[0] != 'declined']

    @staticmethod
    def filter_status(value):
        # officers should not see applications in draft mode.
        if value.lower() == TableApplicationsOfficerView.STATUS_PENDING:
            return Q(processing_status__in=DataTableApplicationsOfficerView._get_pending_processing_statuses())
        return Q(processing_status=value) if value != 'all' else ~Q(customer_status='draft')

    @staticmethod
    def _render_action_column(obj):
        if obj.processing_status == 'ready_for_conditions':
            return '<a href="{0}">Enter Conditions</a>'.format(
                reverse('applications:enter_conditions', args=[obj.pk]),
            )
        if obj.processing_status == 'ready_to_issue':
            return '<a href="{0}">Issue Licence</a>'.format(
                reverse('applications:issue_licence', args=[obj.pk]),
            )
        elif obj.processing_status == 'issued' and obj.licence is not None and obj.licence.document is not None:
            return '<a href="{0}" target="_blank">View licence</a>'.format(
                obj.licence.document.file.url
            )
        else:
            return '<a href="{0}">Process</a>'.format(
                reverse('applications:process', args=[obj.pk]),
            )


class TableApplicationsOfficerOnBehalfView(OfficerRequiredMixin, TableBaseView):
    template_name = 'wl/dash_tables_applications_officer_onbehalf.html'

    def _build_data(self):
        data = super(TableApplicationsOfficerOnBehalfView, self)._build_data()
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
        data['applications']['ajax']['url'] = reverse('dashboard:data_application_officer_onbehalf')

        return data


class DataTableApplicationsOfficerOnBehalfView(OfficerRequiredMixin, DataTableApplicationBaseView):
    columns = ['lodgement_number', 'licence_type.code', 'applicant_profile.user', 'processing_status', 'lodgement_date',
               'action']
    order_columns = ['lodgement_number', 'licence_type.code',
                     ['applicant_profile.user.last_name', 'applicant_profile.user.first_name',
                      'applicant_profile.user.email'],
                     'processing_status', 'lodgement_date',
                     '']

    columns_helpers = dict(DataTableApplicationBaseView.columns_helpers.items(), **{
        'lodgement_number': {
            'render': lambda self, instance: _render_lodgement_number(instance)
        },
        'lodgement_date': {
            'render': lambda self, instance: _render_date(instance.lodgement_date)
        },
        'action': {
            'render': lambda self, action: self._render_action_column,
        },
    })

    @staticmethod
    def _render_action_column(obj):
        status = obj.customer_status
        if status == 'draft':
            return '<a href="{0}">{1}</a>'.format(
                reverse('applications:edit_application', args=[obj.licence_type.code, obj.pk]),
                'Continue application'
            )
        elif status == 'amendment_required' or status == 'id_and_amendment_required':
            return '<a href="{0}">{1}</a>'.format(
                reverse('applications:edit_application', args=[obj.licence_type.code, obj.pk]),
                'Amend application'
            )
        elif status == 'id_required' and obj.id_check_status == 'awaiting_update':
            return '<a href="{0}">{1}</a>'.format(
                reverse('main:identification'),
                'Update ID')
        elif obj.processing_status == 'issued' and obj.licence is not None and obj.licence.document is not None:
            return '<a href="{0}" target="_blank">View licence</a>'.format(
                obj.licence.document.file.url
            )
        else:
            return 'Locked'

    def get_initial_queryset(self):
        return _get_current_onbehalf_applications(self.request.user)


class TableLicencesOfficerView(OfficerRequiredMixin, TableBaseView):
    template_name = 'wl/dash_tables_licences_officer.html'

    DATE_FILTER_ACTIVE = 'active'
    DATE_FILTER_RENEWABLE = 'renewable'
    DATE_FILTER_EXPIRED = 'expired'
    DATE_FILTER_ALL = 'all'

    def _build_data(self):
        data = super(TableLicencesOfficerView, self)._build_data()
        del data['applications']
        del data['returns']
        data['licences']['columnDefinitions'] = [
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
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['licences']['ajax']['url'] = reverse('dashboard:data_licences_officer')
        # filters (note: there is already the licenceType from the super class)
        filters = {
            'date': {
                'values': [
                    (self.DATE_FILTER_ACTIVE, self.DATE_FILTER_ACTIVE.capitalize()),
                    (self.DATE_FILTER_RENEWABLE, self.DATE_FILTER_RENEWABLE.capitalize()),
                    (self.DATE_FILTER_EXPIRED, self.DATE_FILTER_EXPIRED.capitalize()),
                    (self.DATE_FILTER_ALL, self.DATE_FILTER_ALL.capitalize()),
                ]
            }
        }
        data['licences']['filters'].update(filters)
        # global table options
        data['licences']['tableOptions'] = {
            'pageLength': 25
        }
        return data


class DataTableLicencesOfficerView(OfficerRequiredMixin, DataTableBaseView):
    model = WildlifeLicence
    columns = [
        'licence_number',
        'licence_type.code',
        'profile.user',
        'start_date',
        'end_date',
        'licence',
        'action']
    order_columns = [
        'licence_number',
        'licence_type.code',
        ['profile.user.last_name', 'profile.user.first_name'],
        'start_date',
        'end_date',
        '',
        '']

    columns_helpers = {
        'licence_number': {
            'render': lambda self, instance: _render_licence_number(instance)
        },
        'profile.user': {
            'render': lambda self, instance: render_user_name(instance.profile.user, first_name_first=False),
            'search': lambda self, search: _build_field_query([
                'profile__user__last_name', 'profile__user__first_name'],
                search),
        },
        'issue_date': {
            'render': lambda self, instance: _render_date(instance.issue_date)
        },
        'start_date': {
            'render': lambda self, instance: _render_date(instance.start_date)
        },
        'end_date': {
            'render': lambda self, instance: _render_date(instance.end_date)
        },
        'licence': {
            'render': lambda self, instance: _render_licence_document(instance)
        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        }
    }

    @staticmethod
    def filter_date(value):
        today = datetime.date.today()
        if value == TableLicencesOfficerView.DATE_FILTER_ACTIVE:
            return Q(start_date__lte=today) & Q(end_date__gte=today)
        elif value == TableLicencesOfficerView.DATE_FILTER_RENEWABLE:
            return Q(is_renewable=True) & Q(end_date__gte=today) & Q(end_date__lte=today + datetime.timedelta(days=30))
        elif value == TableLicencesOfficerView.DATE_FILTER_EXPIRED:
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
    def _render_action(instance):
        url = reverse('applications:reissue_licence', args=(instance.pk,))
        return '<a href="{0}">Reissue</a>'.format(url)

    def get_initial_queryset(self):
        return WildlifeLicence.objects.all()


class TableReturnsOfficerView(OfficerRequiredMixin, TableBaseView):
    template_name = 'wl/dash_tables_returns_officer.html'

    STATUS_FILTER_ALL_BUT_DRAFT = 'all_but_draft'
    OVERDUE_FILTER = 'overdue'

    def _build_data(self):
        data = super(TableReturnsOfficerView, self)._build_data()
        del data['applications']
        del data['returns']
        data['returns']['columnDefinitions'] = [
            {
                'title': 'Return Number'
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
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['returns']['ajax']['url'] = reverse('dashboard:data_returns_officer')
        # global table options
        data['returns']['tableOptions'] = {
            'pageLength': 25
        }
        filters = {
            'status': {
                'values': [
                              (self.STATUS_FILTER_ALL_BUT_DRAFT, 'All (but draft)'),
                              (self.OVERDUE_FILTER, self.OVERDUE_FILTER.capitalize())
                          ] + list(Return.STATUS_CHOICES)
            }
        }
        data['returns']['filters'].update(filters)

        return data


class DataTableReturnsOfficerView(DataTableBaseView):
    model = Return
    columns = [
        'lodgement_number',
        'licence.licence_type.code',
        'licence.profile.user',
        'lodgement_date',
        'due_date',
        'status',
        'licence',
        'action',
    ]
    order_columns = [
        'lodgement_number',
        'licence.licence_type.code',
        ['licence.profile.user.last_name', 'licence.profile.user.first_name'],
        'lodgement_date',
        'due_date',
        'status',
        '',
        '']
    columns_helpers = {
        'lodgement_number': {
            'render': lambda self, instance: _render_return_number(instance)
        },
        'lodgement_date': {
            'render': lambda self, instance: _render_date(instance.lodgement_date)
        },
        'licence.profile.user': {
            'render': lambda self, instance: render_user_name(instance.licence.profile.user, first_name_first=False),
            'search': lambda self, search: _build_field_query([
                'licence__profile__user__last_name', 'licence__profile__user__first_name'],
                search),
        },
        'due_date': {
            'render': lambda self, instance: _render_date(instance.due_date)
        },
        'licence': {
            'render': lambda self, instance: _render_licence_document(instance.licence)
        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        }
    }

    @staticmethod
    def _render_action(instance):
        return 'View'

    @staticmethod
    def filter_licence_type(value):
        if value.lower() != 'all':
            return Q(return_type__licence_type__pk=value)
        else:
            return None

    @staticmethod
    def filter_status(value):
        if value == TableReturnsOfficerView.STATUS_FILTER_ALL_BUT_DRAFT:
            return ~Q(status='draft')
        elif value == TableReturnsOfficerView.OVERDUE_FILTER:
            return Q(due_date__lt=datetime.date.today()) & ~Q(status__in=['submitted', 'accepted', 'declined'])
        elif value:
            return Q(status=value)
        else:
            return None

    def get_initial_queryset(self):
        return Return.objects.all()


########################
#    Assessors
########################

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


class DataTableApplicationAssessorView(OfficerOrAssessorRequiredMixin, DataTableBaseView):
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
            'render': lambda self, instance: _render_lodgement_number(instance.application)
        },
        'application.applicant_profile.user': {
            'render': lambda self, instance: render_user_name(instance.application.applicant_profile.user),
            'search': lambda self, search: _build_field_query(
                ['application__applicant_profile__user__last_name', 'application__applicant_profile__user__first_name'],
                search
            ),
        },
        'application.assigned_officer': {
            'render': lambda self, instance: render_user_name(instance.application.assigned_officer),
            'search': lambda self, search: _build_field_query(
                ['application__assigned_officer__last_name', 'application__assigned_officer__first_name',
                 'application__assigned_officer__email'],
                search
            ),
        },
        'action': {
            'render': lambda self, instance: DataTableApplicationAssessorView.render_action_column(instance),
        },
        'application.lodgement_date': {
            'render': lambda self, instance: _render_date(instance.application.lodgement_date),
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


########################
#    Customers
########################


class TableCustomerView(LoginRequiredMixin, TableBaseView):
    """
    This view includes the table definitions and fiters for applications, licences and returns for the customers as it's
    display on the same page.
    """
    template_name = 'wl/dash_tables_customer.html'

    def _build_data(self):
        data = super(TableCustomerView, self)._build_data()
        # Applications
        data['applications']['columnDefinitions'] = [
            {
                'title': 'Lodge Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'Profile'
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
        # no filters
        if 'filters' in data['applications']:
            del data['applications']['filters']
        data['applications']['ajax']['url'] = reverse('dashboard:data_application_customer')

        # Licences
        data['licences']['columnDefinitions'] = [
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
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['licences']['ajax']['url'] = reverse('dashboard:data_licences_customer')
        # no filters
        if 'filters' in data['licences']:
            del data['licences']['filters']
        # global table options
        data['licences']['tableOptions'] = {
            'order': [[4, 'desc']]
        }

        # Returns
        data['returns']['columnDefinitions'] = [
            {
                'title': 'Return Number'
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
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['returns']['ajax']['url'] = reverse('dashboard:data_returns_customer')
        # no filters
        if 'filters' in data['returns']:
            del data['returns']['filters']
        # global table options
        data['returns']['tableOptions'] = {
            'order': [[3, 'desc']]
        }

        return data


class DataTableApplicationCustomerView(DataTableApplicationBaseView):
    columns = ['lodgement_number', 'licence_type.code', 'applicant_profile', 'customer_status', 'lodgement_date',
               'action']
    order_columns = ['lodgement_number', 'licence_type.code', 'applicant_profile', 'customer_status', 'lodgement_date',
                     '']

    columns_helpers = dict(DataTableApplicationBaseView.columns_helpers.items(), **{
        'lodgement_number': {
            'render': lambda self, instance: _render_lodgement_number(instance)
        },
        'action': {
            'render': lambda self, instance: DataTableApplicationCustomerView.render_action_column(instance),
        },
        'lodgement_date': {
            'render': lambda self, instance: _render_date(instance.lodgement_date)
        },
    })

    @staticmethod
    def render_action_column(obj):
        status = obj.customer_status
        if status == 'draft':
            return '<a href="{0}">{1}</a>'.format(
                reverse('applications:edit_application', args=[obj.licence_type.code, obj.pk]),
                'Continue application'
            )
        elif status == 'amendment_required' or status == 'id_and_amendment_required':
            return '<a href="{0}">{1}</a>'.format(
                reverse('applications:edit_application', args=[obj.licence_type.code, obj.pk]),
                'Amend application'
            )
        elif status == 'id_required' and obj.id_check_status == 'awaiting_update':
            return '<a href="{0}">{1}</a>'.format(
                reverse('main:identification'),
                'Update ID')
        elif obj.processing_status == 'issued' and obj.licence is not None and obj.licence.document is not None:
            return '<a href="{0}" target="_blank">View licence</a>'.format(
                obj.licence.document.file.url
            )
        else:
            return 'Locked'

    def get_initial_queryset(self):
        return _get_user_applications(self.request.user)


class DataTableLicencesCustomerView(DataTableBaseView):
    model = WildlifeLicence
    columns = ['licence_number', 'licence_type.code', 'issue_date', 'start_date', 'end_date', 'licence', 'action']
    order_columns = ['licence_number', 'licence_type.code', 'issue_date', 'start_date', 'end_date', '', '']

    columns_helpers = {
        'licence_number': {
            'render': lambda self, instance: _render_licence_number(instance)
        },
        'issue_date': {
            'render': lambda self, instance: _render_date(instance.issue_date)
        },
        'start_date': {
            'render': lambda self, instance: _render_date(instance.start_date)
        },
        'end_date': {
            'render': lambda self, instance: _render_date(instance.end_date)
        },
        'licence': {
            'render': lambda self, instance: _render_licence_document(instance)
        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        }
    }

    @staticmethod
    def _render_action(instance):
        if not instance.is_renewable:
            return 'Not renewable'
        else:
            try:
                application = Application.objects.get(licence=instance)
                if Application.objects.filter(previous_application=application).exists():
                    return 'Renewed'
            except Application.DoesNotExist:
                pass
            expiry_days = (instance.end_date - datetime.date.today()).days
            if expiry_days <= 30:
                url = reverse('applications:renew_licence', args=(instance.pk,))
                return '<a href="{0}">Renew</a>'.format(url)
            else:
                return 'Renewable in ' + str(expiry_days - 30) + ' days'

    def get_initial_queryset(self):
        return WildlifeLicence.objects.filter(user=self.request.user)


class DataTableReturnsCustomerView(DataTableBaseView):
    model = Return
    columns = ['lodgement_number', 'licence.licence_type.code', 'lodgement_date', 'due_date', 'status', 'licence',
               'action']
    order_columns = ['lodgement_number', 'licence.licence_type.code', 'lodgement_date', 'due_date', 'status', '', '']
    columns_helpers = {
        'lodgement_number': {
            'render': lambda self, instance: _render_return_number(instance)
        },
        'lodgement_date': {
            'render': lambda self, instance: _render_date(instance.lodgement_date)
        },
        'due_date': {
            'render': lambda self, instance: _render_date(instance.due_date)
        },
        'licence': {
            'render': lambda self, instance: _render_licence_document(instance.licence)
        },
        'action': {
            'render': lambda self, instance: self._render_action(instance)
        }
    }

    @staticmethod
    def _render_action(instance):
        return 'View'

    def get_initial_queryset(self):
        return Return.objects.filter(licence__user=self.request.user)
