import traceback
import os
from datetime import datetime, timedelta
from django.db.models import Q
from django.db import transaction
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from rest_framework import viewsets, serializers, status, views
from rest_framework.decorators import detail_route, list_route, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from ledger.accounts.models import EmailUser
from ledger.checkout.utils import calculate_excl_gst
from django.urls import reverse
from django.shortcuts import redirect
from wildlifecompliance.components.applications.utils import (
    SchemaParser,
    MissingFieldsException,
)
from wildlifecompliance.components.main.utils import checkout, set_session_application, delete_session_application
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.applications.models import (
    Application,
    ApplicationSelectedActivity,
    ApplicationCondition,
    ApplicationStandardCondition,
    Assessment,
    ActivityPermissionGroup,
    AmendmentRequest,
    ApplicationUserAction,
    ApplicationFormDataRecord,
)
from wildlifecompliance.components.applications.serializers import (
    ApplicationSerializer,
    InternalApplicationSerializer,
    SaveApplicationSerializer,
    BaseApplicationSerializer,
    CreateExternalApplicationSerializer,
    DTInternalApplicationSerializer,
    DTExternalApplicationSerializer,
    ApplicationUserActionSerializer,
    ApplicationLogEntrySerializer,
    ApplicationConditionSerializer,
    ApplicationStandardConditionSerializer,
    ProposedLicenceSerializer,
    ProposedDeclineSerializer,
    AssessmentSerializer,
    ActivityPermissionGroupSerializer,
    SaveAssessmentSerializer,
    SimpleSaveAssessmentSerializer,
    AmendmentRequestSerializer,
    ApplicationProposedIssueSerializer,
    DTAssessmentSerializer,
)

from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer


