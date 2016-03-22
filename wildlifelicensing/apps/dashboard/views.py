import json
import urllib

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from wildlifelicensing.apps.applications.models import Application


def _build_url(base, query):
    return base + '?' + urllib.urlencode(query)


class DashBoardRoutingView(TemplateView):
    template_name = 'wl/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect('dashboard:quick')
        else:
            return super(DashBoardRoutingView, self).get(*args, **kwargs)


class DashboardQuickView(TemplateView):
    template_name = 'wl/dash_quick.html'

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
        # pending licenses
        query = {
            'model': 'license',
            'status': 'pending',
        }
        pending_licenses = []
        pending_licenses_node = _create_node('Pending licenses', href=_build_url(url, query),
                                             count=len(pending_licenses))
        # overdue license
        query = {
            'model': 'return',
            'due_date': 'overdue'
        }
        overdue_returns = []
        overdue_returns_node = _create_node('Overdue returns', href=_build_url(url, query),
                                            count=len(overdue_returns))
        return [pending_applications_node, pending_licenses_node, overdue_returns_node]

    def get_context_data(self, **kwargs):
        if 'dataJSON' not in kwargs:
            kwargs['dataJSON'] = json.dumps(self._build_tree_nodes())
        return super(DashboardQuickView, self).get_context_data(**kwargs)


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
