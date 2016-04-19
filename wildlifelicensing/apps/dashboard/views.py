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

from django.contrib.auth.mixins import LoginRequiredMixin

from ledger.licence.models import LicenceType
from wildlifelicensing.apps.applications.models import Application, AssessmentRequest
from wildlifelicensing.apps.main.mixins import OfficerOrAssessorRequiredMixin
from wildlifelicensing.apps.main.helpers import is_officer, is_assessor, get_all_officers, render_user_name
from .forms import LoginForm

logger = logging.getLogger(__name__)


def _build_url(base, query):
    return base + '?' + urllib.urlencode(query)


def _get_user_applications(user):
    return Application.objects.filter(applicant_profile__user=user)


def _get_processing_statuses_but_draft():
    return [s for s in Application.PROCESSING_STATUS_CHOICES if s[0] != 'draft']


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
            elif is_assessor(self.request.user):
                return redirect('dashboard:tables_assessor')

            return redirect('dashboard:tables_customer')
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


class DashboardOfficerTreeView(OfficerOrAssessorRequiredMixin, DashboardTreeViewBase):
    template_name = 'wl/dash_tree.html'
    title = 'Dashboard'
    url = reverse_lazy('dashboard:tables_officer')

    def _build_tree_nodes(self):
        """
            +Applications assigned to me
              - status
            +All applications
              - status
        """
        # The draft status is excluded from the officer status list
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

        user_applications = all_applications.filter(assigned_officer=self.request.user)
        query = {
            'application_assignee': self.request.user.pk
        }
        user_applications_node = self._create_node('My assigned applications', href=_build_url(self.url, query),
                                                   count=user_applications.count())
        user_applications_node['state']['expanded'] = True
        for s_value, s_title in statuses:
            applications = user_applications.filter(processing_status=s_value)
            if applications.count() > 0:
                query.update({
                    'application_status': s_value
                })
                href = _build_url(self.url, query)
                node = self._create_node(s_title, href=href, count=applications.count())
                self._add_node(user_applications_node, node)

        return [user_applications_node, all_applications_node]


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
        my_applications_node = self._create_node('My applications', href=self.url, count=my_applications.count())
        # one children node per status
        for status_value, status_title in Application.CUSTOMER_STATUS_CHOICES:
            applications = my_applications.filter(customer_status=status_value)
            if applications.count() > 0:
                query = {
                    'application_status': status_value,
                }
                href = _build_url(self.url, query)
                node = self._create_node(status_title, href=href, count=applications.count())
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
    template_name = 'wl/dash_tables_officer.html'

    def _build_data(self):
        data = super(DashboardTableOfficerView, self)._build_data()
        data['applications']['columnDefinitions'] = [
            {
                'title': 'Lodge No.'
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
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['applications']['filters']['status']['values'] = \
            [('all', 'All')] + _get_processing_statuses_but_draft()
        data['applications']['filters']['assignee'] = {
            'values': [('all', 'All')] + [(user.pk, render_user_name(user),) for user in get_all_officers()]
        }
        data['applications']['ajax']['url'] = reverse('dashboard:data_application_officer')
        return data


class DashboardTableAssessorView(DashboardTableOfficerView):
    """
    Same table as officer with limited filters
    """
    template_name = 'wl/dash_tables_assessor.html'

    def _build_data(self):
        data = super(DashboardTableAssessorView, self)._build_data()
        print('data', data['applications']['filters'])
        data['applications']['ajax']['url'] = reverse('dashboard:data_application_assessor')
        # remove status filter
        del data['applications']['filters']['status']
        print('data', data['applications']['filters'])
        return data


class DashboardTableCustomerView(DashboardTableBaseView):
    template_name = 'wl/dash_tables_customer.html'

    def _build_data(self):
        data = super(DashboardTableCustomerView, self)._build_data()
        data['applications']['columnDefinitions'] = [
            {
                'title': 'Lodge No.'
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
        data['applications']['filters']['status']['values'] = \
            [('all', 'All')] + list(Application.CUSTOMER_STATUS_CHOICES)
        data['applications']['ajax']['url'] = reverse('dashboard:data_application_customer')
        return data


class DataApplicationBaseView(LoginRequiredMixin, BaseDatatableView):
    model = Application
    columns = ['licence_type.code', 'applicant_profile.user', 'applicant_profile', 'processing_status']
    order_columns = ['licence_type.code', 'applicant_profile.user', 'applicant_profile', 'processing_status']

    def _build_search_query(self, fields_to_search, search):
        query = Q()
        for field in fields_to_search:
            query |= Q(**{"{0}__icontains".format(field): search})
        return query

    def _build_user_search_query(self, search):
        fields_to_search = ['applicant_profile__user__last_name', 'applicant_profile__user__first_name',
                            'applicant_profile__user__email']
        return self._build_search_query(fields_to_search, search)

    def _build_profile_search_query(self, search):
        fields_to_search = ['applicant_profile__email', 'applicant_profile__name']
        return self._build_search_query(fields_to_search, search)

    def _render_user_column(self, obj):
        return render_user_name(obj.applicant_profile.user, first_name_first=False)

    def _render_profile_column(self, obj):
        profile = obj.applicant_profile
        if profile is None:
            return 'unknown'
        else:
            # return the string rep
            return '{}'.format(profile)

    columns_helpers = {
        'applicant_profile.user': {
            'render': _render_user_column,
            'search': _build_user_search_query
        },
        'applicant_profile': {
            'render': _render_profile_column,
            'search': _build_profile_search_query
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
        return Q(processing_status=status_value) if status_value != 'all' else Q()

    def filter_queryset(self, qs):
        query = Q()
        # part 1: filter from top level filters
        filters = self._parse_filters()
        for filter_name, filter_value in filters.items():
            # if the value is 'all' no filter to apply.
            # There is a special case for the status. There are two kinds of status depending on the user
            # (customer or officer) also if the application is a draft it should not be seen by the officers.
            # That is why the status filter is left to be implemented by subclasses.
            if filter_name == 'status':
                query &= self._build_status_filter(filter_value)
            if filter_value != 'all':
                if filter_name == 'assignee':
                    query &= Q(assigned_officer__pk=filter_value)
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
            result = super(DataApplicationBaseView, self).render_column(application, column)
        return result

    def _build_global_search_query(self, search):
        query = Q()
        col_data = super(DataApplicationBaseView, self).extract_datatables_column_data()
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


class DataApplicationOfficerView(OfficerOrAssessorRequiredMixin, DataApplicationBaseView):
    columns = ['lodgement_number', 'licence_type.code', 'applicant_profile.user', 'processing_status', 'lodgement_date',
               'assigned_officer', 'action']
    order_columns = ['id', 'licence_type.code',
                     ['applicant_profile.user.last_name', 'applicant_profile.user.first_name',
                      'applicant_profile.user.email'],
                     'processing_status', 'lodgement_date',
                     ['assigned_officer.first_name', 'assigned_officer.last_name', 'assigned_officer.email'], '']

    def _build_status_filter(self, status_value):
        # officers should not see applications in draft mode.
        return Q(processing_status=status_value) if status_value != 'all' else ~Q(customer_status='draft')

    def _render_action_column(self, obj):
        return '<a href="{0}">Process</a>'.format(
            reverse('applications:process', args={obj.pk}),
        )

    def _build_assignee_search_query(self, search):
        fields_to_search = ['assigned_officer__last_name', 'assigned_officer__first_name',
                            'assigned_officer__email']
        return self._build_search_query(fields_to_search, search)

    def _render_assignee_column(self, obj):
        return render_user_name(obj.assigned_officer)

    def _render_lodgement_date(self, obj):
        return _render_date(obj.lodgement_date)

    columns_helpers = dict(DataApplicationBaseView.columns_helpers.items(), **{
        'assigned_officer': {
            'search': _build_assignee_search_query,
            'render': _render_assignee_column
        },
        'action': {
            'render': _render_action_column,
        },
        'lodgement_date': {
            'render': _render_lodgement_date
        },
    })

    def get_initial_queryset(self):
        return self.model.objects.all()


class DataApplicationCustomerView(DataApplicationBaseView):
    columns = ['lodgement_number', 'licence_type.code', 'applicant_profile', 'customer_status', 'lodgement_date',
               'action']
    order_columns = ['lodgement_number', 'licence_type.code', 'applicant_profile', 'customer_status', 'lodgement_date',
                     '']

    def get_initial_queryset(self):
        return _get_user_applications(self.request.user)

    def _build_status_filter(self, status_value):
        return Q(customer_status=status_value) if status_value != 'all' else Q()

    def _render_action_column(self, obj):
        if obj.customer_status == 'draft':
            return '<a href="{0}">{1}</a>'.format(
                reverse('applications:edit_application', args=[obj.licence_type.code, obj.pk]),
                'Continue application'
            )
        elif obj.customer_status == 'amendment_required':
            return '<a href="{0}">{1}</a>'.format(
                reverse('applications:edit_application', args=[obj.licence_type.code, obj.pk]),
                'Amend application'
            )
        else:
            return 'Locked'

    def _render_lodgement_date(self, obj):
        return _render_date(obj.lodgement_date)

    columns_helpers = dict(DataApplicationBaseView.columns_helpers.items(), **{
        'action': {
            'render': _render_action_column,
        },
        'lodgement_date': {
            'render': _render_lodgement_date
        },
    })


class DataApplicationAssessorView(DataApplicationOfficerView):
    def get_initial_queryset(self):
        departments = self.request.user.assessordepartment_set.all()
        assessments = AssessmentRequest.objects.filter(assessor_department__in=departments)
        applications = Application.objects.filter(pk__in=[assessment.application.pk for assessment in assessments])
        return applications
