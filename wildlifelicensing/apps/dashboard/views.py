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
from wildlifelicensing.apps.main.helpers import is_officer, is_customer
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
        url = reverse_lazy('dashboard:tables')

        # pending applications
        query = {
            'model': 'application',
            'status': 'lodged',
        }
        pending_applications = Application.objects.filter(status='lodged')
        pending_applications_node = self._create_node('New applications', href=_build_url(url, query),
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


class DashboardCustomerTreeView(LoginRequiredMixin, DashboardTreeViewBase):
    template_name = 'wl/dash_tree.html'
    title = 'My Dashboard'

    def _build_tree_nodes(self):
        """
            +My applications
              - status
        :return:
        """
        my_applications = _get_user_applications(self.request.user)
        target_url = reverse_lazy('dashboard:tables')
        my_applications_node = self._create_node('My applications', href=target_url, count=len(my_applications))
        # one children node per status
        for status in [s[0] for s in Application.STATUS_CHOICES]:
            applications = my_applications.filter(status=status)
            if applications.count() > 0:
                query = {
                    'model': 'application',
                    'status': status,
                }
                href = _build_url(target_url, query)
                node = self._create_node(status, href=href, count=applications.count())
                self._add_node(my_applications_node, node)
        return [my_applications_node]


class DashboardTableView(TemplateView):
    template_name = 'wl/dash_tables.html'

    def get_context_data(self, **kwargs):
        licence_types = [('all', 'All')] + [(lt.pk, lt.code) for lt in LicenceType.objects.all()]
        if 'dataJSON' not in kwargs:
            data = {
                'applications': {
                    'filters': {
                        'licenceType': {
                            'values': licence_types,
                        },
                        'status': {
                            'values': [('all', 'All')] + list(Application.STATUS_CHOICES),
                        }
                    }
                },
                'query': self.request.GET.dict()
            }
            kwargs['dataJSON'] = json.dumps(data)
        return super(DashboardTableView, self).get_context_data(**kwargs)


class ApplicationDataTableView(LoginRequiredMixin, BaseDatatableView):
    model = Application
    columns = ['licence_type', 'applicant_persona', 'status']
    order_columns = ['licence_type', 'applicant_persona', 'status']

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
        if is_customer(self.request.user):
            return _get_user_applications(self.request.user)
        else:
            return self.model.objects.all()

    def filter_queryset(self, qs):
        filters = self._parse_filters()
        query = Q()
        for filter_name, filter_value in filters.items():
            # if the value is 'all' no filter to apply
            if filter_value != 'all':
                if filter_name == 'status':
                    query &= Q(status=filter_value)
        return qs.filter(query)

    def render_column(self, application, column):
        def render_applicant_column(persona):
            user_details = '{last}, {first}, {email}'.format(
                last=persona.user.last_name,
                first=persona.user.first_name,
                email=persona.email
            )
            persona_details = '{}'.format(persona)
            if is_officer(self.request.user):
                return user_details + ' [{}]'.format(persona_details)
            else:
                return persona_details

        if column == 'licence_type':
            licence_type = application.licence_type.code
            result = '{}'.format(licence_type) if licence_type is not None else 'unknown'
        elif column == 'applicant_persona':
            result = render_applicant_column(
                application.applicant_persona) if application.applicant_persona is not None else 'unknown'
        else:
            result = super(ApplicationDataTableView, self).render_column(application, column)
        return result
