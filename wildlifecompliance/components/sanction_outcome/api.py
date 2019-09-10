import json
import logging
import traceback

from datetime import datetime

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse

from rest_framework import viewsets, serializers, status
from rest_framework.decorators import list_route, detail_route, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from wildlifecompliance.components.main.api import process_generic_document

from wildlifecompliance.components.call_email.models import CallEmail, CallEmailUserAction
from wildlifecompliance.components.inspection.models import Inspection, InspectionUserAction
from wildlifecompliance.components.main.email import prepare_mail
from wildlifecompliance.components.offence.models import SectionRegulation, AllegedOffence
from wildlifecompliance.components.sanction_outcome.email import send_mail
from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome, RemediationAction, \
    SanctionOutcomeCommsLogEntry, AllegedCommittedOffence
from wildlifecompliance.components.sanction_outcome.serializers import SanctionOutcomeSerializer, \
    SaveSanctionOutcomeSerializer, SaveRemediationActionSerializer, SanctionOutcomeDatatableSerializer, \
    UpdateAssignedToIdSerializer, SanctionOutcomeCommsLogEntrySerializer, SanctionOutcomeUserActionSerializer
from wildlifecompliance.components.users.models import CompliancePermissionGroup, RegionDistrict
from wildlifecompliance.helpers import is_internal

logger = logging.getLogger('compliancemanagement')


