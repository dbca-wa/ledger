import json
import re
import operator
import traceback
import os
import base64
import geojson
from django.db.models import Q, Min, Max
from django.db import transaction
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.conf import settings

from wildlifecompliance import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views, filters
import rest_framework.exceptions as rest_exceptions
from rest_framework.decorators import (
    detail_route,
    list_route,
    renderer_classes,
    parser_classes,
    api_view
)
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from ledger.checkout.utils import calculate_excl_gst
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from wildlifecompliance.components.main.api import save_location, process_generic_document
from wildlifecompliance.components.main.email import prepare_mail
from wildlifecompliance.components.users.api import generate_dummy_email
from wildlifecompliance.components.users.serializers import (
    UserAddressSerializer,
    ComplianceUserDetailsSerializer,
)
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.call_email.models import (
    CallEmail,
    Classification,
    Location,
    ComplianceFormDataRecord,
    ReportType,
    Referrer,
    CallEmailUserAction,
    MapLayer,
    CasePriority,
    #InspectionType,
    # ExternalOrganisation,
    CallEmailLogEntry,
    )
from wildlifecompliance.components.call_email.serializers import (
    CallEmailSerializer,
    ClassificationSerializer,
    ComplianceFormDataRecordSerializer,
    CallEmailLogEntrySerializer,
    LocationSerializer,
    CallEmailUserActionSerializer,
    LocationSerializer,
    ReportTypeSerializer,
    SaveCallEmailSerializer,
    CreateCallEmailSerializer,
    ReportTypeSchemaSerializer,
    ReferrerSerializer,
    LocationSerializerOptimized,
    CallEmailOptimisedSerializer,
    EmailUserSerializer,
    SaveEmailUserSerializer,
    MapLayerSerializer,
    #ComplianceWorkflowLogEntrySerializer,
    CallEmailDatatableSerializer,
    SaveUserAddressSerializer,
    #InspectionTypeSerializer,
    CasePrioritySerializer,
    # ExternalOrganisationSerializer,
    CallEmailAllocatedGroupSerializer,
    UpdateAssignedToIdSerializer
    )
from wildlifecompliance.components.users.models import (
    CompliancePermissionGroup,    
)
from django.contrib.auth.models import Permission, ContentType
from utils import SchemaParser

from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer

from wildlifecompliance.components.call_email.email import send_mail
#from wildlifecompliance.components.inspection.serializers import InspectionTypeSerializer


class CallEmailFilterBackend(DatatablesFilterBackend):

    def filter_queryset(self, request, queryset, view):
        #import ipdb; ipdb.set_trace()
        # Get built-in DRF datatables queryset first to join with search text, then apply additional filters
        # super_queryset = super(CallEmailFilterBackend, self).filter_queryset(request, queryset, view).distinct()

        total_count = queryset.count()
        status_filter = request.GET.get('status_description')
        classification_filter = request.GET.get('classification_description')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        search_text = request.GET.get('search[value]')

        if search_text:
            search_text = search_text.lower()
            search_text_callemail_ids = []
            for call_email in queryset:
                #lodged_on_str = time.strftime('%d/%m/%Y', call_email.lodged_on)
                lodged_on_str = call_email.lodged_on.strftime('%d/%m/%Y')
                if (search_text in (call_email.number.lower() if call_email.number else '')
                    or search_text in (call_email.status.lower() if call_email.status else '')
                    or search_text in (call_email.classification.name.lower() if call_email.classification else '')
                    or search_text in (lodged_on_str.lower() if lodged_on_str else '')
                    or search_text in (call_email.caller.lower() if call_email.caller else '')
                    or search_text in (
                        call_email.assigned_to.first_name.lower() + ' ' + call_email.assigned_to.last_name.lower()
                        if call_email.assigned_to else ''
                        )
                    ):
                    search_text_callemail_ids.append(call_email.id)

            # use pipe to join both custom and built-in DRF datatables querysets (returned by super call above)
            # (otherwise they will filter on top of each other)
            #_queryset = queryset.filter(id__in=search_text_callemail_ids).distinct() | super_queryset
            # BB 20190704 - is super_queryset necessary?
            queryset = queryset.filter(id__in=search_text_callemail_ids)

        status_filter = status_filter.lower() if status_filter else 'all'
        if status_filter != 'all':
            status_filter_callemail_ids = []
            for call_email in queryset:
                if status_filter == call_email.get_status_display().lower():
                    status_filter_callemail_ids.append(call_email.id)
            queryset = queryset.filter(id__in=status_filter_callemail_ids)
        classification_filter = classification_filter.lower() if classification_filter else 'all'
        if classification_filter != 'all':
            classification_filter_callemail_ids = []
            for call_email in queryset:
                if classification_filter in call_email.classification.name.lower() if call_email.classification else '':
                    classification_filter_callemail_ids.append(call_email.id)
            queryset = queryset.filter(id__in=classification_filter_callemail_ids)

        if date_from:
            queryset = queryset.filter(lodged_on__gte=date_from)
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            queryset = queryset.filter(lodged_on__lte=date_to)

        # override queryset ordering, required because the ordering is usually handled
        # in the super call, but is then clobbered by the custom queryset joining above
        # also needed to disable ordering for all fields for which data is not an
        # CallEmail model field, as property functions will not work with order_by
        
        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        if len(ordering):
           for num, item in enumerate(ordering):
                if item == 'status__name':
                    ordering.pop(num)
                    ordering.insert(num, 'status')
                if item == '-status__name':
                    ordering.pop(num)
                    ordering.insert(num, '-status')

           queryset = queryset.order_by(*ordering)
        else:
            queryset = queryset.order_by(['-number'])


        setattr(view, '_datatables_total_count', total_count)
        return queryset


