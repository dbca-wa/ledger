from __future__ import unicode_literals

import datetime
import json
import logging

from dateutil.parser import parse as date_parse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
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

from wildlifelicensing.apps.payments.utils import get_application_payment_status, PAYMENT_STATUS_AWAITING, \
    PAYMENT_STATUSES

logger = logging.getLogger(__name__)


def build_url(base, query):
    return base + '?' + urlencode(query)


def get_processing_statuses_but_draft():
    return [s for s in Application.PROCESSING_STATUS_CHOICES if s[0] != 'draft' and s[0] != 'temp']


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


def render_download_return_template(ret):
    url = reverse('wl_returns:download_return_template', args=[ret.return_type.pk])
    return '<a href="{}">Download (XLSX)</a>'.format(url)


def render_payment(application, redirect_url):
    status = get_application_payment_status(application)
    result = '{}'.format(PAYMENT_STATUSES[status])
    if status == PAYMENT_STATUS_AWAITING:
        url = '{}?redirect_url={}'.format(
            reverse('wl_payments:manual_payment', args=[application.id]),
            redirect_url
        )
        result += ' <a href="{}">Enter payment</a>'.format(url)
    return result


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
        licence_types = [('all', 'All')] + [(lt.pk, lt.display_name) for lt in LicenceType.objects.all()]
        data = {
            'applications': {
                'tableOptions': {
                    'pageLength': 10,
                    'order': [[0, 'asc']],
                },
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
                'tableOptions': {
                    'pageLength': 10,
                    'order': [[0, 'asc']],
                },
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
                'tableOptions': {
                    'pageLength': 10,
                    'order': [[0, 'asc']],
                },
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
            if 'query' not in data:
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
    17/10/2016: Added support for saving column_order/search/page_length in session
    """
    model = None
    columns = [
        'licence_type'
    ]
    order_columns = [
        ['licence_type.short_name', 'licence_type.name'],
    ]
    columns_helpers = {
        # a global render and search fot the licence_type column.
        # Note: this has to be overridden if the model hasn't the licence_type related field.
        'licence_type': {
            'render': lambda self, instance: instance.licence_type.display_name,
            'search': lambda self, search: build_field_query(
                ['licence_type__short_name', 'licence_type__name'], search)
        }
    }

    SESSION_SAVE_SETTINGS = True  # Set to True if you want to save order/search in the session
    SESSION_KEY = None  # if you don't specify a session_key one will be generated based on the class name

    @classmethod
    def get_session_key(cls):
        result = cls.SESSION_KEY or 'dt_{}'.format(cls.__name__)
        return result

    @classmethod
    def get_session_data(cls, request):
        result = {}
        if request:
            result = request.session.get(cls.get_session_key(), {})
        return result

    @classmethod
    def get_session_order(cls, request, default=None):
        return cls.get_session_data(request).get('order', default)

    @classmethod
    def get_session_search_term(cls, request, default=''):
        return cls.get_session_data(request).get('search', default)

    @classmethod
    def get_session_page_length(cls, request, default=10):
        return cls.get_session_data(request).get('pageLength', default)

    @classmethod
    def get_session_filters(cls, request):
        return cls.get_session_data(request).get('filters', {})

    def _build_global_search_query(self, search):
        # a bit of a hack for searching for date with a '/', ex 27/05/2016
        # The right way to search for a date is to use the format YYYY-MM-DD.
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

    def _get_filters(self):
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

    def _get_order_config_array(self):
        """
        From the order parameters passed in the request, return a datatable configuration array that can be stored
        in session. See https://datatables.net/reference/option/order
        Example:
        Received params:
        (u'order[0][column]', u'4'), (u'order[0][dir]', u'desc'), (u'order[1][column]', u'0'), (u'order[1][dir]', u'desc')
        Returned array:
        [[4, 'desc'], [0, 'desc']]
        :return:
        """
        result = []
        querydict = self._querydict
        counter = 0
        order_col_number_key = 'order[{0}][column]'.format(counter)
        order_direction_key = 'order[{0}][dir]'.format(counter)
        while order_col_number_key in querydict and order_direction_key in querydict:
            result.append([
                int(querydict[order_col_number_key]),
                querydict[order_direction_key]
            ])
            counter += 1
            order_col_number_key = 'order[{0}][column]'.format(counter)
            order_direction_key = 'order[{0}][dir]'.format(counter)
        return result

    def _get_search_value(self):
        # return the search value parameter
        return self._querydict.get('search[value]')

    def _get_page_length(self):
        return int(self._querydict.get('length', 10))

    def save_session_data(self):
        data = {
            'order': self._get_order_config_array(),
            'search': self._get_search_value(),
            'pageLength': self._get_page_length(),
            'filters': self._get_filters()
        }
        self.request.session[self.get_session_key()] = data

    def get_context_data(self, *args, **kwargs):
        """
        Override this method just to add a call to save_session_data if set-up.
        The post_process is not supposed to return anything. It will mostly be used to store session data like the
        column ordering and the search
        :param args:
        :param kwargs:
        :return:
        """
        result = super(DataTableBaseView, self).get_context_data(*args, **kwargs)
        try:
            if self.SESSION_SAVE_SETTINGS:
                self.save_session_data()
        except Exception as e:
            logger.exception(str(e))

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
        filters = self._get_filters()
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
    columns = [
        'licence_type',
        'applicant',
        'applicant_profile',
        'processing_status'
    ]
    order_columns = [
        ['licence_type.short_name', 'licence_type.name'],
        'applicant',
        'applicant_profile',
        'processing_status'
    ]

    columns_helpers = dict(DataTableBaseView.columns_helpers.items(), **{
        'applicant': {
            'render': lambda self, instance: render_user_name(instance.applicant, first_name_first=False),
            'search': lambda self, search: build_field_query(
                ['applicant_profile__user__last_name', 'applicant_profile__user__first_name'], search)
        },
        'applicant_profile': {
            'render': lambda self, instance: '{}'.format(instance.applicant_profile),
            'search': lambda self, search: build_field_query(
                ['applicant_profile__email', 'applicant_profile__name'], search)
        },
    })

    @staticmethod
    def filter_status(value):
        return Q(processing_status=value) if value.lower() != 'all' else None

    @staticmethod
    def filter_assignee(value):
        return Q(assigned_officer__pk=value) if value.lower() != 'all' else None

    @staticmethod
    def filter_licence_type(value):
        return Q(licence_type__pk=value) if value.lower() != 'all' else None

    def get_initial_queryset(self):
        return self.model.objects.all().exclude(processing_status='temp')
