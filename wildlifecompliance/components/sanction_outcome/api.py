import json
import traceback

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse

from rest_framework import viewsets, serializers
from rest_framework.decorators import list_route, detail_route, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from wildlifecompliance.components.main.api import process_generic_document

from wildlifecompliance.components.call_email.models import CallEmail, CallEmailUserAction
from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome, RemediationAction
from wildlifecompliance.components.sanction_outcome.serializers import SanctionOutcomeSerializer, \
    SaveSanctionOutcomeSerializer, SaveRemediationActionSerializer
from wildlifecompliance.components.users.models import CompliancePermissionGroup, RegionDistrict
from wildlifecompliance.helpers import is_internal


class SanctionOutcomeViewSet(viewsets.ModelViewSet):
    queryset = SanctionOutcome.objects.all()
    serializer_class = SanctionOutcomeSerializer

    def get_queryset(self):
        user = self.request.user
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
                serializer = SaveSanctionOutcomeSerializer(data=request_data)
                serializer.is_valid(raise_exception=True)
                saved_obj = serializer.save()

                # Save sanction outcome document, and link to the sanction outcome

                # Save remediation action, and link to the sanction outcome
                for dict in request_data['remediation_actions']:
                    dict['sanction_outcome_id'] = saved_obj.id
                    remediation_action = SaveRemediationActionSerializer(data=dict)
                    if remediation_action.is_valid(raise_exception=True):
                        remediation_action.save()

                # Log action
                if request_data['call_email_id']:
                    call_email = CallEmail.objects.get(id=request_data['call_email_id'])
                    call_email.log_user_action(CallEmailUserAction.ACTION_SANCTION_OUTCOME.format(call_email.number), request)

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
        print("process_default_document")
        print(request.data)
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
