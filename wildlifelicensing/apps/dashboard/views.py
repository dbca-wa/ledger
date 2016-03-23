import json
import urllib
import logging

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from braces.views import LoginRequiredMixin

from ledger.licence.models import LicenceType
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.helpers import is_officer, is_customer
from .forms import LoginForm

logger = logging.getLogger(__name__)


def _build_url(base, query):
    return base + '?' + urllib.urlencode(query)


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
            'nodes': None
        }
        result = {}
        result.update(node_template)
        result['text'] = str(title)
        if href is not None:
            result['href'] = str(href)
        if count is not None:
            result['tags'].append(str(count))

        return result

    def _build_tree_nodes(self):
        url = reverse_lazy('dashboard:tables')

        # pending applications
        query = {
            'model': 'application',
            'state': 'lodged',
        }
        pending_applications = Application.objects.filter(state='lodged')
        pending_applications_node = self._create_node('Pending applications', href=_build_url(url, query),
                                                      count=len(pending_applications))
        print('super node', pending_applications_node)
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
        target_url = reverse_lazy('dashboard:tables')
        my_applications = Application.objects.filter(applicant=self.request.user)
        my_applications_node = self._create_node('My applications', href=target_url, count=len(my_applications))
        print('Node', my_applications_node)
        return [my_applications_node]


class DashboardTableView(TemplateView):
    template_name = 'wl/dash_tables.html'

    def get_context_data(self, **kwargs):
        license_types = [('all', 'All')] + [(lt.pk, lt.name) for lt in LicenceType.objects.all()]
        if 'dataJSON' not in kwargs:
            data = {
                'applications': {
                    'filters': {
                        'licenseType': {
                            'values': license_types,
                        },
                        'status': {
                            'values': [('all', 'All')] + list(Application.STATES),
                        }
                    }
                },
                'licences': {
                    'filters': {
                        'licenseType': {
                            'values': license_types
                        },
                        'status': {
                            'values': [('all', 'All')],
                        }
                    }
                },
                'returns': {
                    'filters': {
                        'licenseType': {
                            'values': license_types,
                        },
                        'dueDate': {
                            'values': [('all', 'All'), ('overdue', 'Overdue')],
                        }
                    }
                },
                'query': self.request.GET.dict()
            }
            kwargs['dataJSON'] = json.dumps(data)
        return super(DashboardTableView, self).get_context_data(**kwargs)


class ApplicationDataTableView(LoginRequiredMixin, BaseDatatableView):
    model = Application
    columns = ['licence_type', 'applicant', 'state']
    order_columns = ['licence_type', 'applicant', 'state']

    def get_initial_queryset(self):
        print('init query set', self.request.user)
        if is_customer(self.request.user):
            return self.model.objects.filter(applicant=self.request.user)
        else:
            return self.model.objects.all()

    def render_column(self, application, column):
        def render_applicant(applicant):
            return '{last}, {first} ({email})'.format(
                last=applicant.last_name,
                first=applicant.first_name,
                email=applicant.email
            )

        if column == 'licence_type':
            licence_type = application.licence_type
            result = '{}'.format(licence_type) if licence_type is not None else 'unknown'
        elif column == 'applicant':
            user = application.applicant
            result = render_applicant(user) if user is not None else 'unknown'
        else:
            result = super(ApplicationDataTableView, self).render_column(application, column)
        return result