class GetEmptyList(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        return Response([])


class ApplicationFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """
    def filter_queryset(self, request, queryset, view):

        # Get built-in DRF datatables queryset first to join with search text, then apply additional filters
        super_queryset = super(ApplicationFilterBackend, self).filter_queryset(request, queryset, view).distinct()

        total_count = queryset.count()
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        category_name = request.GET.get('category_name')
        processing_status = request.GET.get('processing_status')
        customer_status = request.GET.get('customer_status')
        status_filter = request.GET.get('status')
        submitter = request.GET.get('submitter')
        search_text = request.GET.get('search[value]')

        if queryset.model is Application:
            # search_text filter, join all custom search columns
            # where ('searchable: false' in the datatable defintion)
            if search_text:
                search_text = search_text.lower()
                # join queries for the search_text search
                search_text_app_ids = []
                for application in queryset:
                    if (search_text in application.licence_category.lower()
                        or search_text in application.licence_purpose_names.lower()
                        or search_text in application.applicant.lower()
                        or search_text in application.processing_status.lower()
                        or search_text in application.customer_status.lower()
                        or search_text in application.payment_status.lower()
                    ):
                        search_text_app_ids.append(application.id)
                    # if applicant is not an organisation, also search against the user's email address
                    if (application.applicant_type == Application.APPLICANT_TYPE_PROXY and
                        search_text in application.proxy_applicant.email.lower()):
                            search_text_app_ids.append(application.id)
                    if (application.applicant_type == Application.APPLICANT_TYPE_SUBMITTER and
                        search_text in application.submitter.email.lower()):
                            search_text_app_ids.append(application.id)
                # use pipe to join both custom and built-in DRF datatables querysets (returned by super call above)
                # (otherwise they will filter on top of each other)
                queryset = queryset.filter(id__in=search_text_app_ids).distinct() | super_queryset

            # apply user selected filters
            category_name = category_name.lower() if category_name else 'all'
            if category_name != 'all':
                category_name_app_ids = []
                for application in queryset:
                    if category_name in application.licence_category_name.lower():
                        category_name_app_ids.append(application.id)
                queryset = queryset.filter(id__in=category_name_app_ids)
            processing_status = processing_status.lower() if processing_status else 'all'
            if processing_status != 'all':
                processing_status_app_ids = []
                for application in queryset:
                    if processing_status in application.processing_status.lower():
                        processing_status_app_ids.append(application.id)
                queryset = queryset.filter(id__in=processing_status_app_ids)
            customer_status = customer_status.lower() if customer_status else 'all'
            if customer_status != 'all':
                customer_status_app_ids = []
                for application in queryset:
                    if customer_status in application.customer_status.lower():
                        customer_status_app_ids.append(application.id)
                queryset = queryset.filter(id__in=customer_status_app_ids)
            if date_from:
                queryset = queryset.filter(lodgement_date__gte=date_from)
            if date_to:
                date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                queryset = queryset.filter(lodgement_date__lte=date_to)
            submitter = submitter.lower() if submitter else 'all'
            if submitter != 'all':
                queryset = queryset.filter(submitter__email__iexact=submitter)

        if queryset.model is Assessment:
            # search_text filter, join all custom search columns
            # where ('searchable: false' in the datatable definition)
            if search_text:
                search_text = search_text.lower()
                # join queries for the search_text search
                search_text_ass_ids = []
                for assessment in queryset:
                    if (search_text in assessment.application.licence_category.lower()
                        or search_text in assessment.licence_activity.short_name.lower()
                        or search_text in assessment.application.applicant.lower()
                        or search_text in assessment.get_status_display().lower()
                    ):
                        search_text_ass_ids.append(assessment.id)
                    # if applicant is not an organisation, also search against the user's email address
                    if (assessment.application.applicant_type == Application.APPLICANT_TYPE_PROXY and
                        search_text in assessment.application.proxy_applicant.email.lower()):
                            search_text_ass_ids.append(assessment.id)
                    if (assessment.application.applicant_type == Application.APPLICANT_TYPE_SUBMITTER and
                        search_text in assessment.application.submitter.email.lower()):
                            search_text_ass_ids.append(assessment.id)
                # use pipe to join both custom and built-in DRF datatables querysets (returned by super call above)
                # (otherwise they will filter on top of each other)
                queryset = queryset.filter(id__in=search_text_ass_ids).distinct() | super_queryset

            # apply user selected filters
            category_name = category_name.lower() if category_name else 'all'
            if category_name != 'all':
                category_name_app_ids = []
                for assessment in queryset:
                    if category_name in assessment.application.licence_category_name.lower():
                        category_name_app_ids.append(assessment.id)
                queryset = queryset.filter(id__in=category_name_app_ids)
            status_filter = status_filter.lower() if status_filter else 'all'
            if status_filter != 'all':
                queryset = queryset.filter(status=status_filter)
            if date_from:
                queryset = queryset.filter(application__lodgement_date__gte=date_from)
            if date_to:
                date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                queryset = queryset.filter(application__lodgement_date__lte=date_to)
            submitter = submitter.lower() if submitter else 'all'
            if submitter != 'all':
                queryset = queryset.filter(application__submitter__email__iexact=submitter)

        # override queryset ordering, required because the ordering is usually handled
        # in the super call, but is then clobbered by the custom queryset joining above
        # also needed to disable ordering for all fields for which data is not an
        # Application model field, as property functions will not work with order_by
        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        setattr(view, '_datatables_total_count', total_count)
        return queryset


class ApplicationRenderer(DatatablesRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'view' in renderer_context and hasattr(renderer_context['view'], '_datatables_total_count'):
            data['recordsTotal'] = renderer_context['view']._datatables_total_count
        return super(ApplicationRenderer, self).render(data, accepted_media_type, renderer_context)


class ApplicationPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ApplicationFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ApplicationRenderer,)
    queryset = Application.objects.none()
    serializer_class = DTExternalApplicationSerializer
    page_size = 10

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Application.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            return Application.objects.filter(Q(org_applicant_id__in=user_orgs) | Q(
                proxy_applicant=user) | Q(submitter=user))
        return Application.objects.none()

    @list_route(methods=['GET', ])
    def internal_datatable_list(self, request, *args, **kwargs):
        self.serializer_class = DTInternalApplicationSerializer
        queryset = self.get_queryset()
        # Filter by org
        org_id = request.GET.get('org_id', None)
        if org_id:
            queryset = queryset.filter(org_applicant_id=org_id)
        # Filter by proxy_applicant
        proxy_applicant_id = request.GET.get('proxy_applicant_id', None)
        if proxy_applicant_id:
            queryset = queryset.filter(proxy_applicant_id=proxy_applicant_id)
        # Filter by submitter
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            queryset = queryset.filter(submitter_id=submitter_id)
        # Filter by user (submitter or proxy_applicant)
        user_id = request.GET.get('user_id', None)
        if user_id:
            queryset = Application.objects.filter(
                Q(proxy_applicant=user_id) |
                Q(submitter=user_id)
            )
        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTInternalApplicationSerializer(result_page, context={'request': request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    @list_route(methods=['GET', ])
    def external_datatable_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by org
        org_id = request.GET.get('org_id', None)
        if org_id:
            queryset = queryset.filter(org_applicant_id=org_id)
        # Filter by proxy_applicant
        proxy_applicant_id = request.GET.get('proxy_applicant_id', None)
        if proxy_applicant_id:
            queryset = queryset.filter(proxy_applicant_id=proxy_applicant_id)
        # Filter by submitter
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            queryset = queryset.filter(submitter_id=submitter_id)
        self.serializer_class = DTExternalApplicationSerializer
        user_orgs = [
            org.id for org in request.user.wildlifecompliance_organisations.all()]
        queryset = self.get_queryset().filter(
            Q(submitter=request.user) |
            Q(proxy_applicant=request.user) |
            Q(org_applicant_id__in=user_orgs)
        ).computed_exclude(
            processing_status=Application.PROCESSING_STATUS_DISCARDED
        ).distinct()
        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTExternalApplicationSerializer(result_page, context={'request': request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Application.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            return Application.objects.filter(Q(org_applicant_id__in=user_orgs) | Q(
                proxy_applicant=user) | Q(submitter=user))
        return Application.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = BaseApplicationSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def process_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            action = request.POST.get('action')
            section = request.POST.get('input_name')
            if action == 'list' and 'input_name' in request.POST:
                pass

            elif action == 'delete' and 'document_id' in request.POST:
                document_id = request.POST.get('document_id')
                document = instance.documents.get(id=document_id)

                if document._file and os.path.isfile(
                        document._file.path) and document.can_delete:
                    os.remove(document._file.path)

                document.delete()
                instance.save(version_comment='Approval File Deleted: {}'.format(
                    document.name))  # to allow revision to be added to reversion history

            elif action == 'save' and 'input_name' in request.POST and 'filename' in request.POST:
                application_id = request.POST.get('application_id')
                filename = request.POST.get('filename')
                _file = request.POST.get('_file')
                if not _file:
                    _file = request.FILES.get('_file')

                document = instance.documents.get_or_create(
                    input_name=section, name=filename)[0]
                path = default_storage.save(
                    'applications/{}/documents/{}'.format(
                        application_id, filename), ContentFile(
                        _file.read()))

                document._file = path
                document.save()
                # to allow revision to be added to reversion history
                instance.save(
                    version_comment='File Added: {}'.format(filename))

            return Response(
                [
                    dict(
                        input_name=d.input_name,
                        name=d.name,
                        file=d._file.url,
                        id=d.id,
                        can_delete=d.can_delete) for d in instance.documents.filter(
                        input_name=section) if d._file])

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

    @detail_route(methods=['GET', ])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ApplicationUserActionSerializer(qs, many=True)
            return Response(serializer.data)
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
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = ApplicationLogEntrySerializer(qs, many=True)
            return Response(serializer.data)
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
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                request.data['application'] = u'{}'.format(instance.id)
                request.data['staff'] = u'{}'.format(request.user.id)
                serializer = ApplicationLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents

                return Response(serializer.data)
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
    def conditions(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.conditions.all()
            licence_activity = self.request.query_params.get(
                'licence_activity', None)
            if licence_activity is not None:
                qs = qs.filter(licence_activity=licence_activity)
            serializer = ApplicationConditionSerializer(qs, many=True)
            return Response(serializer.data)
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
    def assessments(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.assessments
            serializer = AssessmentSerializer(qs, many=True)
            print(qs)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @list_route(methods=['POST', ])
    def estimate_price(self, request, *args, **kwargs):
        purpose_ids = request.data.get('purpose_ids', [])
        application_id = request.data.get('application_id')
        if application_id is not None:
            application = Application.objects.get(id=application_id)
            return Response({
                'fees': application.calculate_fees(request.data.get('field_data', {}))
            })
        return Response({
            'fees': Application.calculate_base_fees(purpose_ids)
        })

    @list_route(methods=['GET', ])
    def internal_datatable_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = DTInternalApplicationSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['GET', ])
    def user_list(self, request, *args, **kwargs):
        user_orgs = [
            org.id for org in request.user.wildlifecompliance_organisations.all()]

        queryset = self.get_queryset().filter(
            Q(submitter=request.user) |
            Q(proxy_applicant=request.user) |
            Q(org_applicant_id__in=user_orgs)
        ).computed_exclude(
            processing_status=Application.PROCESSING_STATUS_DISCARDED
        ).distinct()

        serializer = DTExternalApplicationSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['GET', ])
    def internal_application(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = InternalApplicationSerializer(
            instance, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def submit(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            try:
                instance.submit(request, self)
            except MissingFieldsException as e:
                return Response({
                    'missing': e.error_list},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            delete_session_application(request.session)
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            delete_session_application(request.session)
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def application_fee_checkout(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            product_lines = []
            application_submission = u'Application submitted by {} confirmation {}'.format(
                u'{} {}'.format(instance.submitter.first_name, instance.submitter.last_name), instance.lodgement_number)
            set_session_application(request.session, instance)
            product_lines.append({
                'ledger_description': '{}'.format(instance.licence_type_name),
                'quantity': 1,
                'price_incl_tax': str(instance.application_fee),
                'price_excl_tax': str(calculate_excl_gst(instance.application_fee)),
                'oracle_code': ''
            })
            checkout_result = checkout(request, instance, lines=product_lines,
                                       invoice_text=application_submission)
            return checkout_result
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

    @detail_route(methods=['POST', ])
    def accept_id_check(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept_id_check(request)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
            return Response(serializer.data)
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
    def reset_id_check(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.reset_id_check(request)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
            return Response(serializer.data)
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
    def request_id_check(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.request_id_check(request)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
            return Response(serializer.data)
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
    def accept_character_check(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept_character_check(request)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
            return Response(serializer.data)
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
    def assign_to_me(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user = request.user
            if user not in instance.licence_officers:
                raise serializers.ValidationError(
                    'You are not in any relevant licence officer groups for this application.')
            instance.assign_officer(request, request.user)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
            return Response(serializer.data)
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
    def assign_officer(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get('officer_id', None)
            user = None
            if not user_id:
                raise serializers.ValidationError('An officer id is required')
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise serializers.ValidationError(
                    'A user with the id passed in does not exist')
            if not request.user.has_perm('wildlifecompliance.licensing_officer'):
                raise serializers.ValidationError(
                    'You are not authorised to assign officers to applications')
            if user not in instance.licence_officers:
                raise serializers.ValidationError(
                    'User is not in any relevant licence officer groups for this application')
            instance.assign_officer(request, user)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
            return Response(serializer.data)
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
    def unassign_officer(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.unassign_officer(request)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
            return Response(serializer.data)
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
    def return_to_officer(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
            activity_id = request.data.get('activity_id')
            if not activity_id:
                raise serializers.ValidationError(
                    'Activity ID is required!')

            instance.return_to_officer_conditions(request, activity_id)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
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

    @detail_route(methods=['POST', ])
    def update_activity_status(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
            activity_id = request.data.get('activity_id')
            status = request.data.get('status')
            if not status or not activity_id:
                raise serializers.ValidationError(
                    'Status and activity id is required')
            else:
                if not ApplicationSelectedActivity.is_valid_status(status):
                    raise serializers.ValidationError(
                        'The status provided is not allowed')
            instance.set_activity_processing_status(activity_id, status)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
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

    @detail_route(methods=['POST', ])
    def complete_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.complete_assessment(request)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
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

    @detail_route(methods=['POST', ])
    def proposed_licence(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ProposedLicenceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.proposed_licence(request, serializer.validated_data)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
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

    @detail_route(methods=['GET', ])
    def get_proposed_decisions(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.get_proposed_decisions(request)
            # qs = instance.decisions.filter(action='propose_issue')
            # print(qs)
            serializer = ApplicationProposedIssueSerializer(qs, many=True)
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

    @detail_route(methods=['POST', ])
    def final_decision(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.final_decision(request)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
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

    @detail_route(methods=['POST', ])
    def proposed_decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ProposedDeclineSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.proposed_decline(request, serializer.validated_data)
            serializer = InternalApplicationSerializer(
                instance, context={'request': request})
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

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def draft(self, request, *args, **kwargs):
        parser = SchemaParser(draft=True)
        try:
            instance = self.get_object()
            parser.save_application_user_data(instance, request, self)
            return redirect(reverse('external'))
        except MissingFieldsException as e:
            return Response({
                'missing': e.error_list},
                status=status.HTTP_400_BAD_REQUEST
            )
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
        raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def officer_comments(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            ApplicationFormDataRecord.process_form(
                request,
                instance,
                request.data,
                action=ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_COMMENT
            )
            return Response({'success': True})
        except Exception as e:
            print(traceback.print_exc())
        raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def form_data(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            ApplicationFormDataRecord.process_form(
                request,
                instance,
                request.data,
                action=ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_VALUE
            )
            return Response({'success': True})
        except MissingFieldsException as e:
            return Response({
                'missing': e.error_list},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
        raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def application_officer_save(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            parser = SchemaParser()
            parser.save_application_officer_data(instance, request, self)
            return redirect(reverse('external'))
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    # @detail_route(methods=['post'])
    # @renderer_classes((JSONRenderer,))
    # def assess_save(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         save_assess_data(instance, request, self)
    #         return redirect(reverse('external'))
    #     except serializers.ValidationError:
    #         print(traceback.print_exc())
    #         raise
    #     except ValidationError as e:
    #         raise serializers.ValidationError(repr(e.error_dict))
    #     except Exception as e:
    #         print(traceback.print_exc())
    #         raise serializers.ValidationError(str(e))

    @renderer_classes((JSONRenderer,))
    def create(self, request, *args, **kwargs):
        try:
            app_data = self.request.data
            licence_category_data = app_data.get('licence_category_data')
            org_applicant = request.data.get('org_applicant')
            proxy_applicant = request.data.get('proxy_applicant')
            licence_purposes = request.data.get('licence_purposes')
            data = {
                'submitter': request.user.id,
                'licence_type_data': licence_category_data,
                'org_applicant': org_applicant,
                'proxy_applicant': proxy_applicant,
                'licence_purposes': licence_purposes,
            }

            # Use serializer for external application creation - do not expose unneeded fields
            serializer = CreateExternalApplicationSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer.instance.update_dynamic_attributes()

            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SaveApplicationSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def destroy(self, request, *args, **kwargs):
        http_status = status.HTTP_200_OK
        instance = self.get_object()
        if instance.processing_status != Application.PROCESSING_STATUS_DRAFT:
            raise serializers.ValidationError(
                'You cannot discard a submitted application!')

        instance.activities.filter(
            processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_DRAFT
        ).update(
            processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_DISCARDED
        )

        return Response({'processing_status': ApplicationSelectedActivity.PROCESSING_STATUS_DISCARDED
                         }, status=http_status)

    @detail_route(methods=['DELETE', ])
    def discard_activity(self, request, *args, **kwargs):
        http_status = status.HTTP_200_OK
        activity_id = request.GET.get('activity_id')
        instance = self.get_object()

        try:
            activity = instance.activities.get(
                licence_activity_id=activity_id,
                processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_DRAFT
            )
        except ApplicationSelectedActivity.DoesNotExist:
            raise serializers.ValidationError("This activity cannot be discarded at this time.")

        activity.processing_status = ApplicationSelectedActivity.PROCESSING_STATUS_DISCARDED
        activity.save()

        return Response({'processing_status': instance.processing_status}, status=http_status)

    @detail_route(methods=['GET', ])
    def assessment_details(self, request, *args, **kwargs):
        # queryset = self.get_queryset()
        instance = self.get_object()
        queryset = Assessment.objects.filter(application=instance.id)
        licence_activity = self.request.query_params.get(
            'licence_activity', None)
        if licence_activity is not None:
            queryset = queryset.filter(
                licence_activity=licence_activity)
        serializer = AssessmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(permission_classes=[], methods=['GET'])
    def application_checkout_status(self, request, *args, **kwargs):
        # TODO: may need to re-build this function for Wildlife Licensing (code taken from Parkstay) if required
        try:
            # instance = self.get_object()
            response = {
                'status': 'rejected',
                'error': ''
            }
            # # Check the type of booking
            # if instance.booking_type != 3:
            #    response['error'] = 'This booking has already been paid for'
            #    return Response(response,status=status.HTTP_200_OK)
            # # Check if the time for the booking has elapsed
            # if instance.expiry_time <= timezone.now():
            #     response['error'] = 'This booking has expired'
            #     return Response(response,status=status.HTTP_200_OK)
            # if all is well
            response['status'] = 'approved'
            return Response(response, status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ApplicationConditionViewSet(viewsets.ModelViewSet):
    queryset = ApplicationCondition.objects.all()
    serializer_class = ApplicationConditionSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ApplicationCondition.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            user_applications = [application.id for application in Application.objects.filter(
                Q(org_applicant_id__in=user_orgs) | Q(proxy_applicant=user) | Q(submitter=user))]
            return ApplicationCondition.objects.filter(
                Q(application_id__in=user_applications))
        return ApplicationCondition.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                instance = serializer.save()
                instance.submit()
                instance.application.log_user_action(
                    ApplicationUserAction.ACTION_ENTER_CONDITIONS.format(
                        instance.licence_activity.name), request)
            return Response(serializer.data)
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
    def move_up(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.up()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
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
    def move_down(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.down()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ApplicationStandardConditionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApplicationStandardCondition.objects.all()
    serializer_class = ApplicationStandardConditionSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return ApplicationStandardCondition.objects.all()
        elif is_customer(self.request):
            return ApplicationStandardCondition.objects.none()
        return ApplicationStandardCondition.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AssessmentPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ApplicationFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ApplicationRenderer,)
    queryset = Assessment.objects.none()
    serializer_class = DTAssessmentSerializer
    page_size = 10

    def get_queryset(self):
        if is_internal(self.request):
            return Assessment.objects.all()
        elif is_customer(self.request):
            return Assessment.objects.none()
        return Assessment.objects.none()

    @list_route(methods=['GET', ])
    def datatable_list(self, request, *args, **kwargs):
        self.serializer_class = DTAssessmentSerializer
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = DTAssessmentSerializer(result_page, context={'request': request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Assessment.objects.all()
        elif is_customer(self.request):
            return Assessment.objects.none()
        return Assessment.objects.none()

    @list_route(methods=['GET', ])
    def get_latest_for_application_activity(self, request, *args, **kwargs):
        application_id = request.query_params.get(
            'application_id', None)
        activity_id = request.query_params.get(
            'activity_id', None)
        latest_assessment = Assessment.objects.filter(
            application_id=application_id,
            licence_activity_id=activity_id
        ).exclude(
            status='recalled'
        ).latest('id')
        serializer = AssessmentSerializer(latest_assessment)
        return Response(serializer.data)

    @list_route(methods=['GET', ])
    def user_list(self, request, *args, **kwargs):
        # Get the assessor groups the current user is member of
        assessor_groups = request.user.get_wildlifelicence_permission_group('assessor', first=False)

        # For each assessor groups get the assessments
        queryset = self.get_queryset().none()
        for group in assessor_groups:
            queryset = queryset | Assessment.objects.filter(
                assessor_group=group)

        serializer = DTAssessmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @renderer_classes((JSONRenderer,))
    def create(self, request, *args, **kwargs):
        try:
            serializer = SaveAssessmentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            instance.generate_assessment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                print e
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def remind_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.remind_assessment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
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
    def recall_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.recall_assessment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
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
    def resend_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.resend_assessment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['PUT', ])
    def update_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SimpleSaveAssessmentSerializer(instance, data=self.request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                print e
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class AssessorGroupViewSet(viewsets.ModelViewSet):
    queryset = ActivityPermissionGroup.objects.none()
    serializer_class = ActivityPermissionGroupSerializer
    renderer_classes = [JSONRenderer, ]

    def get_queryset(self, application=None):
        if is_internal(self.request):
            if application is not None:
                return application.get_permission_groups('assessor')
            return ActivityPermissionGroup.objects.filter(
                permissions__codename='assessor'
            )
        elif is_customer(self.request):
            return ActivityPermissionGroup.objects.none()
        return ActivityPermissionGroup.objects.none()

    @list_route(methods=['POST', ])
    def user_list(self, request, *args, **kwargs):
        app_id = request.data.get('application_id')
        application = Application.objects.get(id=app_id)
        id_list = set()
        for assessment in application.assessments:
            id_list.add(assessment.assessor_group.id)
        queryset = self.get_queryset(application).exclude(id__in=id_list)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class AmendmentRequestViewSet(viewsets.ModelViewSet):
    queryset = AmendmentRequest.objects.all()
    serializer_class = AmendmentRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return AmendmentRequest.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            user_applications = [application.id for application in Application.objects.filter(
                Q(org_applicant_id__in=user_orgs) | Q(proxy_applicant=user) | Q(submitter=user))]
            return AmendmentRequest.objects.filter(
                Q(application_id__in=user_applications))
        return AmendmentRequest.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            # print(request.data)
            amend_data = self.request.data
            reason = amend_data.pop('reason')
            application_id = amend_data.pop('application')
            text = amend_data.pop('text')
            activity_id = amend_data.pop('activity_id')
            for item in activity_id:
                data = {
                    'application': application_id,
                    'reason': reason,
                    'text': text,
                    'licence_activity': item
                }

                application = Application.objects.get(id=application_id)
                selected_activity = application.get_selected_activity(item)
                if selected_activity.processing_status == ApplicationSelectedActivity.PROCESSING_STATUS_DISCARDED:
                    raise serializers.ValidationError('Selected activity has been discarded by the customer!')

                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                instance.reason = reason
                instance.generate_amendment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                print e
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class AmendmentRequestReasonChoicesView(views.APIView):

    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        choices_list = []
        choices = AmendmentRequest.REASON_CHOICES
        if choices:
            for c in choices:
                choices_list.append({'key': c[0], 'value': c[1]})

        return Response(choices_list)
