import json
import traceback

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse

from rest_framework import viewsets, serializers
from rest_framework.decorators import list_route

from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome
from wildlifecompliance.components.sanction_outcome.serializers import SanctionOutcomeSerializer, \
    SaveSanctionOutcomeSerializer
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

    @list_route(methods=['POST',])
    def sanction_outcome_save(self, request, *args, **kwargs):

        try:
            with transaction.atomic():
                res_json = {}
                request_data = request.data
                request_data['offence_id'] = request_data['current_offence']['id']
                request_data['offender_id'] = request_data['current_offender']['id']

                # Save sanction outcome (offence, offender, alleged_offences)
                serializer = SaveSanctionOutcomeSerializer(data=request_data)
                serializer.is_valid(raise_exception=True)
                saved_obj = serializer.save()

                # Save sanction outcome document, and link to the sanction outcome

                # Save remediation action, and link to the sanction outcome

                # Load sanction outcome

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

