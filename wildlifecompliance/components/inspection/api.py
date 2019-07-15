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
from wildlifecompliance.components.users.serializers import (
    UserAddressSerializer,
    ComplianceUserDetailsSerializer,
)
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.inspection.models import (
    Inspection,
    InspectionUserAction,
    InspectionType,
)    
from wildlifecompliance.components.inspection.serializers import (
    InspectionSerializer,
    InspectionUserActionSerializer,
    InspectionCommsLogEntrySerializer,
    SaveInspectionSerializer,
    InspectionDatatableSerializer,
    UpdateAssignedToIdSerializer,
    InspectionTypeSerializer,
    )
from wildlifecompliance.components.users.models import (
    CompliancePermissionGroup,    
)
from django.contrib.auth.models import Permission, ContentType
from utils import SchemaParser

from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer

from wildlifecompliance.components.inspection.email import (
    send_inspection_forward_email)


class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer

    def get_queryset(self):
        # import ipdb; ipdb.set_trace()
        user = self.request.user
        if is_internal(self.request):
            return Inspection.objects.all()
        return Inspection.objects.none()

    @list_route(methods=['GET', ])
    def datatable_list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = InspectionDatatableSerializer(
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
    
    @detail_route(methods=['GET', ])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = InspectionUserActionSerializer(qs, many=True)
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
            serializer = InspectionCommsLogEntrySerializer(qs, many=True)
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
    def add_comms_log(self, request, instance, workflow=False, *args, **kwargs):
        try:
            with transaction.atomic():
                #instance = self.get_object()
                request.data['inspection'] = u'{}'.format(instance.id)
                print(request.data)
                # request.data['staff'] = u'{}'.format(request.user.id)
                serializer = InspectionCommsLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    print("filename")
                    print(str(request.FILES[f]))
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
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

    @detail_route(methods=['POST', ])
    @renderer_classes((JSONRenderer,))
    def inspection_save(self, request, workflow=False, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                serializer = SaveInspectionSerializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    saved_instance = serializer.save()
                    instance.log_user_action(
                            InspectionUserAction.ACTION_SAVE_INSPECTION_.format(
                            instance.number), request)
                    headers = self.get_success_headers(serializer.data)
                    return_serializer = InspectionSerializer(saved_instance)
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
        print("update assigned to")
        print(request.data)
        try:
            instance = self.get_object()
            serializer = None

            validation_serializer = InspectionSerializer(instance, context={'request': request})
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
                    return_serializer = InspectionSerializer(instance=instance,
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

    def create(self, request, *args, **kwargs):
        print(request.data)
        try:
            with transaction.atomic():
                #instance = self.get_object()
                #workflow_entry = self.add_comms_log(request, workflow=True)
                serializer = SaveInspectionSerializer(
                        data=request.data, 
                        partial=True
                        )
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    instance = serializer.save()
                comms_log_id = request.data.get('comms_log_id')
                if comms_log_id and comms_log_id is not 'null':
                    workflow_entry = instance.comms_logs.get(
                            id=comms_log_id)
                else:
                    workflow_entry = self.add_comms_log(request, instance, workflow=True)

                attachments = []
                for doc in workflow_entry.documents.all():
                    attachments.append(doc)

                email_group = []
                if request.data.get('assigned_to'):
                    try:
                        user_id_int = int(request.data.get('assigned_to'))
                        email_group.append(EmailUser.objects.get(id=user_id_int))
                        # update CallEmail
                        instance.assigned_to = (EmailUser.objects.get(id=user_id_int))
                    except Exception as e:
                            print(traceback.print_exc())
                            raise
                elif request.data.get('allocated_group'):
                    users = request.data.get('allocated_group').split(",")
                    for user_id in users:
                        if user_id:
                            try:
                                user_id_int = int(user_id)
                                email_group.append(EmailUser.objects.get(id=user_id_int))
                            except Exception as e:
                                print(traceback.print_exc())
                                raise
                else:
                    email_group.append(request.user)

                # Set Inspection status to open
                instance.status = 'open'
                
                instance.region_id = None if request.data.get('region_id') =='null' else request.data.get('region_id')
                instance.district_id = None if request.data.get('district_id') == 'null' else request.data.get('district_id')
                #instance.allocated_group_id = request.data.get('allocated_group_id')

                instance.assigned_to_id = None if request.data.get('assigned_to_id') == 'null' else request.data.get('assigned_to_id')
                instance.inspection_type_id = None if request.data.get('inspection_type_id') == 'null' else request.data.get('inspection_type_id')
                instance.allocated_group_id = None if request.data.get('allocated_group_id') == 'null' else request.data.get('allocated_group_id')

                #if not workflow_type == 'allocate_for_follow_up':
                 #   instance.assigned_to_id = None
                instance.save()

                # send email
                email_data = send_inspection_forward_email(
                email_group, 
                instance,
                # workflow_entry.documents,
                workflow_entry,
                request)

                serializer = InspectionCommsLogEntrySerializer(instance=workflow_entry, data=email_data, partial=True)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    serializer.save()
                    return_serializer = InspectionSerializer(instance=instance, 
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



class InspectionTypeViewSet(viewsets.ModelViewSet):
   queryset = InspectionType.objects.all()
   serializer_class = InspectionTypeSerializer

   def get_queryset(self):
       user = self.request.user
       if is_internal(self.request):
           return InspectionType.objects.all()
       return InspectionType.objects.none()

