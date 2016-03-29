from __future__ import unicode_literals
import json
import urllib
import logging

from django.core.urlresolvers import reverse_lazy
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
        # pending applications
        query = {
            'model': 'application',
            'customer_status': 'pending',
        }
        pending_applications = Application.objects.filter(processing_status='lodged')
        pending_applications_node = self._create_node('New applications', href=_build_url(self.url, query),
                                                      count=len(pending_applications))
        return [pending_applications_node]

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
    licence_types = [('all', 'All')] + [(lt.pk, lt.code) for lt in LicenceType.objects.all()]
    applications_statuses = []
    data = {
        'applications': {
            'columnDefinitions': [
            ],
            'filters': {
                'licenceType': {
                    'values': licence_types,
                },
                'status': {
                    'values': applications_statuses,
                }
            },
            'ajax': {
                'url': ''
            }
        }
    }

    def get_context_data(self, **kwargs):
        if 'dataJSON' not in kwargs:
            # add the request query to the data
            self.data['query'] = self.request.GET.dict()
            kwargs['dataJSON'] = json.dumps(self.data)
        return super(DashboardTableBaseView, self).get_context_data(**kwargs)


class DashboardTableOfficerView(DashboardTableBaseView):
    applications_statuses = [('all', 'All')] + list(Application.PROCESSING_STATUS_CHOICES)
    data = {
        'applications': {
            'columnDefinitions': [
                {
                    'title': 'Licence Type',
                    'name': 'license_type',
                },
                {
                    'title': 'User',
                    'name': 'applicant_persona__user'
                },
                {
                    'title': 'Persona',
                    'name': 'applicant_persona'
                },
                {
                    'title': 'Status',
                    'name': 'status'
                }
            ],
            'filters': {
                'licenceType': {
                    'values': DashboardTableBaseView.licence_types,
                },
                'status': {
                    'values': applications_statuses,
                }
            },
            'ajax': {
                # TODO why the reverse throw a ImproperlyConfigured exception
                # 'url': reverse('dashboard:applications_data_officer')
                'url': '/dashboard/data/applications/officer/'
            }
        }
    }


class DashboardTableCustomerView(DashboardTableBaseView):
    applications_statuses = [('all', 'All')] + list(Application.CUSTOMER_STATUS_CHOICES)
    data = {
        'applications': {
            'columnDefinitions': [
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
                }
            ],
            'filters': {
                'licenceType': {
                    'values': DashboardTableBaseView.licence_types,
                },
                'status': {
                    'values': applications_statuses,
                }
            },
            'ajax': {
                # TODO why the reverse throw a ImproperlyConfigured exception
                # 'url': reverse('dashboard:applications_data_customer')
                'url': '/dashboard/data/applications/customer/'
            }
        }
    }


class ApplicationDataTableBaseView(LoginRequiredMixin, BaseDatatableView):
    model = Application
    columns = ['licence_type.code', 'applicant_persona', 'processing_status']
    order_columns = ['licence_type', 'applicant_persona', 'processing_status']

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
        filters = self._parse_filters()
        query = Q()
        for filter_name, filter_value in filters.items():
            # if the value is 'all' no filter to apply
            if filter_value != 'all':
                if filter_name == 'status':
                    query &= self._build_status_filter(filter_value)
        return qs.filter(query)

    def render_column(self, application, column):
        if column == 'licence_type':
            result = '{}'.format(application.licence_type.code)
        elif column == 'applicant_persona.user':
            user = application.applicant_persona.user
            result = '{last}, {first}, {email}'.format(
                last=user.last_name,
                first=user.first_name,
                email=user.email
            )
        elif column == 'applicant_persona':
            result = '{}'.format(application.applicant_persona)
        else:
            result = super(ApplicationDataTableBaseView, self).render_column(application, column)
        return result


class ApplicationDataTableOfficerView(ApplicationDataTableBaseView):
    columns = ['licence_type.code', 'applicant_persona.user', 'applicant_persona', 'processing_status']
    order_columns = ['licence_type.code', 'applicant_persona.user', 'applicant_persona', 'processing_status']

    def get_initial_queryset(self):
        return self.model.objects.all()


class ApplicationDataTableCustomerView(ApplicationDataTableBaseView):
    columns = ['licence_type.code', 'applicant_persona', 'processing_status']
    order_columns = ['licence_type.code', 'applicant_persona', 'processing_status']

    def get_initial_queryset(self):
        return _get_user_applications(self.request.user)

    def _build_status_filter(self, status_value):
        return Q(customer_status=status_value)
