import json
import datetime
import itertools
import urllib

from django.views.generic import TemplateView, RedirectView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy, reverse
from braces.views import LoginRequiredMixin

from .models import generate_mock_data, DATA_SAMPLES

MOCK_DATA_SESSION_KEY = 'mock-data'


def _get_mock_data(request):
    if MOCK_DATA_SESSION_KEY in request.session:
        mock_data = request.session[MOCK_DATA_SESSION_KEY]
    else:
        mock_data = generate_mock_data()
        request.session[MOCK_DATA_SESSION_KEY] = mock_data
    return mock_data


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
    def _build_tree_nodes(mock_data):

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

        def _add_node(parent, child):
            if 'nodes' not in parent or type(parent['nodes']) != list:
                parent['nodes'] = [child]
            else:
                parent['nodes'].append(child)
            return parent

        date_format = '%Y-%m-%d'
        today = datetime.date.today()
        url = reverse_lazy('dashboard:tables')

        # pending applications
        query = {
            'model': 'application',
            'status': 'pending',
        }
        pending_applications = [app for app in mock_data['applications'] if app['status'].lower() == 'pending']
        pending_applications_node = _create_node('Pending applications', href=_build_url(url, query),
                                                 count=len(pending_applications))
        data = sorted(pending_applications, lambda x, y: cmp(x['license_type'].lower(), y['license_type'].lower()))
        for k, g in itertools.groupby(data, lambda x: x['license_type']):
            query['license_type'] = k
            node = _create_node(k, href=_build_url(url, query), count=len(list(g)))
            _add_node(pending_applications_node, node)

        # pending licenses
        query = {
            'model': 'license',
            'status': 'pending',
        }
        pending_licenses = [lic for lic in mock_data['licenses'] if lic['status'] == 'pending']
        pending_licenses_node = _create_node('Pending licenses', href=_build_url(url, query),
                                             count=len(pending_licenses))
        data = sorted(pending_licenses, lambda x, y: cmp(x['license_type'].lower(), y['license_type'].lower()))
        for k, g in itertools.groupby(data, lambda x: x['license_type']):
            query['license_type'] = k
            node = _create_node(k, href=_build_url(url, query), count=len(list(g)))
            _add_node(pending_licenses_node, node)

        # overdue license
        query = {
            'model': 'return',
            'due_date': 'overdue'
        }
        overdue_returns = [ret for ret in mock_data['returns'] if
                           datetime.datetime.strptime(ret['due_date'], date_format).date() < today]
        overdue_returns_node = _create_node('Overdue returns', href=_build_url(url, query),
                                            count=len(overdue_returns))
        data = sorted(overdue_returns, lambda x, y: cmp(x['license_type'].lower(), y['license_type'].lower()))
        for k, g in itertools.groupby(data, lambda x: x['license_type']):
            query['license-type'] = k
            node = _create_node(k, href=_build_url(url, query), count=len(list(g)))
            _add_node(overdue_returns_node, node)

        return [pending_applications_node, pending_licenses_node, overdue_returns_node]

    def get_context_data(self, **kwargs):
        mock_data = _get_mock_data(self.request)
        if 'dataJSON' not in kwargs:
            kwargs['dataJSON'] = json.dumps(self._build_tree_nodes(mock_data))
        return super(DashboardQuickView, self).get_context_data(**kwargs)


class DashboardTableView(TemplateView):
    template_name = 'wl/dash_tables.html'

    def get_context_data(self, **kwargs):
        mock_data = _get_mock_data(self.request)
        if 'dataJSON' not in kwargs:
            data = {
                'applications': {
                    'tableData': mock_data['applications'],
                    'collapsed': False,
                    'filters': {
                        'licenseType': {
                            'values': ['All'] + DATA_SAMPLES['licenseTypes'],
                        },
                        'status': {
                            'values': ['All'] + DATA_SAMPLES['statusApplication'],
                            'selected': 'All'
                        }
                    }
                },
                'licenses': {
                    'tableData': mock_data['licenses'],
                    'collapsed': False,
                    'filters': {
                        'licenseType': {
                            'values': ['All'] + DATA_SAMPLES['licenseTypes'],
                            'selected': 'All'
                        },
                        'status': {
                            'values': ['All'] + DATA_SAMPLES['statusLicense'],
                            'selected': 'All'
                        }
                    }
                },
                'returns': {
                    'tableData': mock_data['returns'],
                    'collapsed': False,
                    'filters': {
                        'licenseType': {
                            'values': ['All'] + DATA_SAMPLES['licenseTypes'],
                            'selected': 'All'
                        },
                        'dueDate': {
                            'values': ['All', 'Overdue'],
                            'selected': 'All'
                        }
                    }
                },
                'query': self.request.GET.dict()
            }
            kwargs['dataJSON'] = json.dumps(data)
        return super(DashboardTableView, self).get_context_data(**kwargs)