class CallEmailRenderer(DatatablesRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'view' in renderer_context and hasattr(renderer_context['view'], '_datatables_total_count'):
            data['recordsTotal'] = renderer_context['view']._datatables_total_count
        return super(CallEmailRenderer, self).render(data, accepted_media_type, renderer_context)


class CallEmailPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (CallEmailFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (CallEmailRenderer,)
    queryset = CallEmail.objects.none()
    serializer_class = CallEmailDatatableSerializer
    page_size = 10
    
    def get_queryset(self):
        # import ipdb; ipdb.set_trace()
        user = self.request.user
        if is_internal(self.request):
            return CallEmail.objects.all()
        return CallEmail.objects.none()

    @list_route(methods=['GET', ])
    def get_paginated_datatable(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = CallEmailDatatableSerializer(
            result_page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)


class CallEmailViewSet(viewsets.ModelViewSet):
    queryset = CallEmail.objects.all()
    serializer_class = CallEmailSerializer

    def get_queryset(self):
        # import ipdb; ipdb.set_trace()
        user = self.request.user
        if is_internal(self.request):
            return CallEmail.objects.all()
        return CallEmail.objects.none()

    @list_route(methods=['GET', ])
    def optimised(self, request, *args, **kwargs):
        queryset = self.get_queryset().exclude(location__isnull=True)

        filter_status = request.query_params.get('status', '')
        filter_status = '' if filter_status.lower() == 'all' else filter_status
        filter_classification = request.query_params.get('classification', '')
        filter_classification = '' if filter_classification.lower() == 'all' else filter_classification
        filter_lodged_from = request.query_params.get('lodged_from', '')
        filter_lodged_to = request.query_params.get('lodged_to', '')

        q_list = []
        if filter_status:
            q_list.append(Q(status__exact=filter_status))
        if filter_classification:
            q_list.append(Q(classification__exact=filter_classification))
        if filter_lodged_from:
            date_from = datetime.strptime(filter_lodged_from, '%d/%m/%Y')
            q_list.append(Q(lodged_on__gte=date_from))
        if filter_lodged_to:
            date_to = datetime.strptime(filter_lodged_to, '%d/%m/%Y')
            q_list.append(Q(lodged_on__lte=date_to))

        queryset = queryset.filter(reduce(operator.and_, q_list)) if len(q_list) else queryset

        serializer = CallEmailOptimisedSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @list_route(methods=['GET', ])
    def datatable_list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = CallEmailDatatableSerializer(
                qs, many=True, context={'request': request})
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

    @list_route(methods=['GET', ])    
    def status_choices(self, request, *args, **kwargs):
        res_obj = [] 
        for choice in CallEmail.STATUS_CHOICES:
            res_obj.append({'id': choice[0], 'display': choice[1]});
        res_json = json.dumps(res_obj)
        return HttpResponse(res_json, content_type='application/json')

    @detail_route(methods=['GET', ])
    @renderer_classes((JSONRenderer,))
    def get_allocated_group(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = CallEmailAllocatedGroupSerializer(instance)

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
    def form_data(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            ComplianceFormDataRecord.process_form(
                request,
                instance,
                request.data.get('renderer_data'),
                action=ComplianceFormDataRecord.ACTION_TYPE_ASSIGN_VALUE
            )
            return redirect(reverse('external'))
        
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
        raise serializers.ValidationError(str(e))
    
    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def process_renderer_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            returned_data = process_generic_document(request, instance)
            if returned_data:
                return Response(returned_data)
            else:
                return Response()

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

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def process_comms_log_document(self, request, *args, **kwargs):
        print("process_comms_log_document")
        print(request.data)
        try:
            instance = self.get_object()
            returned_data = process_generic_document(request, instance, document_type='comms_log')
            if returned_data:
                return Response(returned_data)
            else:
                return Response()

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
            serializer = CallEmailUserActionSerializer(qs, many=True)
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
            serializer = CallEmailLogEntrySerializer(qs, many=True)
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
    def add_comms_log(self, request, workflow=False, *args, **kwargs):
        print("add_comms_log")
        print(request.data)
        try:
            with transaction.atomic():
                instance = self.get_object()
                request.data['call_email'] = u'{}'.format(instance.id)
                # request.data['staff'] = u'{}'.format(request.user.id)
                if request.data.get('comms_log_id'):
                    comms_instance = CallEmailLogEntry.objects.get(id=request.data.get('comms_log_id'))
                    serializer = CallEmailLogEntrySerializer(comms_instance, data=request.data)
                else:
                    serializer = CallEmailLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                #comms.process_comms_log_document(request)
                # for f in request.FILES:
                #     document = comms.documents.create()
                #     print("filename")
                #     print(str(request.FILES[f]))
                #     document.name = str(request.FILES[f])
                #     document._file = request.FILES[f]
                #     document.save()
                # End Save Documents

                if workflow:
                    return comms
                else:
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

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                request_data = request.data
                # Create location then include in request to create new Call/Email
                returned_location = None

                if (
                    request_data.get('location', {}).get('geometry', {}).get('coordinates', {}) or
                    request_data.get('location', {}).get('properties', {}).get('postcode', {}) or
                    request_data.get('location', {}).get('properties', {}).get('details', {})
                ):
                    returned_location = self.save_location(request)
                    if returned_location:
                        request_data.update({'location_id': returned_location.get('id')})
                
                if request_data.get('report_type'):
                    request_data.update({'report_type_id': request_data.get('report_type', {}).get('id')})

                # Initial allocated_group_id must be volunteers
                compliance_content_type = ContentType.objects.get(model="compliancepermissiongroup")
                permission = Permission.objects.filter(codename='volunteer').filter(content_type_id=compliance_content_type.id).first()
                group = CompliancePermissionGroup.objects.filter(permissions=permission).first()
                request_data.update({'allocated_group_id': group.id})
                
                serializer = CreateCallEmailSerializer(data=request_data, partial=True)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    new_instance = serializer.save()
                    new_returned = serializer.data
                    # Ensure classification_id and report_type_id is returned for Vue template evaluation                
                    # new_returned.update({'classification_id': request_data.get('classification_id')})
                    new_returned.update({'report_type_id': request_data.get('report_type_id')})
                    # new_returned.update({'referrer_id': request_data.get('referrer_id')})
                    if request_data.get('location'):
                        new_returned.update({'location_id': request_data.get('location').get('id')})

                    if request.data.get('renderer_data'):
                    # option required for duplicated Call/Emails
                        ComplianceFormDataRecord.process_form(
                            request,
                            new_instance,
                            request.data.get('renderer_data'),
                            action=ComplianceFormDataRecord.ACTION_TYPE_ASSIGN_VALUE
                        )

                        # Serializer returns CallEmail.data for HTTP response
                        duplicate = CallEmailSerializer(instance=new_instance, context={'request': request})
                        headers = self.get_success_headers(duplicate.data)

                        # duplicate.data.update({'classification_id': request_data.get('classification_id')})
                        duplicate.data.update({'report_type_id': request_data.get('report_type_id')})
                        # duplicate.data.update({'referrer_id': request_data.get('referrer_id')})
                        if request_data.get('location'):
                            duplicate.data.update({'location_id': request_data.get('location').get('id')})
                        
                        return Response(
                            duplicate.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers
                            )
                    else:
                        headers = self.get_success_headers(serializer.data)
                        return Response(
                            new_returned,
                            status=status.HTTP_201_CREATED,
                            headers=headers
                        )
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
    def call_email_save_person(self, request, *args, **kwargs):
        call_email_instance = self.get_object()

        try:
            with transaction.atomic():
                #####
                # Email user
                #####
                email_user_id_requested = request.data.get('email_user', {}).get('id', {})
                email_address = request.data.get('email_user', {}).get('email', '')
                if not email_address:
                    first_name = request.data.get('email_user', {}).get('first_name', '')
                    last_name = request.data.get('email_user', {}).get('last_name', '')
                    email_address = generate_dummy_email(first_name, last_name)

                if email_user_id_requested:
                    email_user_instance = EmailUser.objects.get(id=email_user_id_requested)
                    email_user_instance.email = email_address
                else:
                    email_user_instance = EmailUser.objects.create_user(email_address, '')
                    request.data['email_user'].update({'email': email_address})

                email_user_serializer = SaveEmailUserSerializer(
                    email_user_instance,
                    data=request.data['email_user'],
                    partial=True)

                if email_user_serializer.is_valid(raise_exception=True):
                    email_user_serializer.save()

                    #####
                    # Residential address
                    #####
                    # UPDATE user_id of residential address in order to save the residential address
                    request.data['email_user']['residential_address'].update({'user_id': email_user_serializer.data['id']})
                    residential_address_id_requested = request.data.get('email_user', {}).get('residential_address', {}).get('id', {})
                    if residential_address_id_requested:
                        residential_address_instance = Address.objects.get(id=residential_address_id_requested)
                        address_serializer = SaveUserAddressSerializer(
                            instance=residential_address_instance,
                            data=request.data['email_user']['residential_address'],
                            partial=True)
                    else:
                        address_serializer = SaveUserAddressSerializer(
                            data=request.data['email_user']['residential_address'],
                            partial=True)
                    if address_serializer.is_valid(raise_exception=True):
                        address_serializer.save()

                    # Update relation between email_user and residential_address
                    request.data['email_user'].update({'residential_address_id': address_serializer.data['id']})
                    email_user = EmailUser.objects.get(id=email_user_serializer.instance.id)
                    email_user_serializer = SaveEmailUserSerializer(email_user, request.data['email_user'])
                    if email_user_serializer.is_valid():
                        email_user_serializer.save()

                    # Update relation between call_email and email_user
                    request.data.update({'email_user_id': email_user_serializer.data['id']})
                    call_email_serializer = SaveCallEmailSerializer(call_email_instance, data=request.data)
                    if call_email_serializer.is_valid():
                        call_email_serializer.save()
                        call_email_instance.log_user_action(
                            CallEmailUserAction.ACTION_PERSON_SEARCH.format(
                            call_email_instance.number), request)

            # Reload data via serializer
            email_user = EmailUser.objects.get(id=email_user_serializer.instance.id)
            email_user_serializer = SaveEmailUserSerializer(email_user)
            return Response(
                email_user_serializer.data,
                status=status.HTTP_201_CREATED,
                headers=self.get_success_headers(email_user_serializer.data)
            )

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
    def call_email_save(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            with transaction.atomic():
                request_data = request.data

                if (
                    request_data.get('location', {}).get('geometry', {}).get('coordinates', {}) or
                    request_data.get('location', {}).get('properties', {}).get('postcode', {}) or
                    request_data.get('location', {}).get('properties', {}).get('details', {})
                ):
                    location_request_data = request.data.get('location')
                    returned_location = save_location(location_request_data)
                    if returned_location:
                        request_data.update({'location_id': returned_location.get('id')})

                # self.save_email_user(request)

                if request_data.get('renderer_data'):
                    self.form_data(request)

                if request_data.get('report_type'):
                    request_data.update({'report_type_id': request_data.get('report_type', {}).get('id')})

                serializer = SaveCallEmailSerializer(instance, data=request_data)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    saved_instance = serializer.save()
                    instance.log_user_action(
                        CallEmailUserAction.ACTION_SAVE_CALL_EMAIL_.format(
                        instance.number), request)
                    headers = self.get_success_headers(serializer.data)
                    return_serializer = CallEmailSerializer(instance=saved_instance, context={'request': request})
                    return Response(
                        return_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers
                    )
                    
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    #def send_mail(self, request, instance, workflow_entry, *args, **kwargs):
    #    print("send_mail")
    #    print(request.data)
    #    try:
    #        #attachments = []
    #        #for doc in workflow_entry.documents.all():
    #         #   attachments.append(doc)

    #        email_group = []
    #        if request.data.get('assigned_to'):
    #            try:
    #                user_id_int = int(request.data.get('assigned_to'))
    #                email_group.append(EmailUser.objects.get(id=user_id_int))
    #                # update CallEmail
    #                instance.assigned_to = (EmailUser.objects.get(id=user_id_int))
    #            except Exception as e:
    #                    print(traceback.print_exc())
    #                    raise
    #        elif request.data.get('allocated_group'):
    #            users = request.data.get('allocated_group').split(",")
    #            for user_id in users:
    #                if user_id:
    #                    try:
    #                        user_id_int = int(user_id)
    #                        email_group.append(EmailUser.objects.get(id=user_id_int))
    #                    except Exception as e:
    #                        print(traceback.print_exc())
    #                        raise
    #        else:
    #            email_group.append(request.user)

    #        # send email
    #        email_data = send_call_email_forward_email(
    #        email_group, 
    #        instance,
    #        # workflow_entry.documents,
    #        workflow_entry,
    #        request)

    #        return email_data

    #    except Exception as e:
    #        print(traceback.print_exc())
    #        raise e

    @detail_route(methods=['POST', ])
    @renderer_classes((JSONRenderer,))
    def workflow_action(self, request, *args, **kwargs):
        print(request.data)
        try:
            with transaction.atomic():
                instance = self.get_object()
                comms_log_id = request.data.get('call_email_comms_log_id')
                if comms_log_id and comms_log_id is not 'null':
                    workflow_entry = instance.comms_logs.get(
                            id=comms_log_id)
                else:
                    workflow_entry = self.add_comms_log(request, workflow=True)

                # Set CallEmail status depending on workflow type
                workflow_type = request.data.get('workflow_type')
                if workflow_type == 'forward_to_regions':
                    instance.forward_to_regions(request)
                elif workflow_type == 'forward_to_wildlife_protection_branch':
                    instance.forward_to_wildlife_protection_branch(request)
                elif workflow_type == 'allocate_for_follow_up':
                    instance.allocate_for_follow_up(request)
                elif workflow_type == 'allocate_for_inspection':
                    instance.allocate_for_inspection(request)
                elif workflow_type == 'allocate_for_case':
                    instance.allocate_for_case(request)
                elif workflow_type == 'close':
                    instance.close(request)
                elif workflow_type == 'offence':
                    instance.add_offence(request)
                elif workflow_type == 'sanction_outcome':
                    instance.add_sanction_outcome(request)

                if request.data.get('referrers_selected'):
                    instance.add_referrers(request)

                instance.region_id = None if not request.data.get('region_id') else request.data.get('region_id')
                instance.district_id = None if not request.data.get('district_id') else request.data.get('district_id')
                instance.assigned_to_id = None if not request.data.get('assigned_to_id') else request.data.get('assigned_to_id')
                instance.inspection_type_id = None if not request.data.get('inspection_type_id') else request.data.get('inspection_type_id')
                instance.case_priority_id = None if not request.data.get('case_priority_id') else request.data.get('case_priority_id')
                instance.allocated_group_id = None if not request.data.get('allocated_group_id') else request.data.get('allocated_group_id')

                instance.save()

                email_data = prepare_mail(request, instance, workflow_entry, send_mail)

                serializer = CallEmailLogEntrySerializer(instance=workflow_entry, data=email_data, partial=True)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    serializer.save()
                    return_serializer = CallEmailSerializer(instance=instance, 
                            context={'request': request}
                            ) 
                    headers = self.get_success_headers(return_serializer.data)
                    return Response(
                            return_serializer.data, 
                            status=status.HTTP_201_CREATED,
                            headers=headers
                            )
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
    def update_assigned_to_id(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = None

            validation_serializer = CallEmailSerializer(instance, context={'request': request})
            user_in_group = validation_serializer.data.get('user_in_group')

            if request.data.get('current_user') and user_in_group:
                serializer = UpdateAssignedToIdSerializer(
                        instance=instance,
                        data={
                            'assigned_to_id': request.user.id,
                            }
                        )
            elif user_in_group:
                serializer = UpdateAssignedToIdSerializer(instance=instance, data=request.data)
            
            if serializer:
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    serializer.save()
                    return_serializer = CallEmailSerializer(instance=instance,
                            context={'request': request}
                            )
                    headers = self.get_success_headers(return_serializer.data)
                    return Response(
                            return_serializer.data, 
                            status=status.HTTP_201_CREATED,
                            headers=headers
                            )
            else:
                return Response(validation_serializer.data, 
                                status=status.HTTP_201_CREATED
                                )
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

class ClassificationViewSet(viewsets.ModelViewSet):
    queryset = Classification.objects.all()
    serializer_class = ClassificationSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Classification.objects.all()
        return Classification.objects.none()


class ReferrerViewSet(viewsets.ModelViewSet):
    queryset = Referrer.objects.all()
    serializer_class = ReferrerSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Referrer.objects.all()
        return Referrer.objects.none()


class CasePriorityViewSet(viewsets.ModelViewSet):
    queryset = CasePriority.objects.all()
    serializer_class = CasePrioritySerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return CasePriority.objects.all()
        return CasePriority.objects.none()


# class InspectionTypeViewSet(viewsets.ModelViewSet):
#     queryset = InspectionType.objects.all()
#     serializer_class = InspectionTypeSerializer

#     def get_queryset(self):
#         user = self.request.user
#         if is_internal(self.request):
#             return InspectionType.objects.all()
#         return InspectionType.objects.none()


class ReportTypeViewSet(viewsets.ModelViewSet):
    queryset = ReportType.objects.all()
    serializer_class = ReportTypeSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ReportType.objects.all()
        return ReportType.objects.none()

    @list_route(methods=['GET', ])
    @renderer_classes((JSONRenderer,))
    def get_distinct_queryset(self, request, *args, **kwargs):
        user = self.request.user
        return_list = []
        if is_internal(self.request):
            valid_records = ReportType.objects.values('report_type').annotate(Max('version'))
            for record in valid_records:
                qs_record = ReportType.objects \
                    .filter(report_type=record['report_type']) \
                    .filter(version=record['version__max']) \
                    .values('id', 'report_type', 'version')[0]

                return_list.append(qs_record)
        return Response(return_list)

    @detail_route(methods=['GET',])
    @renderer_classes((JSONRenderer,))
    def get_schema(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            serializer = ReportTypeSchemaSerializer(instance)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                )
                
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
   

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Location.objects.all()
        return Location.objects.none()

    @list_route(methods=['GET', ])
    def optimised(self, request, *args, **kwargs):
        queryset = self.get_queryset().exclude(call_location__isnull=True)
        serializer = LocationSerializerOptimized(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            serializer = LocationSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                    )
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


class EmailUserViewSet(viewsets.ModelViewSet):
    queryset = EmailUser.objects.all()
    serializer_class = EmailUserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'mobile_number', 'organisation')


class MapLayerViewSet(viewsets.ModelViewSet):
    queryset = MapLayer.objects.filter(availability__exact=True)
    serializer_class =  MapLayerSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return MapLayer.objects.filter(availability__exact=True)
        return MapLayer.objects.none()

