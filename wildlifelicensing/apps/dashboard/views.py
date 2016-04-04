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

from braces.views import LoginRequiredMixin

from ledger.licence.models import LicenceType
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.helpers import is_officer
from .forms import LoginForm

logger = logging.getLogger(__name__)


def _build_url(base, query):
    return base + '?' + urllib.urlencode(query)


def _get_user_applications(user):
    return Application.objects.filter(applicant_persona__user=user)


# render date in dd/mm/yyyy format
def _render_date(date):
    if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
        return date.strftime("%d/%m/%Y")
    if not date:
        return ''
    return 'not a valid date object'


class DashBoardRoutingView(TemplateView):
    template_name = 'wl/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_officer(self.request.user):
                return redirect('dashboard:tree_officer')
            return redirect('dashboard:tree_customer')
        else:
            kwargs['form'] = LoginForm
            return super(DashBoardRoutingView, self).get(*args, **kwargs)


class DashboardTreeViewBase(TemplateView):
    template_name = 'wl/dash_tree.html'
    url = reverse_lazy('dashboard:tables_officer')

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
            +All applications
              - status
        """
        all_applications = Application.objects.all()
        all_applications_node = self._create_node('All applications', href=self.url,
                                                  count=len(all_applications))
        for s_value, s_title in Application.PROCESSING_STATUS_CHOICES:
            applications = all_applications.filter(processing_status=s_value)
            if applications.count() > 0:
                query = {
                    'model': 'application',
                    'status': s_value,
                }
                href = _build_url(self.url, query)
                node = self._create_node(s_title, href=href, count=applications.count())
                self._add_node(all_applications_node, node)

        return [all_applications_node]

    def get_context_data(self, **kwargs):
        if 'dataJSON' not in kwargs:
            kwargs['dataJSON'] = json.dumps(self._build_tree_nodes())
        if 'title' not in kwargs and hasattr(self, 'title'):
            kwargs['title'] = self.title
        return super(DashboardTreeViewBase, self).get_context_data(**kwargs)


class DashboardOfficerTreeView(OfficerRequiredMixin, DashboardTreeViewBase):
    template_name = 'wl/dash_tree.html'
    title = 'Quick glance dashboard'
    url = reverse_lazy('dashboard:tables_officer')


class DashboardCustomerTreeView(LoginRequiredMixin, DashboardTreeViewBase):
    template_name = 'wl/dash_tree.html'
    title = 'My Dashboard'
    url = reverse_lazy('dashboard:tables_customer')

    def _build_tree_nodes(self):
        """
            +My applications
              - status
        :return:
        """
        my_applications = _get_user_applications(self.request.user)
        my_applications_node = self._create_node('My applications', href=self.url, count=len(my_applications))
        # one children node per status
        for status in [s[0] for s in Application.CUSTOMER_STATUS_CHOICES]:
            applications = my_applications.filter(customer_status=status)
            if applications.count() > 0:
                query = {
                    'model': 'application',
                    'status': status,
                }
                href = _build_url(self.url, query)
                node = self._create_node(status, href=href, count=applications.count())
                self._add_node(my_applications_node, node)
        return [my_applications_node]


class DashboardTableBaseView(TemplateView):
    template_name = 'wl/dash_tables.html'

    def _build_data(self):
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
            }
        }
        return data

    def get_context_data(self, **kwargs):
        if 'dataJSON' not in kwargs:
            data = self._build_data()
            # add the request query to the data
            data['query'] = self.request.GET.dict()
            kwargs['dataJSON'] = json.dumps(data)
        return super(DashboardTableBaseView, self).get_context_data(**kwargs)


class DashboardTableOfficerView(DashboardTableBaseView):
    def _build_data(self):
        data = super(DashboardTableOfficerView, self)._build_data()
        data['applications']['columnDefinitions'] = [
            {
                'title': 'ID',
                'name': 'id'
            },
            {
                'title': 'Licence Type',
                'name': 'license_type',
            },
            {
                'title': 'User',
                'name': 'applicant_persona__user'
            },
            {
                'title': 'Status',
                'name': 'status'
            },
            {
                'title': 'Lodged on',
                'name': 'lodged_date'
            },
            {
                'title': 'Assignee',
                'name': 'assigned_officer'
            },
            {
                'title': 'Action',
                'name': 'action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['applications']['filters']['status']['values'] = \
            [('all', 'All')] + list(Application.PROCESSING_STATUS_CHOICES)
        data['applications']['ajax']['url'] = reverse('dashboard:applications_data_officer')
        return data


class DashboardTableCustomerView(DashboardTableBaseView):
    def _build_data(self):
        data = super(DashboardTableCustomerView, self)._build_data()
        data['applications']['columnDefinitions'] = [
            {
                'title': 'Licence Type',
                'name': 'license_type',
            },
            {
                'title': 'Persona',
                'name': 'applicant_persona'
            },
            {
                'title': 'Status',
                'name': 'status'
            },
            {
                'title': 'Action',
                'name': 'action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['applications']['filters']['status']['values'] = \
            [('all', 'All')] + list(Application.CUSTOMER_STATUS_CHOICES)
        data['applications']['ajax']['url'] = reverse('dashboard:applications_data_customer')
        return data


class ApplicationDataTableBaseView(LoginRequiredMixin, BaseDatatableView):
    model = Application
    columns = ['licence_type.code', 'applicant_persona.user', 'applicant_persona', 'processing_status']
    order_columns = ['licence_type.code', 'applicant_persona.user', 'applicant_persona', 'processing_status']

    def _build_search_query(self, fields_to_search, search):
        query = Q()
        for field in fields_to_search:
            query |= Q(**{"{0}__icontains".format(field): search})
        return query

    def _build_user_search_query(self, search):
        fields_to_search = ['applicant_persona__user__last_name', 'applicant_persona__user__first_name',
                            'applicant_persona__user__email']
        return self._build_search_query(fields_to_search, search)

    def _build_persona_search_query(self, search):
        fields_to_search = ['applicant_persona__email', 'applicant_persona__name']
        return self._build_search_query(fields_to_search, search)

    def _render_user_column(self, obj):
        user = obj.applicant_persona.user
        if user.last_name:
            return '{last}, {first}, {email}'.format(
                last=user.last_name,
                first=user.first_name,
                email=user.email
            )
        else:
            return '{email}'.format(
                email=user.email
            )

    def _render_persona_column(self, obj):
        persona = obj.applicant_persona
        if persona is None:
            return 'unknown'
        else:
            # return the string rep
            return '{}'.format(persona)

    columns_helpers = {
        'applicant_persona.user': {
            'render': _render_user_column,
            'search': _build_user_search_query
        },
        'applicant_persona': {
            'render': _render_persona_column,
            'search': _build_persona_search_query
        }
    }

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

    def get_initial_queryset(self):
        return self.model.objects.all()

    def _build_status_filter(self, status_value):
        return Q(processing_status=status_value)

    def filter_queryset(self, qs):
        query = Q()
        # part 1: filter from top level filters
        filters = self._parse_filters()
        for filter_name, filter_value in filters.items():
            # if the value is 'all' no filter to apply
            if filter_value != 'all':
                if filter_name == 'status':
                    query &= self._build_status_filter(filter_value)
        # part 2: filter from the global search
        search = self.request.GET.get('search[value]', None)
        if search:
            query &= self._build_global_search_query(search)
        return qs.filter(query)

    def render_column(self, application, column):
        if column in self.columns_helpers and 'render' in self.columns_helpers[column]:
            func = self.columns_helpers[column]['render']
            return func(self, application)
        else:
            result = super(ApplicationDataTableBaseView, self).render_column(application, column)
        return result

    def _build_global_search_query(self, search):
        query = Q()
        col_data = super(ApplicationDataTableBaseView, self).extract_datatables_column_data()
        for col_no, col in enumerate(col_data):
            if col['searchable']:
                col_name = self.columns[col_no]
                # special cases
                if col_name in self.columns_helpers and 'search' in self.columns_helpers[col_name]:
                    func = self.columns_helpers[col_name]['search']
                    q = func(self, search)
                    query |= q
                else:
                    query |= Q(**{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): search})
        return query


class ApplicationDataTableOfficerView(OfficerRequiredMixin, ApplicationDataTableBaseView):
    columns = ['id', 'licence_type.code', 'applicant_persona.user', 'processing_status', 'lodged_date',
               'assigned_officer', 'action']
    order_columns = ['id', 'licence_type.code', 'applicant_persona.user', 'processing_status', 'lodged_date',
                     'assigned_officer', '']

    def _render_action_column(self, obj):
        return '<a href="{0}">Process</a>'.format(
            reverse('applications:process', args={obj.pk}),
        )

    def _build_assignee_search_query(self, search):
        fields_to_search = ['assigned_officer__user__last_name', 'assigned_officer__user__first_name',
                            'assigned_officer__user__email']
        return self._build_search_query(fields_to_search, search)

    def _render_assignee_column(self, obj):
        user = obj.assigned_officer
        if user is None:
            return ''
        else:
            return '{email}'.format(
                email=user.email
            )

    def _render_lodged_date(selfself, obj):
        return _render_date(obj.lodged_date)

    columns_helpers = dict(ApplicationDataTableBaseView.columns_helpers.items(), **{
        'assigned_officer': {
            'search': _build_assignee_search_query,
            'render': _render_assignee_column
        },
        'action': {
            'render': _render_action_column,
        },
        'lodged_date': {
            'render': _render_lodged_date
        },
    })

    def get_initial_queryset(self):
        return self.model.objects.all()


class ApplicationDataTableCustomerView(ApplicationDataTableBaseView):
    columns = ['licence_type.code', 'applicant_persona', 'customer_status', 'action']
    order_columns = ['licence_type.code', 'applicant_persona', 'customer_status', '']

    def get_initial_queryset(self):
        return _get_user_applications(self.request.user)

    def _build_status_filter(self, status_value):
        return Q(customer_status=status_value)

    def _render_action_column(self, obj):
        if obj.customer_status == 'draft':
            return '<a href="{0}">{1}</a>'.format(
                reverse('applications:enter_details', args={obj.licence_type.code, obj.pk}),
                'Continue application'
            )
        else:
            return 'Locked'

    columns_helpers = dict(ApplicationDataTableBaseView.columns_helpers.items(), **{
        'action': {
            'render': _render_action_column,
        },
    })
