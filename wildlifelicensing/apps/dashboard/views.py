import json
import urllib

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from braces.views import LoginRequiredMixin

from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.helpers import is_officer
from .forms import LoginForm


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
    def _build_tree_nodes():

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

        url = reverse_lazy('dashboard:tables')

        # pending applications
        query = {
            'model': 'application',
            'state': 'lodged',
        }
        pending_applications = Application.objects.filter(state='lodged')
        pending_applications_node = _create_node('Pending applications', href=_build_url(url, query),
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


class DashboardTableView(TemplateView):
    template_name = 'wl/dash_tables.html'

    def get_context_data(self, **kwargs):
        license_types = [('all', 'All')]
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
                'licenses': {
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


class ApplicationDataTableView(BaseDatatableView):
    model = Application
    columns = ['state']
    order_columns = ['state']

    def get(self, request, *args, **kwargs):
        return super(ApplicationDataTableView, self).get(request, *args, **kwargs)