class SanctionOutcomeFilterBackend(DatatablesFilterBackend):

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

    def retrieve(self, request, *args, **kwargs):
        """
        Get existing sanction outcome
        """
        return super(SanctionOutcomeViewSet, self).retrieve(request, *args, **kwargs)

    def get_compliance_permission_groups(self, region_district_id, workflow_type):
        """
        Determine which CompliancePermissionGroup this sanction outcome should belong to
        :param region_district_id: The regionDistrict id this sanction outcome is in
        :param workflow_type: string like 'send_to_manager', 'return_to_officer', ...
        :return: CompliancePermissionGroup quersyet
        """
        # 1. Determine regionDistrict of this sanction outcome
        region_district = RegionDistrict.objects.filter(id=region_district_id)

        # 2. Determine which permission(s) is going to be apllied
        compliance_content_type = ContentType.objects.get(model="compliancepermissiongroup")
        codename = 'officer'
        if workflow_type == SanctionOutcome.WORKFLOW_SEND_TO_MANAGER:
            codename = 'manager'
        elif workflow_type == SanctionOutcome.WORKFLOW_DECLINE:
            codename = '---'
        elif workflow_type == SanctionOutcome.WORKFLOW_ENDORSE:
            codename = 'infringement_notice_coordinator'
        elif workflow_type == SanctionOutcome.WORKFLOW_RETURN_TO_OFFICER:
            codename = 'officer'
        elif workflow_type == SanctionOutcome.WORKFLOW_WITHDRAW:
            codename = '---'
        elif workflow_type == SanctionOutcome.WORKFLOW_CLOSE:
            codename = '---'
        else:
            # Should not reach here
            # instance.save()
            pass

        permissions = Permission.objects.filter(codename=codename, content_type_id=compliance_content_type.id)

        # 3. Find groups which has the permission(s) determined above in the regionDistrict.
        groups = CompliancePermissionGroup.objects.filter(region_district__in=region_district, permissions__in=permissions)

        return groups

    @detail_route(methods=['POST', ])
    @renderer_classes((JSONRenderer,))
    def update_assigned_to_id(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            validation_serializer = SanctionOutcomeSerializer(instance, context={'request': request})
            user_in_group = validation_serializer.data.get('user_in_group')

            if user_in_group:
                # current user is in the group
                if request.data.get('current_user'):
                    # current user is going to assign him or herself to the object
                    serializer_partial = UpdateAssignedToIdSerializer(instance=instance, data={'assigned_to_id': request.user.id,})
                else:
                    # current user is going to assign someone else to the object
                    serializer_partial = UpdateAssignedToIdSerializer(instance=instance, data=request.data)

                if serializer_partial.is_valid(raise_exception=True):
                    # Update only assigned_to_id data
                    serializer_partial.save()

                # Construct return value
                return_serializer = SanctionOutcomeSerializer(instance=instance, context={'request': request})
                headers = self.get_success_headers(return_serializer.data)
                return Response(return_serializer.data, status=status.HTTP_200_OK, headers=headers)
            else:
                return Response(validation_serializer.data, status=status.HTTP_200_OK)

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
            serializer = SanctionOutcomeUserActionSerializer(qs, many=True)
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
            serializer = SanctionOutcomeCommsLogEntrySerializer(qs, many=True)
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

    def update(self, request, *args, **kwargs):
        """
        Update existing sanction outcome
        """
        try:
            with transaction.atomic():
                instance = self.get_object()
                request_data = request.data

                # Offence should not be changed
                # Offender
                request_data['offender_id'] = request_data.get('current_offender', {}).get('id', None);

                # No workflow
                # No allocated group changes

                serializer = SaveSanctionOutcomeSerializer(instance, data=request_data, partial=True)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()

                # Handle relations between this sanction outcome and the alleged offence(s)

                # Save remediation action, and link to the sanction outcome

                # Log

                # Action

                # Return

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
        """
        Create new sanction outcome from the modal
        """
        try:
            with transaction.atomic():
                res_json = {}

                request_data = request.data

                # offence and offender
                request_data['offence_id'] = request_data.get('current_offence', {}).get('id', None);
                request_data['offender_id'] = request_data.get('current_offender', {}).get('id', None);

                # workflow
                workflow_type = request_data.get('workflow_type', '')

                # allocated group
                regionDistrictId = request_data['district_id'] if request_data['district_id'] else request_data['region_id']
                groups = self.get_compliance_permission_groups(regionDistrictId, workflow_type)
                if groups.count() == 1:
                    group = groups.first()
                elif groups.count() > 1:
                    group = groups.first()
                request_data['allocated_group_id'] = group.id

                # Save sanction outcome (offence, offender, alleged_offences)
                if hasattr(request_data, 'id') and request_data['id']:
                    instance = SanctionOutcome.objects.get(id=request_data['id'])
                    serializer = SaveSanctionOutcomeSerializer(instance, data=request_data, partial=True)
                else:
                    serializer = SaveSanctionOutcomeSerializer(data=request_data, partial=True)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()

                # Create relations between this sanction outcome and the alleged offence(s)
                for id in request_data['alleged_offence_ids_included']:
                    try:
                        alleged_offence = AllegedOffence.objects.get(id=id)
                        alleged_commited_offence = AllegedCommittedOffence.objects.create(sanction_outcome=instance, alleged_offence=alleged_offence, included=True)
                    except:
                        pass  # Should not reach here

                for id in request_data['alleged_offence_ids_excluded']:
                    try:
                        alleged_offence = AllegedOffence.objects.get(id=id)
                        alleged_commited_offence = AllegedCommittedOffence.objects.create(sanction_outcome=instance, alleged_offence=alleged_offence, included=False)
                    except:
                        pass  # Should not reach here

                # Handle workflow
                if workflow_type == SanctionOutcome.WORKFLOW_SEND_TO_MANAGER:
                    instance.send_to_manager(request)
                elif not workflow_type:
                    instance.save()

                # Save remediation action, and link to the sanction outcome
                for dict in request_data['remediation_actions']:
                    dict['sanction_outcome_id'] = instance.id
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

                # Create/Retrieve comms log entry
                comms_log_id = request.data.get('comms_log_id')
                if comms_log_id and comms_log_id is not 'null':
                    workflow_entry = instance.comms_logs.get(id=comms_log_id)
                else:
                    workflow_entry = self.add_comms_log(request, instance, workflow=True)

                # Update the entry above with email_data
                email_data = prepare_mail(request, instance, workflow_entry, send_mail)
                serializer = SanctionOutcomeCommsLogEntrySerializer(instance=workflow_entry, data=email_data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

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

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def workflow_action(self, request, instance=None, *args, **kwargs):
        try:
            with transaction.atomic():
                if not instance:
                    instance = self.get_object()

                comms_log_id = request.data.get('comms_log_id')
                if comms_log_id and comms_log_id is not 'null':
                    workflow_entry = instance.comms_logs.get(id=comms_log_id)
                else:
                    workflow_entry = self.add_comms_log(request, instance, workflow=True)

                # Set status
                workflow_type = request.data.get('workflow_type')
                if workflow_type == SanctionOutcome.WORKFLOW_SEND_TO_MANAGER:
                    instance.send_to_manager(request)
                elif workflow_type == SanctionOutcome.WORKFLOW_DECLINE:
                    instance.decline(request)
                elif workflow_type == SanctionOutcome.WORKFLOW_ENDORSE:
                    instance.endorse(request)
                elif workflow_type == SanctionOutcome.WORKFLOW_RETURN_TO_OFFICER:
                    instance.return_to_officer(request)
                elif workflow_type == SanctionOutcome.WORKFLOW_WITHDRAW:
                    instance.withdraw(request)
                else:
                    # Should not reach here
                    # instance.save()
                    pass

                # Log parent actions and update status
                # self.update_parent(request, instance)

                # if instance.assigned_to_id:
                #     instance = self.modify_inspection_team(request, instance, workflow=True, user_id=instance.assigned_to_id)

                # Send email and Log it
                email_data = prepare_mail(request, instance, workflow_entry, send_mail)
                serializer = SanctionOutcomeCommsLogEntrySerializer(instance=workflow_entry, data=email_data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

                return_serializer = SanctionOutcomeSerializer(instance=instance, context={'request': request})
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
    def add_comms_log(self, request, instance=None, workflow=False, *args, **kwargs):
        try:
            with transaction.atomic():
                # create sanction outcome instance if not passed to this method
                if not instance:
                    instance = self.get_object()
                # add sanction outcome attribute to request_data
                request_data = request.data.copy()
                request_data['sanction_outcome'] = u'{}'.format(instance.id)
                if request_data.get('comms_log_id'):
                    comms = SanctionOutcomeCommsLogEntry.objects.get(
                        id=request_data.get('comms_log_id')
                    )
                    serializer = SanctionOutcomeCommsLogEntrySerializer(
                        instance=comms,
                        data=request.data)
                else:
                    serializer = SanctionOutcomeCommsLogEntrySerializer(
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
