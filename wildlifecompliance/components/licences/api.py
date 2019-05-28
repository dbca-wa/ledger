import traceback
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import viewsets, serializers
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from datetime import datetime, timedelta
import pytz
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.licences.models import (
    WildlifeLicence,
    LicenceCategory
)
from wildlifecompliance.components.applications.serializers import (
    ExternalApplicationSelectedActivitySerializer
)
from wildlifecompliance.components.licences.serializers import (
    WildlifeLicenceSerializer,
    LicenceCategorySerializer,
    DTInternalWildlifeLicenceSerializer,
    DTExternalWildlifeLicenceSerializer
)
from wildlifecompliance.components.applications.models import (
    Application,
    ApplicationSelectedActivity
)
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
        # Filter by user (submitter or proxy_applicant)
        user_id = request.GET.get('user_id', None)
        if user_id:
            queryset = WildlifeLicence.objects.filter(
                Q(current_application__proxy_applicant=user_id) |
                Q(current_application__submitter=user_id)
            )
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
        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTExternalWildlifeLicenceSerializer(result_page, context={'request': request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class LicenceViewSet(viewsets.ModelViewSet):
    queryset = WildlifeLicence.objects.all()
    serializer_class = DTExternalWildlifeLicenceSerializer

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

    def list(self, request, pk=None, *args, **kwargs):
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
        # Display only the relevant Activity if activity_id param set
        activity_id = request.GET.get('activity_id', None)
        if activity_id and pk:
            queryset = queryset.get(id=pk).current_activities.get(id=activity_id)
            serializer = ExternalApplicationSelectedActivitySerializer(queryset)
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

    @detail_route(methods=['POST', ])
    def cancel_activity(self, request, pk=None, *args, **kwargs):
        try:
            activity_id = request.GET.get('activity_id', None)
            if activity_id and pk:
                instance = self.get_object()
                instance = instance.current_activities.get(id=activity_id)
                if not request.user.has_perm('wildlifecompliance.licensing_officer'):
                    raise serializers.ValidationError(
                        'You are not authorised to cancel licenced activities')
                instance.cancel(request)
                serializer = ExternalApplicationSelectedActivitySerializer(instance)
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID and Activity ID must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


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
        from wildlifecompliance.components.licences.models import LicencePurpose

        queryset = self.get_queryset()
        only_purpose_records = None
        application_type = request.GET.get('application_type')
        licence_category = request.GET.get('licence_category')

        active_applications = Application.get_active_licence_applications(request, application_type)
        if not active_applications.count() and application_type == Application.APPLICATION_TYPE_RENEWAL:
            # Do not present with renewal options if no activities are within the renewal period
            queryset = LicenceCategory.objects.none()
            only_purpose_records = LicencePurpose.objects.none()

        elif active_applications.count():
            # Activities relevant to the current application type
            current_activities = Application.get_active_licence_activities(request, application_type)
            active_category_ids = current_activities.values_list(
                'licence_activity__licence_category_id',
                flat=True
            )
            active_purpose_ids = []
            for selected_activity in current_activities:
                active_purpose_ids.extend([purpose.id for purpose in selected_activity.purposes])

            if application_type in [
                Application.APPLICATION_TYPE_ACTIVITY,
                Application.APPLICATION_TYPE_NEW_LICENCE,
            ]:
                only_purpose_records = LicencePurpose.objects.exclude(
                    id__in=active_purpose_ids
                )

            elif application_type in [
                Application.APPLICATION_TYPE_AMENDMENT,
                Application.APPLICATION_TYPE_RENEWAL,
            ]:
                amendable_purpose_ids = active_applications.values_list(
                    'licence_purposes__id',
                    flat=True
                )

                queryset = queryset.filter(id__in=active_category_ids)
                only_purpose_records = LicencePurpose.objects.filter(
                    id__in=amendable_purpose_ids,
                    licence_activity_id__in=current_activities.values_list(
                        'licence_activity_id', flat=True)
                )

        if licence_category:
            only_purpose_records = only_purpose_records.filter(
                licence_category_id=licence_category
            )
            if not only_purpose_records:
                queryset = LicenceCategory.objects.none()
            else:
                queryset = queryset.filter(id=licence_category)

        serializer = LicenceCategorySerializer(queryset, many=True, context={
            'request': request,
            'purpose_records': only_purpose_records
        })
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super(UserAvailableWildlifeLicencePurposesViewSet, self).get_serializer_context()
        context.update({
            "test": 'test context'
        })
        return context
