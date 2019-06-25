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
    LicenceCategory,
    LicencePurpose
)
from wildlifecompliance.components.applications.serializers import (
    ExternalApplicationSelectedActivitySerializer
)
from wildlifecompliance.components.licences.serializers import (
    WildlifeLicenceSerializer,
    LicenceCategorySerializer,
    DTInternalWildlifeLicenceSerializer,
    DTExternalWildlifeLicenceSerializer,
    BasePurposeSerializer
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
        # Filter for WildlifeLicence objects that have a current application linked with an
        # ApplicationSelectedActivity that has been ACCEPTED
        asa_accepted = ApplicationSelectedActivity.objects.filter(
            processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED)
        if is_internal(self.request):
            return WildlifeLicence.objects.filter(
                current_application__in=asa_accepted.values_list('application_id', flat=True))
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            return WildlifeLicence.objects.filter(
                Q(current_application__org_applicant_id__in=user_orgs) |
                Q(current_application__proxy_applicant=user) |
                Q(current_application__submitter=user)
            ).filter(current_application__in=asa_accepted.values_list('application_id', flat=True))
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
        # Filter for WildlifeLicence objects that have a current application linked with an
        # ApplicationSelectedActivity that has been ACCEPTED
        asa_accepted = ApplicationSelectedActivity.objects.filter(
            processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED)
        user_orgs = [
            org.id for org in request.user.wildlifecompliance_organisations.all()]
        queryset = WildlifeLicence.objects.filter(
            Q(current_application__org_applicant_id__in=user_orgs) |
            Q(current_application__proxy_applicant=request.user) |
            Q(current_application__submitter=request.user)
        ).filter(current_application__in=asa_accepted.values_list('application_id', flat=True))
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
        # Filter for WildlifeLicence objects that have a current application linked with an
        # ApplicationSelectedActivity that has been ACCEPTED
        asa_accepted = ApplicationSelectedActivity.objects.filter(
            processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED)
        if is_internal(self.request):
            return WildlifeLicence.objects.filter(
                current_application__in=asa_accepted.values_list('application_id', flat=True))
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            return WildlifeLicence.objects.filter(
                Q(current_application__org_applicant_id__in=user_orgs) |
                Q(current_application__proxy_applicant=user) |
                Q(current_application__submitter=user)
            ).filter(current_application__in=asa_accepted.values_list('application_id', flat=True))
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
    def reactivate_renew_purposes(self, request, pk=None, *args, **kwargs):
        try:
            purpose_ids_list = request.data.get('purpose_ids_list', None)
            if not type(purpose_ids_list) == list:
                raise serializers.ValidationError(
                    'Purpose IDs must be a list')
            if not request.user.has_perm('wildlifecompliance.issuing_officer'):
                raise serializers.ValidationError(
                    'You are not authorised to reactivate renew for licenced activities')
            if LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                    values_list('licence_activity_id',flat=True).\
                    distinct().count() != 1:
                raise serializers.ValidationError(
                    'Selected purposes must all be of the same licence activity')
            if purpose_ids_list and pk:
                licence_activity_id = LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                                        first().licence_activity_id
                instance = self.get_object()
                can_reactivate_renew_purposes = instance.get_latest_purposes_for_licence_activity_and_action(
                    licence_activity_id, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW)
                can_reactivate_renew_purposes_ids_list = [purpose.id for purpose in can_reactivate_renew_purposes.order_by('id')]
                if not set(purpose_ids_list).issubset(can_reactivate_renew_purposes_ids_list):
                    raise serializers.ValidationError(
                        'Renew for selected purposes cannot be reactivated')
                instance.apply_action_to_purposes(request, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW)
                serializer = DTExternalWildlifeLicenceSerializer(instance, context={'request': request})
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID and Purpose IDs list must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def surrender_licence(self, request, pk=None, *args, **kwargs):
        try:
            if pk:
                instance = self.get_object()
                instance.apply_action_to_licence(request, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER)
                serializer = DTExternalWildlifeLicenceSerializer(instance, context={'request': request})
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def surrender_purposes(self, request, pk=None, *args, **kwargs):
        try:
            purpose_ids_list = request.data.get('purpose_ids_list', None)
            if not type(purpose_ids_list) == list:
                raise serializers.ValidationError(
                    'Purpose IDs must be a list')
            if LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                    values_list('licence_activity_id',flat=True).\
                    distinct().count() != 1:
                raise serializers.ValidationError(
                    'Selected purposes must all be of the same licence activity')
            if purpose_ids_list and pk:
                licence_activity_id = LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                                        first().licence_activity_id
                instance = self.get_object()
                can_surrender_purposes = instance.get_latest_purposes_for_licence_activity_and_action(
                    licence_activity_id, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER)
                can_surrender_purposes_ids_list = [purpose.id for purpose in can_surrender_purposes.order_by('id')]
                if not set(purpose_ids_list).issubset(can_surrender_purposes_ids_list):
                    raise serializers.ValidationError(
                        'Selected purposes cannot be surrendered')
                instance.apply_action_to_purposes(request, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER)
                serializer = DTExternalWildlifeLicenceSerializer(instance, context={'request': request})
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID and Purpose IDs list must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def cancel_licence(self, request, pk=None, *args, **kwargs):
        try:
            if not request.user.has_perm('wildlifecompliance.issuing_officer'):
                raise serializers.ValidationError(
                    'You are not authorised to cancel licences')
            if pk:
                instance = self.get_object()
                instance.apply_action_to_licence(request, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL)
                serializer = DTExternalWildlifeLicenceSerializer(instance, context={'request': request})
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def cancel_purposes(self, request, pk=None, *args, **kwargs):
        try:
            purpose_ids_list = request.data.get('purpose_ids_list', None)
            if not type(purpose_ids_list) == list:
                raise serializers.ValidationError(
                    'Purpose IDs must be a list')
            if not request.user.has_perm('wildlifecompliance.issuing_officer'):
                raise serializers.ValidationError(
                    'You are not authorised to cancel licenced activities')
            if LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                    values_list('licence_activity_id',flat=True).\
                    distinct().count() != 1:
                raise serializers.ValidationError(
                    'Selected purposes must all be of the same licence activity')
            if purpose_ids_list and pk:
                licence_activity_id = LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                                        first().licence_activity_id
                instance = self.get_object()
                can_cancel_purposes = instance.get_latest_purposes_for_licence_activity_and_action(
                    licence_activity_id, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL)
                can_cancel_purposes_ids_list = [purpose.id for purpose in can_cancel_purposes.order_by('id')]
                if not set(purpose_ids_list).issubset(can_cancel_purposes_ids_list):
                    raise serializers.ValidationError(
                        'Selected purposes cannot be cancelled')
                instance.apply_action_to_purposes(request, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL)
                serializer = DTExternalWildlifeLicenceSerializer(instance, context={'request': request})
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID and Purpose IDs list must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def suspend_licence(self, request, pk=None, *args, **kwargs):
        try:
            if not request.user.has_perm('wildlifecompliance.issuing_officer'):
                raise serializers.ValidationError(
                    'You are not authorised to suspend licences')
            if pk:
                instance = self.get_object()
                instance.apply_action_to_licence(request, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND)
                serializer = DTExternalWildlifeLicenceSerializer(instance, context={'request': request})
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def suspend_purposes(self, request, pk=None, *args, **kwargs):
        try:
            purpose_ids_list = request.data.get('purpose_ids_list', None)
            if not type(purpose_ids_list) == list:
                raise serializers.ValidationError(
                    'Purpose IDs must be a list')
            if not request.user.has_perm('wildlifecompliance.issuing_officer'):
                raise serializers.ValidationError(
                    'You are not authorised to suspend licenced activities')
            if LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                    values_list('licence_activity_id',flat=True).\
                    distinct().count() != 1:
                raise serializers.ValidationError(
                    'Selected purposes must all be of the same licence activity')
            if purpose_ids_list and pk:
                licence_activity_id = LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                                        first().licence_activity_id
                instance = self.get_object()
                can_suspend_purposes = instance.get_latest_purposes_for_licence_activity_and_action(
                    licence_activity_id, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND)
                can_suspend_purposes_ids_list = [purpose.id for purpose in can_suspend_purposes.order_by('id')]
                if not set(purpose_ids_list).issubset(can_suspend_purposes_ids_list):
                    raise serializers.ValidationError(
                        'Selected purposes cannot be suspended')
                instance.apply_action_to_purposes(request, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND)
                serializer = DTExternalWildlifeLicenceSerializer(instance, context={'request': request})
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID and Purpose IDs list must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def reinstate_licence(self, request, pk=None, *args, **kwargs):
        try:
            if not request.user.has_perm('wildlifecompliance.issuing_officer'):
                raise serializers.ValidationError(
                    'You are not authorised to reinstate licences')
            if pk:
                instance = self.get_object()
                instance.apply_action_to_licence(request, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE)
                serializer = DTExternalWildlifeLicenceSerializer(instance, context={'request': request})
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def reinstate_purposes(self, request, pk=None, *args, **kwargs):
        try:
            purpose_ids_list = request.data.get('purpose_ids_list', None)
            if not type(purpose_ids_list) == list:
                raise serializers.ValidationError(
                    'Purpose IDs must be a list')
            if not request.user.has_perm('wildlifecompliance.issuing_officer'):
                raise serializers.ValidationError(
                    'You are not authorised to reinstate licenced activities')
            if LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                    values_list('licence_activity_id',flat=True).\
                    distinct().count() != 1:
                raise serializers.ValidationError(
                    'Selected purposes must all be of the same licence activity')
            if purpose_ids_list and pk:
                licence_activity_id = LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                                        first().licence_activity_id
                instance = self.get_object()
                can_reinstate_purposes = instance.get_latest_purposes_for_licence_activity_and_action(
                    licence_activity_id, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE)
                can_reinstate_purposes_ids_list = [purpose.id for purpose in can_reinstate_purposes.order_by('id')]
                if not set(purpose_ids_list).issubset(can_reinstate_purposes_ids_list):
                    raise serializers.ValidationError(
                        'Selected purposes cannot be reinstated')
                instance.apply_action_to_purposes(request, WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE)
                serializer = DTExternalWildlifeLicenceSerializer(instance, context={'request': request})
                return Response(serializer.data)
            else:
                raise serializers.ValidationError(
                    'Licence ID and Purpose IDs list must be specified')
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET', ])
    def get_latest_purposes_for_licence_activity_and_action(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            licence_activity_id = request.GET.get('licence_activity_id', None)
            action = request.GET.get('action', None)
            if not licence_activity_id or not action:
                raise serializers.ValidationError(
                    'A licence activity ID and action must be specified')
            queryset = instance.get_latest_purposes_for_licence_activity_and_action(licence_activity_id, action)
            serializer = BasePurposeSerializer(queryset, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
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
        available_purpose_records = None
        application_type = request.GET.get('application_type')
        licence_category_id = request.GET.get('licence_category')
        licence_activity_id = request.GET.get('licence_activity')

        active_applications = Application.get_active_licence_applications(request, application_type)
        if not active_applications.count() and application_type == Application.APPLICATION_TYPE_RENEWAL:
            # Do not present with renewal options if no activities are within the renewal period
            queryset = LicenceCategory.objects.none()
            available_purpose_records = LicencePurpose.objects.none()

        elif active_applications.count():
            # Activities relevant to the current application type
            current_activities = Application.get_active_licence_activities(request, application_type)

            if licence_activity_id:
                current_activities = current_activities.filter(licence_activity__id=licence_activity_id)

            active_licence_activity_ids = current_activities.values_list(
                'licence_activity__licence_category_id',
                flat=True
            )

            active_purpose_ids = []
            for selected_activity in current_activities:
                active_purpose_ids.extend([purpose.id for purpose in selected_activity.purposes])

            # Exclude active purposes for New Activity/Purpose or New Licence application types
            if application_type in [
                Application.APPLICATION_TYPE_ACTIVITY,
                Application.APPLICATION_TYPE_NEW_LICENCE,
            ]:
                available_purpose_records = LicencePurpose.objects.exclude(
                    id__in=active_purpose_ids
                )

            # Only include active purposes for Amendment or Renewal application types
            elif application_type in [
                Application.APPLICATION_TYPE_AMENDMENT,
                Application.APPLICATION_TYPE_RENEWAL,
            ]:
                amendable_purpose_ids = active_applications.values_list(
                    'licence_purposes__id',
                    flat=True
                )

                queryset = queryset.filter(id__in=active_licence_activity_ids)
                available_purpose_records = LicencePurpose.objects.filter(
                    id__in=amendable_purpose_ids,
                    licence_activity_id__in=current_activities.values_list(
                        'licence_activity_id', flat=True)
                )

        # Filter by Licence Category ID if specified or
        # return empty queryset if available_purpose_records is empty for the Licence Category ID specified
        if licence_category_id:
            if available_purpose_records:
                available_purpose_records = available_purpose_records.filter(
                    licence_category_id=licence_category_id
                )
                queryset = queryset.filter(id=licence_category_id)
            else:
                queryset = LicenceCategory.objects.none()

        # Filter out LicenceCategory objects that are not linked with available_purpose_records
        queryset = queryset.filter(activity__purpose__in=available_purpose_records).distinct()

        serializer = LicenceCategorySerializer(queryset, many=True, context={
            'request': request,
            'purpose_records': available_purpose_records
        })
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super(UserAvailableWildlifeLicencePurposesViewSet, self).get_serializer_context()
        context.update({
            "test": 'test context'
        })
        return context
