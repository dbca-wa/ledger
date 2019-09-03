import json
import traceback
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.db.models import Q
from rest_framework import viewsets, filters, serializers, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from ledger.accounts.models import EmailUser, Organisation
from wildlifecompliance.components.call_email.models import Location, CallEmailUserAction, CallEmail
from wildlifecompliance.components.inspection.models import InspectionUserAction, Inspection
from wildlifecompliance.components.call_email.serializers import LocationSerializer
from wildlifecompliance.components.main.api import save_location
from wildlifecompliance.components.offence.models import Offence, SectionRegulation
from wildlifecompliance.components.offence.serializers import OffenceSerializer, SectionRegulationSerializer, \
    SaveOffenceSerializer, SaveOffenderSerializer, OrganisationSerializer, OffenceDatatableSerializer
from wildlifecompliance.helpers import is_internal


class OffenceFilterBackend(DatatablesFilterBackend):

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        # Storage for the filters
        # Required filters are accumulated here
        # Then issue a query once at last
        q_objects = Q()

        # Filter by the search_text
        search_text = request.GET.get('search[value]')
        if search_text:
            q_objects &= Q(lodgement_number__icontains=search_text) | \
                         Q(identifier__icontains=search_text) | \
                         Q(offender__person__first_name__icontains=search_text) | \
                         Q(offender__person__last_name__icontains=search_text) | \
                         Q(offender__person__email__icontains=search_text) | \
                         Q(offender__organisation__name__icontains=search_text) | \
                         Q(offender__organisation__abn__icontains=search_text) | \
                         Q(offender__organisation__trading_name__icontains=search_text)

        type = request.GET.get('type',).lower()
        if type and type != 'all':
            q_objects &= Q(type=type)

        status = request.GET.get('status',).lower()
        if status and status != 'all':
            q_objects &= Q(status=status)

        # payment_status = request.GET.get('payment_status',).lower()
        # if payment_status and payment_status != 'all':
        #     q_objects &= Q(payment_status=payment_status)

        date_from = request.GET.get('date_from',).lower()
        if date_from:
            date_from = datetime.strptime(date_from, '%d/%m/%Y')
            q_objects &= Q(date_of_issue__gte=date_from)

        date_to = request.GET.get('date_to',).lower()
        if date_to:
            date_to = datetime.strptime(date_to, '%d/%m/%Y')
            q_objects &= Q(date_of_issue__lte=date_to)

        # perform filters
        queryset = queryset.filter(q_objects)

        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        if len(ordering):
            for num, item in enumerate(ordering):
                # offender is the foreign key of the sanction outcome
                if item == 'offender':
                    # offender can be a person or an organisation
                    ordering[num] = 'offender__person'
                    ordering.insert(num + 1, 'offender__organisation')
                elif item == '-offender':
                    ordering[num] = '-offender__person'
                    ordering.insert(num + 1, '-offender__organisation')
                elif item == 'status__name':
                    ordering[num] = 'status'
                elif item == '-status__name':
                    ordering[num] = '-status'
                elif item == 'user_action':
                    pass

            queryset = queryset.order_by(*ordering).distinct()

        setattr(view, '_datatables_total_count', total_count)
        return queryset


class OffencePaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (OffenceFilterBackend,)
    # filter_backends = (DatatablesFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    # renderer_classes = (InspectionRenderer,)
    queryset = Offence.objects.none()
    serializer_class = OffenceDatatableSerializer
    page_size = 10

    def get_queryset(self):
        # user = self.request.user
        if is_internal(self.request):
            return Offence.objects.all()
        return Offence.objects.none()

    @list_route(methods=['GET', ])
    def get_paginated_datatable(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = OffenceDatatableSerializer(result_page, many=True, context={'request': request})
        ret = self.paginator.get_paginated_response(serializer.data)
        return ret


class OffenceViewSet(viewsets.ModelViewSet):
    queryset = Offence.objects.all()
    serializer_class = OffenceSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Offence.objects.all()
        return Offence.objects.none()

    @list_route(methods=['GET', ])
    def types(self, request, *args, **kwargs):
        res_obj = []
        section_regulations = SectionRegulation.objects.all()
        for item in section_regulations:
            res_obj.append({'id': item.id, 'display': item.act + ' ' + item.name});
        res_json = json.dumps(res_obj)
        return HttpResponse(res_json, content_type='application/json')

    @list_route(methods=['GET', ])
    def statuses(self, request, *args, **kwargs):
        res_obj = []
        for choice in Offence.STATUS_CHOICES:
            res_obj.append({'id': choice[0], 'display': choice[1]});
        res_json = json.dumps(res_obj)
        return HttpResponse(res_json, content_type='application/json')

    @list_route(methods=['GET', ])
    def filter_by_call_email(self, request, *args, **kwargs):
        call_email_id = self.request.query_params.get('call_email_id', None)

        try:
            call_email = CallEmail.objects.get(id=call_email_id)
            queryset = self.get_queryset().filter(call_email__exact=call_email)
        except:
            queryset = self.get_queryset()

        serializer = OffenceSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @list_route(methods=['GET', ])
    def filter_by_inspection(self, request, *args, **kwargs):
        inspection_id = self.request.query_params.get('inspection_id', None)

        try:
            inspection = Inspection.objects.get(id=inspection_id)
            queryset = self.get_queryset().filter(inspection__exact=inspection)
        except:
            queryset = self.get_queryset()

        serializer = OffenceSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def update_parent(self, request, instance, *args, **kwargs):
        # Log parent actions and update status, if required
        # If CallEmail
        if instance.call_email:
            instance.call_email.log_user_action(
                    CallEmailUserAction.ACTION_OFFENCE.format(
                    instance.call_email.number), request)
            #instance.call_email.status = 'open_inspection'
            #instance.call_email.save()
        # If Inspection
        elif instance.inspection:
            instance.inspection.log_user_action(
                    InspectionUserAction.ACTION_OFFENCE.format(
                    instance.inspection.number), request)
            #instance.inspection.status = 'open_inspection'
            #instance.inspection.save()

    # @list_route(methods=['POST', ])
    # def offence_save(self, request, *args, **kwargs):
    def create(self, request, *args, **kwargs):
        print(request.data)
        try:
            with transaction.atomic():
                request_data = request.data

                # 1. Save Location
                if (
                    request_data.get('location', {}).get('geometry', {}).get('coordinates', {}) or
                    request_data.get('location', {}).get('properties', {}).get('postcode', {}) or
                    request_data.get('location', {}).get('properties', {}).get('details', {})
                ):
                    location_request_data = request.data.get('location')
                    returned_location = save_location(location_request_data)
                    if returned_location:
                        request_data.update({'location_id': returned_location.get('id')})

                # 2. Save Offence
                serializer = SaveOffenceSerializer(data=request_data)
                serializer.is_valid(raise_exception=True)
                saved_offence_instance = serializer.save()  # Here, relations between this offence and location, and this offence and call_email/inspection are created
                print(serializer.data)

                # 2. Update parents
                self.update_parent(request, saved_offence_instance)
                
                ## 2a. Log it to the call email, if applicable
                #if saved_offence_instance.call_email:
                #    saved_offence_instance.call_email.log_user_action(
                #            CallEmailUserAction.ACTION_OFFENCE.format(
                #                saved_offence_instance.call_email.number),
                #                request)

                ## 2b. Log it to the inspection, if applicable
                #if saved_offence_instance.inspection:
                #    saved_offence_instance.inspection.log_user_action(
                #            InspectionUserAction.ACTION_OFFENCE.format(
                #                saved_offence_instance.inspection.number),
                #                request)

                # 3. Create relations between this offence and the alleged 0ffence(s)
                for dict in request_data['alleged_offences']:
                    alleged_offence = SectionRegulation.objects.get(id=dict['id'])
                    saved_offence_instance.alleged_offences.add(alleged_offence)
                saved_offence_instance.save()

                # 4. Create relations between this offence and offender(s)
                for dict in request_data['offenders']:
                    if dict['data_type'] == 'individual':
                        offender = EmailUser.objects.get(id=dict['id'])
                        serializer_offender = SaveOffenderSerializer(data={'offence_id': saved_offence_instance.id, 'person_id': offender.id})
                        serializer_offender.is_valid(raise_exception=True)
                        serializer_offender.save()
                    elif dict['data_type'] == 'organisation':
                        offender = Organisation.objects.get(id=dict['id'])
                        serializer_offender = SaveOffenderSerializer(data={'offence_id': saved_offence_instance.id, 'organisation_id': offender.id})
                        serializer_offender.is_valid(raise_exception=True)
                        serializer_offender.save()

                # 4. Return Json
                headers = self.get_success_headers(serializer.data)
                return_serializer = OffenceSerializer(instance=saved_offence_instance, context={'request': request})
                # return_serializer = InspectionSerializer(saved_instance, context={'request': request})
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


class SearchSectionRegulation(viewsets.ModelViewSet):
    queryset = SectionRegulation.objects.all()
    serializer_class = SectionRegulationSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('act', 'name', 'offence_text',)


class SearchOrganisation(viewsets.ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('abn', 'name',)
