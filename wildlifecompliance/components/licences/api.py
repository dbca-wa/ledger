from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from datetime import datetime, timedelta
import pytz
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.licences.models import (
    WildlifeLicence,
    LicenceCategory
)
from wildlifecompliance.components.licences.serializers import (
    WildlifeLicenceSerializer,
    LicenceCategorySerializer,
    DTInternalWildlifeLicenceSerializer,
    DTExternalWildlifeLicenceSerializer
)
from wildlifecompliance.components.applications.models import Application

from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer


class LicenceFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """
    def filter_queryset(self, request, queryset, view):

        # Get built-in DRF datatables queryset first to join with search text, then apply additional filters
        super_queryset = super(LicenceFilterBackend, self).filter_queryset(request, queryset, view).distinct()

        total_count = queryset.count()
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        category_name = request.GET.get('category_name')
        holder = request.GET.get('holder')
        search_text = request.GET.get('search[value]')
        if queryset.model is WildlifeLicence:

            # search_text filter, join all custom search columns
            # where ('searchable: false' in the datatable definition)
            if search_text:
                search_text = search_text.lower()
                # join queries for the search_text search
                search_text_licence_ids = []
                for wildlifelicence in queryset:
                    if (search_text in wildlifelicence.current_application.licence_category.lower()
                        or search_text in wildlifelicence.current_application.applicant.lower()
                    ):
                        search_text_licence_ids.append(wildlifelicence.id)
                    # if applicant is not an organisation, also search against the user's email address
                    if (wildlifelicence.current_application.applicant_type == Application.APPLICANT_TYPE_PROXY and
                        search_text in wildlifelicence.current_application.proxy_applicant.email.lower()):
                            search_text_licence_ids.append(wildlifelicence.id)
                    if (wildlifelicence.current_application.applicant_type == Application.APPLICANT_TYPE_SUBMITTER and
                        search_text in wildlifelicence.current_application.submitter.email.lower()):
                            search_text_licence_ids.append(wildlifelicence.id)
                # use pipe to join both custom and built-in DRF datatables querysets (returned by super call above)
                # (otherwise they will filter on top of each other)
                queryset = queryset.filter(id__in=search_text_licence_ids).distinct() | super_queryset

            # apply user selected filters
            category_name = category_name.lower() if category_name else 'all'
            if category_name != 'all':
                category_name_licence_ids = []
                for wildlifelicence in queryset:
                    if category_name in wildlifelicence.current_application.licence_category_name.lower():
                        category_name_licence_ids.append(wildlifelicence.id)
                queryset = queryset.filter(id__in=category_name_licence_ids)
            if date_from:
                date_from_licence_ids = []
                for wildlifelicence in queryset:
                    if (pytz.timezone('utc').localize(datetime.strptime(date_from, '%Y-%m-%d'))
                            <= wildlifelicence.current_activities.order_by('-issue_date').first().issue_date):
                                date_from_licence_ids.append(wildlifelicence.id)
                queryset = queryset.filter(id__in=date_from_licence_ids)
            if date_to:
                date_to_licence_ids = []
                for wildlifelicence in queryset:
                    if (pytz.timezone('utc').localize(datetime.strptime(date_to, '%Y-%m-%d')) + timedelta(days=1)
                            >= wildlifelicence.current_activities.order_by('-issue_date').first().issue_date):
                                date_to_licence_ids.append(wildlifelicence.id)
                queryset = queryset.filter(id__in=date_to_licence_ids)
            holder = holder.lower() if holder else 'all'
            if holder != 'all':
                holder_licence_ids = []
                for wildlifelicence in queryset:
                    if holder in wildlifelicence.current_application.applicant.lower():
                        holder_licence_ids.append(wildlifelicence.id)
                queryset = queryset.filter(id__in=holder_licence_ids)

        # override queryset ordering, required because the ordering is usually handled
        # in the super call, but is then clobbered by the custom queryset joining above
        # also needed to disable ordering for all fields for which data is not an
        # WildlifeLicence model field, as property functions will not work with order_by
        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        setattr(view, '_datatables_total_count', total_count)
        return queryset


class LicenceRenderer(DatatablesRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'view' in renderer_context and hasattr(renderer_context['view'], '_datatables_total_count'):
            data['recordsTotal'] = renderer_context['view']._datatables_total_count
        return super(LicenceRenderer, self).render(data, accepted_media_type, renderer_context)


class LicencePaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (LicenceFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (LicenceRenderer,)
    queryset = WildlifeLicence.objects.none()
    serializer_class = DTExternalWildlifeLicenceSerializer
    page_size = 10

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return WildlifeLicence.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            return WildlifeLicence.objects.filter(
                Q(current_application__org_applicant_id__in=user_orgs) |
                Q(current_application__proxy_applicant=user) |
                Q(current_application__submitter=user)
            )
        return WildlifeLicence.objects.none()

    @list_route(methods=['GET', ])
    def internal_datatable_list(self, request, *args, **kwargs):
        self.serializer_class = DTInternalWildlifeLicenceSerializer
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTInternalWildlifeLicenceSerializer(result_page, context={'request': request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    @list_route(methods=['GET', ])
    def external_datatable_list(self, request, *args, **kwargs):
        self.serializer_class = DTExternalWildlifeLicenceSerializer
        user_orgs = [
            org.id for org in request.user.wildlifecompliance_organisations.all()]
        queryset = WildlifeLicence.objects.filter(
            Q(current_application__org_applicant_id__in=user_orgs) |
            Q(current_application__proxy_applicant=request.user) |
            Q(current_application__submitter=request.user)
        )
        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTExternalWildlifeLicenceSerializer(result_page, context={'request': request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class LicenceViewSet(viewsets.ModelViewSet):
    queryset = WildlifeLicence.objects.all()
    serializer_class = WildlifeLicenceSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return WildlifeLicence.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            return WildlifeLicence.objects.filter(
                Q(current_application__org_applicant_id__in=user_orgs) |
                Q(current_application__proxy_applicant=user) |
                Q(current_application__submitter=user)
            )
        return WildlifeLicence.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by org
        org_id = request.GET.get('org_id', None)
        if org_id:
            queryset = queryset.filter(current_application__org_applicant_id=org_id)
        # Filter by proxy_applicant
        proxy_applicant_id = request.GET.get('proxy_applicant_id', None)
        if proxy_applicant_id:
            queryset = queryset.filter(current_application__proxy_applicant_id=proxy_applicant_id)
        # Filter by submitter
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            queryset = queryset.filter(current_application__submitter_id=submitter_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET', ])
    def user_list(self, request, *args, **kwargs):
        user_orgs = [
            org.id for org in request.user.wildlifecompliance_organisations.all()]
        qs = []
        qs.extend(list(self.get_queryset().filter(current_application__submitter=request.user)))
        qs.extend(
            list(
                self.get_queryset().filter(
                    current_application__proxy_applicant=request.user)))
        qs.extend(
            list(
                self.get_queryset().filter(
                    current_application__org_applicant_id__in=user_orgs)))
        queryset = list(set(qs))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LicenceCategoryViewSet(viewsets.ModelViewSet):
    queryset = LicenceCategory.objects.all()
    serializer_class = LicenceCategorySerializer


class UserAvailableWildlifeLicencePurposesViewSet(viewsets.ModelViewSet):
    # Filters to only return purposes that are
    # available for selection when applying for
    # a new application
    queryset = LicenceCategory.objects.all()
    serializer_class = LicenceCategorySerializer

    def list(self, request, *args, **kwargs):
        print(self.request)
        print(self.request.GET)
        print(self.request.GET.get('org_applicant', None))
        queryset = self.get_queryset()
        serializer = LicenceCategorySerializer(queryset, many=True, context={'request':request})
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super(UserAvailableWildlifeLicencePurposesViewSet, self).get_serializer_context()
        context.update({
            "test": 'test context'
        })
        return context
