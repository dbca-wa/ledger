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
    InspectionCommsLogEntry,
    )
from wildlifecompliance.components.call_email.models import (
        CallEmailUserAction,
        )
from wildlifecompliance.components.inspection.serializers import (
    InspectionSerializer,
    InspectionUserActionSerializer,
    InspectionCommsLogEntrySerializer,
    SaveInspectionSerializer,
    InspectionDatatableSerializer,
    UpdateAssignedToIdSerializer,
    InspectionTypeSerializer,
    #InspectionTeamSerializer,
    EmailUserSerializer,
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


class InspectionFilterBackend(DatatablesFilterBackend):

    def filter_queryset(self, request, queryset, view):
        #import ipdb; ipdb.set_trace()
        # Get built-in DRF datatables queryset first to join with search text, then apply additional filters
        # super_queryset = super(CallEmailFilterBackend, self).filter_queryset(request, queryset, view).distinct()

        total_count = queryset.count()
        status_filter = request.GET.get('status_description')
        inspection_filter = request.GET.get('inspection_description')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        search_text = request.GET.get('search[value]')

        if search_text:
            search_text = search_text.lower()
            search_text_inspection_ids = []
            for inspection in queryset:
                #lodged_on_str = time.strftime('%d/%m/%Y', call_email.lodged_on)
                planned_for_str = inspection.planned_for_date.strftime('%d/%m/%Y')
                if (search_text in (inspection.number.lower() if inspection.number else '')
                    or search_text in (inspection.status.lower() if inspection.status else '')
                    or search_text in (inspection.inspection_type.description.lower() if inspection.inspection_type else '')
                    or search_text in (planned_for_str.lower() if planned_for_str else '')
                    or search_text in (inspection.title.lower() if inspection.title else '')
                    or search_text in (
                        inspection.assigned_to.first_name.lower() + ' ' + inspection.assigned_to.last_name.lower()
                        if inspection.assigned_to else ''
                        )
                    ):
                    search_text_inspection_ids.append(inspection.id)

            # use pipe to join both custom and built-in DRF datatables querysets (returned by super call above)
            # (otherwise they will filter on top of each other)
            #_queryset = queryset.filter(id__in=search_text_callemail_ids).distinct() | super_queryset
            # BB 20190704 - is super_queryset necessary?
            queryset = queryset.filter(id__in=search_text_inspection_ids)

        status_filter = status_filter.lower() if status_filter else 'all'
        if status_filter != 'all':
            status_filter_inspection_ids = []
            for inspection in queryset:
                if status_filter == inspection.get_status_display().lower():
                    status_filter_inspection_ids.append(inspection.id)
            queryset = queryset.filter(id__in=status_filter_inspection_ids)
        inspection_filter = inspection_filter.lower() if inspection_filter else 'all'
        if inspection_filter != 'all':
            inspection_filter_inspection_ids = []
            for inspection in queryset:
                if inspection_filter in inspection.inspection_type.description.lower() if inspection.inspection_type else '':
                    inspection_filter_inspection_ids.append(inspection.id)
            queryset = queryset.filter(id__in=inspection_filter_inspection_ids)

        if date_from:
            queryset = queryset.filter(planned_for_date__gte=date_from)
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            queryset = queryset.filter(planned_for_date__lte=date_to)

        # override queryset ordering, required because the ordering is usually handled
        # in the super call, but is then clobbered by the custom queryset joining above
        # also needed to disable ordering for all fields for which data is not an
        # CallEmail model field, as property functions will not work with order_by
        
        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        if len(ordering):
            for num, item in enumerate(ordering):
                if item == 'planned_for':
                    # ordering.pop(num)
                    # ordering.insert(num, 'planned_for_date')
                    ordering[num] = 'planned_for_date'
                elif item == '-planned_for':
                    # ordering.pop(num)
                    # ordering.insert(num, '-planned_for_date')
                    ordering[num] = '-planned_for_date'
                elif item == 'status__name':
                    # ordering.pop(num)
                    # ordering.insert(num, 'status')
                    ordering[num] = 'status'
                elif item == '-status__name':
                    # ordering.pop(num)
                    # ordering.insert(num, '-status')
                    ordering[num] = '-status'

            queryset = queryset.order_by(*ordering)

        setattr(view, '_datatables_total_count', total_count)
        return queryset


class InspectionRenderer(DatatablesRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'view' in renderer_context and hasattr(renderer_context['view'], '_datatables_total_count'):
            data['recordsTotal'] = renderer_context['view']._datatables_total_count
        return super(InspectionRenderer, self).render(data, accepted_media_type, renderer_context)


class InspectionPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (InspectionFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (InspectionRenderer,)
    queryset = Inspection.objects.none()
    serializer_class = InspectionDatatableSerializer
    page_size = 10
    
    def get_queryset(self):
        # import ipdb; ipdb.set_trace()
        user = self.request.user
        if is_internal(self.request):
            return Inspection.objects.all()
        return Inspection.objects.none()

    @list_route(methods=['GET', ])
    def get_paginated_datatable(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = InspectionDatatableSerializer(
            result_page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)


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

    @list_route(methods=['GET', ])    
    def status_choices(self, request, *args, **kwargs):
        res_obj = [] 
        for choice in Inspection.STATUS_CHOICES:
            res_obj.append({'id': choice[0], 'display': choice[1]});
        res_json = json.dumps(res_obj)
        return HttpResponse(res_json, content_type='application/json')
    
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
    def add_comms_log(self, request, instance=None, workflow=False, *args, **kwargs):
        try:
            with transaction.atomic():
                # create Inspection instance if not passed to this method
                if not instance:
                    instance = self.get_object()
                # add Inspection attribute to request_data
                request_data = request.data.copy()
                request_data['inspection'] = u'{}'.format(instance.id)
                if request_data.get('comms_log_id'):
                    comms = InspectionCommsLogEntry.objects.get(
                        id=request_data.get('comms_log_id')
                        )
                    serializer = InspectionCommsLogEntrySerializer(
                        instance=comms, 
                        data=request.data)
                else:
                    serializer = InspectionCommsLogEntrySerializer(
                        data=request_data
                        )
                serializer.is_valid(raise_exception=True)
                # overwrite comms with updated instance
                comms = serializer.save()
                
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

    @detail_route(methods=['GET', ])
    @renderer_classes((JSONRenderer,))
    def get_inspection_team(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            #serializer = InspectionTeamSerializer(instance)
            #team = EmailUser.objects.select_related('inspection_team').get(id=instance.id)
            #qs = EmailUser.objects.filter(instance.inspection_team)
            serializer = EmailUserSerializer(
                instance.inspection_team.all(),
                context={
                    'inspection_team_lead_id': instance.inspection_team_lead_id
                },
                many=True)
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

    @detail_route(methods=['POST', ])
    @renderer_classes((JSONRenderer,))
    def modify_inspection_team(self, request, instance=None, workflow=False, user_id=None, *args, **kwargs):
        try:
            with transaction.atomic():
                if not instance:
                    instance = self.get_object()
                if workflow:
                    action = 'add' # 'add', 'remove or 'clear'
                    user_id = user_id
                else:
                    action = request.data.get('action') # 'add', 'remove or 'clear'
                    user_id = request.data.get('user_id')

                #if action and user_list:
                if action and user_id:
                    #users = EmailUser.objects.filter(id__in=user_list)
                    user = EmailUser.objects.get(id=user_id)
                    team_member_list = instance.inspection_team.all()
                    #if action == 'set' and users:
                     #   instance.inspection_team.set(user_list)
                    if action == 'add':
                        if user not in team_member_list:
                            instance.inspection_team.add(user)
                        if not instance.inspection_team_lead or not team_member_list:
                           instance.inspection_team_lead = user
                    if action == 'remove':
                        if user in team_member_list:
                            instance.inspection_team.remove(user)
                        team_member_list = instance.inspection_team.all()
                        if team_member_list and not instance.inspection_team_lead_id in team_member_list:
                            instance.inspection_team_lead = team_member_list[0]
                        else:
                            instance.inspection_team_lead_id = None
                    if action == 'make_team_lead':
                        if user not in team_member_list:
                            instance.inspection_team.add(user)
                        instance.inspection_team_lead = user
                    instance.save()
                    if workflow:
                        return instance
                    else:
                        serializer = InspectionSerializer(instance, context={'request': request})
                        return Response(
                            serializer.data,
                            status=status.HTTP_201_CREATED,
                        )
                else:
                    serializer = InspectionSerializer(instance, context={'request': request})
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
                    return_serializer = InspectionSerializer(saved_instance, context={'request': request})
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
        try:
            instance = self.get_object()
            returned_data = process_generic_document(
                request, 
                instance, 
                document_type='comms_log'
                )
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
        try:
            with transaction.atomic():
                serializer = SaveInspectionSerializer(
                        data=request.data, 
                        partial=True
                        )
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    instance = serializer.save()
                    if request.data.get('allocated_group_id'):
                        res = self.add_workflow_log(request, instance)
                        return res
                    else:
                        # Log parent actions and update status
                        self.update_parent(request, instance)
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

    def send_mail(self, request, instance, workflow_entry, *args, **kwargs):
        print("send_mail")
        print(request.data)
        try:
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

            # send email
            email_data = send_inspection_forward_email(
            email_group, 
            instance,
            # workflow_entry.documents,
            workflow_entry,
            request)

            return email_data

        except Exception as e:
            print(traceback.print_exc())
            raise e

    def update_parent(self, request, instance, *args, **kwargs):
        # Log parent actions and update status
        # If CallEmail
        if instance.call_email:
            instance.call_email.log_user_action(
                    CallEmailUserAction.ACTION_ALLOCATE_FOR_INSPECTION.format(
                    instance.call_email.number), request)
            instance.call_email.status = 'open_inspection'
            instance.call_email.save()


    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def add_workflow_log(self, request, instance=None, *args, **kwargs):
        try:
            with transaction.atomic():
                if not instance:
                    instance = self.get_object()

                comms_log_id = request.data.get('inspection_comms_log_id')
                if comms_log_id and comms_log_id is not 'null':
                    workflow_entry = instance.comms_logs.get(
                            id=comms_log_id)
                else:
                    workflow_entry = self.add_comms_log(request, instance, workflow=True)

                # Set Inspection status to open
                instance.status = 'open'
                
                instance.region_id = None if request.data.get('region_id') =='null' else request.data.get('region_id')
                instance.district_id = None if request.data.get('district_id') == 'null' else request.data.get('district_id')
                #instance.allocated_group_id = request.data.get('allocated_group_id')

                instance.assigned_to_id = None if request.data.get('assigned_to_id') == 'null' else request.data.get('assigned_to_id')
                instance.inspection_type_id = None if request.data.get('inspection_type_id') == 'null' else request.data.get('inspection_type_id')
                instance.allocated_group_id = None if request.data.get('allocated_group_id') == 'null' else request.data.get('allocated_group_id')
                instance.call_email_id = None if request.data.get('call_email_id') == 'null' else request.data.get('call_email_id')

                instance.save()
                # Log parent actions and update status
                self.update_parent(request, instance)

                if instance.assigned_to_id:
                    instance = self.modify_inspection_team(request, instance, workflow=True, user_id=instance.assigned_to_id)

                # send email
                email_data = self.send_mail(request, instance, workflow_entry)

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

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def create_modal_process_comms_log_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # process docs
            returned_data = process_generic_document(request, instance, document_type='comms_log')
            # delete Inspection if user cancels modal
            action = request.data.get('action')
            if action == 'cancel' and returned_data:
                # returned_data = instance.delete()
                instance.status = 'discarded'
                instance.save()
            # return response
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


class InspectionTypeViewSet(viewsets.ModelViewSet):
   queryset = InspectionType.objects.all()
   serializer_class = InspectionTypeSerializer

   def get_queryset(self):
       user = self.request.user
       if is_internal(self.request):
           return InspectionType.objects.all()
       return InspectionType.objects.none()

