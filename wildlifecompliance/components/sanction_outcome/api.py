import json
import traceback

from datetime import datetime

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse

from rest_framework import viewsets, serializers
from rest_framework.decorators import list_route, detail_route, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from wildlifecompliance.components.main.api import process_generic_document

from wildlifecompliance.components.call_email.models import CallEmail, CallEmailUserAction
from wildlifecompliance.components.inspection.models import Inspection, InspectionUserAction
from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome, RemediationAction
from wildlifecompliance.components.sanction_outcome.serializers import SanctionOutcomeSerializer, \
    SaveSanctionOutcomeSerializer, SaveRemediationActionSerializer, SanctionOutcomeDatatableSerializer
from wildlifecompliance.components.users.models import CompliancePermissionGroup, RegionDistrict
from wildlifecompliance.helpers import is_internal


class SanctionOutcomeFilterBackend(DatatablesFilterBackend):

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        # Storage for the filters
        q_objects = Q()

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

        region_id = request.GET.get('region_id',).lower()
        if region_id and region_id != 'all':
            q_objects &= Q(region__id=region_id)

        district_id = request.GET.get('district_id',).lower()
        if district_id and district_id != 'all':
            q_objects &= Q(district__id=district_id)

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


class SanctionOutcomePaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (SanctionOutcomeFilterBackend,)
    # filter_backends = (DatatablesFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    # renderer_classes = (InspectionRenderer,)
    queryset = SanctionOutcome.objects.none()
    serializer_class = SanctionOutcomeDatatableSerializer
    page_size = 10

    def get_queryset(self):
        # user = self.request.user
        if is_internal(self.request):
            return SanctionOutcome.objects.all()
        return SanctionOutcome.objects.none()

    @list_route(methods=['GET', ])
    def get_paginated_datatable(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)
        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = SanctionOutcomeDatatableSerializer(result_page, many=True, context={'request': request})
        ret = self.paginator.get_paginated_response(serializer.data)
        return ret


class SanctionOutcomeViewSet(viewsets.ModelViewSet):
    queryset = SanctionOutcome.objects.all()
    serializer_class = SanctionOutcomeSerializer

    def get_queryset(self):
        # user = self.request.user
        if is_internal(self.request):
            return SanctionOutcome.objects.all()
        return SanctionOutcome.objects.none()

    @list_route(methods=['GET', ])
    def types(self, request, *args, **kwargs):
        res_obj = []
        for choice in SanctionOutcome.TYPE_CHOICES:
            res_obj.append({'id': choice[0], 'display': choice[1]});
        res_json = json.dumps(res_obj)
        return HttpResponse(res_json, content_type='application/json')

    @list_route(methods=['GET', ])
    def statuses(self, request, *args, **kwargs):
        res_obj = []
        for choice in SanctionOutcome.STATUS_CHOICES:
            res_obj.append({'id': choice[0], 'display': choice[1]});
        res_json = json.dumps(res_obj)
        return HttpResponse(res_json, content_type='application/json')

    def create(self, request, *args, **kwargs):
        serializer = SaveSanctionOutcomeSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

    @list_route(methods=['POST',])
    def sanction_outcome_save(self, request, *args, **kwargs):

        try:
            with transaction.atomic():
                res_json = {}

                request_data = request.data

                # offence and offender
                request_data['offence_id'] = request_data.get('current_offence', {}).get('id', None);
                request_data['offender_id'] = request_data.get('current_offender', {}).get('id', None);

                # Retrieve group
                regionDistrictId = request_data['district_id'] if request_data['district_id'] else request_data['region_id']
                region_district = RegionDistrict.objects.get(id=regionDistrictId)
                compliance_content_type = ContentType.objects.get(model="compliancepermissiongroup")
                permission = Permission.objects.filter(codename='manager').filter(content_type_id=compliance_content_type.id).first()
                group = CompliancePermissionGroup.objects.filter(region_district=region_district).filter(permissions=permission).first()
                request_data['allocated_group_id'] = group.id

                # Save sanction outcome (offence, offender, alleged_offences)
                if hasattr(request_data, 'id') and request_data['id']:
                    instance = SanctionOutcome.objects.get(id=request_data['id'])
                    serializer = SaveSanctionOutcomeSerializer(instance, data=request_data, partial=True)
                else:
                    serializer = SaveSanctionOutcomeSerializer(data=request_data, partial=True)
                serializer.is_valid(raise_exception=True)
                saved_obj = serializer.save()

                # if request_data.get('set_sequence'):
                #     # Only when requested, we generate a new lodgement number
                #     saved_obj.set_sequence()
                #     saved_obj.save()

                # Save remediation action, and link to the sanction outcome
                for dict in request_data['remediation_actions']:
                    dict['sanction_outcome_id'] = saved_obj.id
                    remediation_action = SaveRemediationActionSerializer(data=dict)
                    if remediation_action.is_valid(raise_exception=True):
                        remediation_action.save()

                # Log CallEmail action
                if request_data.get('call_email_id'):
                    call_email = CallEmail.objects.get(id=request_data.get('call_email_id'))
                    call_email.log_user_action(CallEmailUserAction.ACTION_SANCTION_OUTCOME.format(call_email.number), request)

                # Log Inspection action
                if request_data.get('inspection_id'):
                    inspection = Inspection.objects.get(id=request_data.get('inspection_id'))
                    inspection.log_user_action(InspectionUserAction.ACTION_SANCTION_OUTCOME.format(inspection.number), request)
                # Return
                return HttpResponse(res_json, content_type='application/json')

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
    def process_default_document(self, request, *args, **kwargs):
        """
        Request sent from the immediate file uploader comes here for both saving and canceling.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        print("process_default_document")
        print(request.data)
        try:
            instance = self.get_object()
            # process docs
            returned_data = process_generic_document(request, instance)
            # delete Sanction Outcome if user cancels modal
            action = request.data.get('action')
            if action == 'cancel' and returned_data:
                instance.status = 'discarded'  # We don't want to delete the instance for audit purpose.
                returned_data = instance.save()
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

    @list_route(methods=['GET', ])
    def datatable_list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = SanctionOutcomeSerializer(qs, many=True, context={'request': request})
            return Response({ 'tableData': serializer.data })
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


