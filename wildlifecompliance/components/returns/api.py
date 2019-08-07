import traceback
from datetime import datetime, timedelta
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
from ledger.checkout.utils import calculate_excl_gst
from rest_framework import viewsets, serializers, status, views
from rest_framework.decorators import detail_route, list_route, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.returns.utils import SpreadSheet
from wildlifecompliance.components.licences.models import (
    WildlifeLicence
)
from wildlifecompliance.components.returns.models import (
    Return,
    ReturnType,
)
from wildlifecompliance.components.returns.serializers import (
    ReturnSerializer,
    ReturnActionSerializer,
    ReturnLogEntrySerializer,
    ReturnTypeSerializer,
    ReturnRequestSerializer,
)
from wildlifecompliance.components.main.utils import (
    checkout,
)
from wildlifecompliance.components.applications.models import (
    Application,
    ReturnRequest,
)

from wildlifecompliance.components.returns.email import (
    send_return_amendment_email_notification,
)

from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer


class ReturnFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """
    def filter_queryset(self, request, queryset, view):

        # Get built-in DRF datatables queryset first to join with search text, then apply additional filters
        super_queryset = super(ReturnFilterBackend, self).filter_queryset(request, queryset, view).distinct()

        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        status = request.GET.get('status')
        queryset = super_queryset

        if queryset.model is Return:

            # apply user selected filters
            status = status.lower() if status else 'all'
            if status != 'all':
                status_ids = []
                for returns in queryset:
                    if status in returns.processing_status.lower():
                        status_ids.append(returns.id)
                queryset = queryset.filter(id__in=status_ids).distinct()
            if date_from:
                date_from = datetime.strptime(date_from, '%Y-%m-%d') + timedelta(days=1)
                queryset = queryset.filter(lodgement_date__gte=date_from)
            if date_to:
                date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                queryset = queryset.filter(lodgement_date__lte=date_to)

        return queryset


class ReturnRenderer(DatatablesRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'view' in renderer_context and hasattr(renderer_context['view'], '_datatables_total_count'):
            data['recordsTotal'] = renderer_context['view']._datatables_total_count
        return super(ReturnRenderer, self).render(data, accepted_media_type, renderer_context)


class ReturnPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ReturnFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ReturnRenderer,)
    queryset = Return.objects.none()
    serializer_class = ReturnSerializer
    page_size = 10

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Return.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            user_licences = [wildlifelicence.id for wildlifelicence in WildlifeLicence.objects.filter(
                Q(current_application__org_applicant_id__in=user_orgs) |
                Q(current_application__proxy_applicant=user) |
                Q(current_application__submitter=user))]
            return Return.objects.filter(Q(licence_id__in=user_licences))
        return Return.objects.none()

    @list_route(methods=['GET', ])
    def user_datatable_list(self, request, *args, **kwargs):
        self.serializer_class = ReturnSerializer
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
        serializer = ReturnSerializer(result_page, context={'request': request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class ReturnViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReturnSerializer
    queryset = Return.objects.all()

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Return.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            user_licences = [wildlifelicence.id for wildlifelicence in WildlifeLicence.objects.filter(
                Q(current_application__org_applicant_id__in=user_orgs) |
                Q(current_application__proxy_applicant=user) |
                Q(current_application__submitter=user))]
            return Return.objects.filter(Q(licence_id__in=user_licences))
        return Return.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by org
        org_id = request.GET.get('org_id', None)
        if org_id:
            queryset = queryset.filter(application__org_applicant_id=org_id)
        # Filter by proxy_applicant
        proxy_applicant_id = request.GET.get('proxy_applicant_id', None)
        if proxy_applicant_id:
            queryset = queryset.filter(application__proxy_applicant_id=proxy_applicant_id)
        # Filter by submitter
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            queryset = queryset.filter(application__submitter_id=submitter_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET', ])
    def user_list(self, request, *args, **kwargs):
        qs = self.get_queryset().exclude(processing_status=Return.RETURN_PROCESSING_STATUS_FUTURE)

        serializer = ReturnSerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET', ])
    def accept(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept(request)
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
    def upload_details(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance.has_data:
                return Response(
                        {'error': 'Upload not applicable for Return Type.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            spreadsheet = SpreadSheet(instance, request.FILES['spreadsheet']).factory()
            if not spreadsheet.is_valid():
                return Response(
                        {'error': 'Enter data in correct format.'}, status=status.HTTP_404_NOT_FOUND)
            table = instance.data.build_table(spreadsheet.rows_list)

            return Response(table)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @list_route(methods=['GET', ])
    def sheet_details(self, request, *args, **kwargs):
        return_id = self.request.query_params.get('return_id')
        species_id = self.request.query_params.get('species_id')
        instance = Return.objects.get(id=return_id).sheet
        instance.set_species(species_id)
        return Response(instance.table)

    @detail_route(methods=['POST', ])
    def sheet_check_transfer(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            if not instance.sheet.is_valid_transfer(request):
                raise ValidationError({'err': 'Transfer not valid.'})

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
    def sheet_pay_transfer(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
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

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def return_fee_checkout(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            product_lines = []
            return_submission = u'Return submitted by {} confirmation {}'.format(
                 u'{} {}'.format(instance.submitter.first_name, instance.submitter.last_name),
                 instance.lodgement_number)
            product_lines.append({
                    'ledger_description': '{}'.format(instance.return_type.description),
                    'quantity': 1,
                    'price_incl_tax': str(instance.return_fee),
                    'price_excl_tax': str(calculate_excl_gst(instance.return_fee)),
                    'oracle_code': ''
            })
            checkout_result = checkout(request, instance, lines=product_lines,
                                       invoice_text=return_submission)
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
    def save(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            if instance.has_data:
                instance.data.store(request)

            if instance.has_sheet:
                instance.sheet.store(request)

            if instance.has_question:
                instance.question.store(request)

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

    @detail_route(methods=['POST', ])
    def submit(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.set_submitted(request)
            instance.submitter = request.user
            instance.save()
            serializer = self.get_serializer(instance)
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
    def discard(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
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
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = ReturnLogEntrySerializer(qs, many=True)
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
                request.data['compliance'] = u'{}'.format(instance.id)
                request.data['staff'] = u'{}'.format(request.user.id)
                serializer = ReturnLogEntrySerializer(data=request.data)
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
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ReturnActionSerializer(qs, many=True)
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


class ReturnTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReturnTypeSerializer
    queryset = ReturnType.objects.none()

    def get_queryset(self):
        if is_internal(self.request):
            return ReturnType.objects.all()
        return ReturnType.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReturnAmendmentRequestViewSet(viewsets.ModelViewSet):
    queryset = ReturnRequest.objects.all()
    serializer_class = ReturnRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ReturnRequest.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            user_applications = [application.id for application in Application.objects.filter(
                Q(org_applicant_id__in=user_orgs) | Q(proxy_applicant=user) | Q(submitter=user))]
            return ReturnRequest.objects.filter(
                Q(application_id__in=user_applications))
        return ReturnRequest.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            amend_data = self.request.data
            reason = amend_data.pop('reason')
            a_return = amend_data.pop('a_return')
            text = amend_data.pop('text')

            returns = Return.objects.get(id=a_return['id'])
            application = a_return['application']
            licence = a_return['licence']
            assigned_to = a_return['assigned_to']
            data = {
                    'application': application,
                    'reason': reason,
                    'text': text,
                    'officer': assigned_to
            }

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            # send email
            send_return_amendment_email_notification(
                request, data, returns, licence)
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


class ReturnAmendmentRequestReasonChoicesView(views.APIView):

    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        choices_list = []
        choices = ReturnRequest.REASON_CHOICES
        if choices:
            for c in choices:
                choices_list.append({'key': c[0], 'value': c[1]})

        return Response(choices_list)