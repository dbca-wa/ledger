from __future__ import unicode_literals

import datetime
import json
import logging

from dateutil.parser import parse as date_parse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.db.models.query import EmptyQuerySet
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.http import urlencode

from ledger.licence.models import LicenceType
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.dashboard.forms import LoginForm
from wildlifelicensing.apps.main.helpers import is_officer, is_assessor, render_user_name

logger = logging.getLogger(__name__)


def build_url(base, query):
    return base + '?' + urlencode(query)


def get_processing_statuses_but_draft():
    return [s for s in Application.PROCESSING_STATUS_CHOICES if s[0] != 'draft']


# render date in dd/mm/yyyy format
def render_date(date):
    if isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
        return date.strftime("%d/%m/%Y")
    if not date:
        return ''
    return 'not a valid date object'


def render_lodgement_number(application):
    if application is not None and application.lodgement_number and application.lodgement_sequence:
        return '%s-%d' % (application.lodgement_number, application.lodgement_sequence)
    else:
        return ''


def render_licence_number(licence):
    if licence is not None and licence.licence_number and licence.licence_sequence:
        return '%s-%d' % (licence.licence_number, licence.licence_sequence)
    else:
        return ''


def render_licence_document(licence):
    if licence is not None and licence.licence_document is not None:
        return '<a href="{0}" target="_blank">View PDF</a><img height="20" src="{1}"></img>'.format(
            licence.licence_document.file.url, static('wl/img/pdf.png'))
    else:
        return ''


class DashBoardRoutingView(TemplateView):
    template_name = 'wl/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_officer(self.request.user):
                return redirect('wl_dashboard:tree_officer')
            elif is_assessor(self.request.user):
                return redirect('wl_dashboard:tables_assessor')

            return redirect('wl_dashboard:tables_customer')
        else:
            kwargs['form'] = LoginForm
            return super(DashBoardRoutingView, self).get(*args, **kwargs)


class DashboardTreeViewBase(TemplateView):
    template_name = 'wl/dash_tree.html'
    url = reverse_lazy('wl_dashboard:tables_applications_officer')

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


def build_field_query(fields_to_search, search):
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
        # a bit of a hack for searching for date with a '/', ex 27/05/2016
        # The rigth way to search for a date is to use the format YYYY-MM-DD.
        # To search with dd/mm/yyyy we use the dateutil parser to infer a date
        if search and search.find('/') >= 0:
            try:
                search = str(date_parse(search, dayfirst=True).date())
            except:
                pass
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
            'search': lambda self, search: build_field_query(
                ['applicant_profile__user__last_name', 'applicant_profile__user__first_name'], search)
        },
        'applicant_profile': {
            'render': lambda self, instance: '{}'.format(instance.applicant_profile),
            'search': lambda self, search: build_field_query(
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
