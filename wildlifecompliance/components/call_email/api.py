import json
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
from datetime import datetime, timedelta
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from ledger.checkout.utils import calculate_excl_gst
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.call_email.models import (
    CallEmail,
    Classification,
    Location,
    ComplianceFormDataRecord,
    ReportType,
    Referrer,
    ComplianceUserAction,
    MapLayer)
from wildlifecompliance.components.call_email.serializers import (
    CallEmailSerializer,
    ClassificationSerializer,
    ComplianceFormDataRecordSerializer,
    ComplianceLogEntrySerializer,
    LocationSerializer,
    ComplianceUserActionSerializer,
    LocationSerializer,
    ReportTypeSerializer,
    SaveCallEmailSerializer,
    CreateCallEmailSerializer,
    ReportTypeSchemaSerializer,
    ReferrerSerializer,
    LocationSerializerMinimum, CallEmailOptimisedSerializer, EmailUserSerializer, MapLayerSerializer)
from utils import SchemaParser

from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer


class CallEmailViewSet(viewsets.ModelViewSet):
    queryset = CallEmail.objects.all()
    serializer_class = CallEmailSerializer

    def get_queryset(self):
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
            serializer = self.get_serializer(
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
    def process_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            action = request.data.get('action')
            section = request.data.get('input_name')
            if action == 'list' and 'input_name' in request.data:
                pass

            elif action == 'delete' and 'document_id' in request.data:
                document_id = request.data.get('document_id')
                document = instance.documents.get(id=document_id)

                if document._file and os.path.isfile(
                        document._file.path) and document.can_delete:
                    os.remove(document._file.path)

                document.delete()
                instance.save(version_comment='Approval File Deleted: {}'.format(
                    document.name))  # to allow revision to be added to reversion history

            elif action == 'save' and 'input_name' in request.data and 'filename' in request.data:
                application_id = request.data.get('application_id')
                filename = request.data.get('filename')
                _file = request.data.get('_file')
                if not _file:
                    _file = request.data.get('_file')

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
            serializer = ComplianceUserActionSerializer(qs, many=True)
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
            serializer = ComplianceLogEntrySerializer(qs, many=True)
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
                request.data['call_email'] = u'{}'.format(instance.id)
                # request.data['staff'] = u'{}'.format(request.user.id)
                serializer = ComplianceLogEntrySerializer(data=request.data)
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

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                request_data = request.data
                # Create location then include in request to create new Call/Email
                returned_location = None
                if not request.user.has_perm('wildlifecompliance.licensing_officer'):
                    raise serializers.ValidationError(
                    'You are not authorised to assign officers to applications')
                else:
                    print(request.user.has_perm('wildlifecompliance.licensing_officer'))
                    print('You are authorised to assign officers to applications')

                if (
                    request_data.get('location', {}).get('geometry', {}).get('coordinates', {}) or
                    request_data.get('location', {}).get('properties', {}).get('postcode', {}) or
                    request_data.get('location', {}).get('properties', {}).get('details', {})
                ):
                    returned_location = self.save_location(request)
                    if returned_location:
                        request_data.update({'location_id': returned_location.get('id')})
                
                print("returned_location")
                print(returned_location)
                print("request_data")
                print(request_data)

                # if request_data.get('classification'):
                #     request_data.update({'classification_id': request_data.get('classification', {}).get('id')})
                if request_data.get('report_type'):
                    request_data.update({'report_type_id': request_data.get('report_type', {}).get('id')})
                
                serializer = CreateCallEmailSerializer(data=request_data, partial=True)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    new_instance = serializer.save()
                    new_returned = serializer.data
                    # Ensure classification_id and report_type_id is returned for Vue template evaluation                
                    # new_returned.update({'classification_id': request_data.get('classification_id')})
                    new_returned.update({'report_type_id': request_data.get('report_type_id')})
                    new_returned.update({'referrer_id': request_data.get('referrer_id')})
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
                        duplicate = CallEmailSerializer(instance=new_instance)
                        headers = self.get_success_headers(duplicate.data)

                        # duplicate.data.update({'classification_id': request_data.get('classification_id')})
                        duplicate.data.update({'report_type_id': request_data.get('report_type_id')})
                        duplicate.data.update({'referrer_id': request_data.get('referrer_id')})
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
    
    def save_location(self, request, *args, **kwargs):
        
        location_request_data = request.data.get('location')
        if location_request_data.get('id'):
            print("exist location_request_data")
            print(location_request_data)
            
            location_instance = Location.objects.get(id=location_request_data.get('id'))
            location_serializer = LocationSerializer(
                instance=location_instance, 
                data=location_request_data, 
                partial=True
                )
            location_serializer.is_valid(raise_exception=True)
            if location_serializer.is_valid():
                location_serializer.save()
        else:
            print("new location_request_data")
            print(location_request_data)
            location_serializer = LocationSerializer(
                data=location_request_data, 
                partial=True
                )
            location_serializer.is_valid(raise_exception=True)
            if location_serializer.is_valid():
                location_instance = location_serializer.save()
        return location_serializer.data

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
                    returned_location = self.save_location(request)
                    if returned_location:
                        request_data.update({'location_id': returned_location.get('id')})
                
                print("returned_location")
                print(returned_location)
                print("request_data")
                print(request_data)

                if request_data.get('renderer_data'):
                    self.form_data(request)

                # if request_data.get('classification'):
                #     request_data.update({'classification_id': request_data.get('classification', {}).get('id')})
                if request_data.get('report_type'):
                    request_data.update({'report_type_id': request_data.get('report_type', {}).get('id')})

                serializer = SaveCallEmailSerializer(instance, data=request_data)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    serializer.save()
                    instance.log_user_action(
                        ComplianceUserAction.ACTION_SAVE_CALL_EMAIL_.format(
                        instance.number), request)
                    headers = self.get_success_headers(serializer.data)
                    returned_data = serializer.data
                    # Ensure classification_id and report_type_id is returned for Vue template evaluation
                    returned_data.update({'classification_id': request_data.get('classification_id')})
                    returned_data.update({'report_type_id': request_data.get('report_type_id')})
                    returned_data.update({'referrer_id': request_data.get('referrer_id')})
                    return Response(
                        returned_data,
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
    
    # @detail_route(methods=['POST', ])
    # def update_schema(self, request, *args, **kwargs):
    #     print("request.data")
    #     print(request.data)
    #     instance = self.get_object()
    #     if request.data.get('report_type_id'):
    #         try:
    #             serializer = UpdateSchemaSerializer(instance, data=request.data)
    #             serializer.is_valid(raise_exception=True)
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 headers = self.get_success_headers(serializer.data)
    #                 returned_data = serializer.data
    #                 return Response(
    #                     serializer.data,
    #                     status=status.HTTP_201_CREATED,
    #                     headers=headers
    #                     )
    #         except serializers.ValidationError:
    #             print(traceback.print_exc())
    #             raise
    #         except ValidationError as e:
    #             print(traceback.print_exc())
    #             raise serializers.ValidationError(repr(e.error_dict))
    #         except Exception as e:
    #             print(traceback.print_exc())
    #             raise serializers.ValidationError(str(e))


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
        serializer = LocationSerializerMinimum(queryset, many=True)

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

