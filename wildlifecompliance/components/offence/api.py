import traceback

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import viewsets, filters, serializers, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from wildlifecompliance.components.call_email.models import Location
from wildlifecompliance.components.call_email.serializers import LocationSerializer
from wildlifecompliance.components.main.api import save_location
from wildlifecompliance.components.offence.models import Offence, SectionRegulation
from wildlifecompliance.components.offence.serializers import OffenceSerializer, SectionRegulationSerializer, \
    SaveOffenceSerializer
from wildlifecompliance.helpers import is_internal


class OffenceViewSet(viewsets.ModelViewSet):
    queryset = Offence.objects.all()
    serializer_class = OffenceSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Offence.objects.all()
        return Offence.objects.none()


    @list_route(methods=['POST', ])
    def offence_save(self, request, *args, **kwargs):
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
                if serializer.is_valid():
                    # Here, relations between this offence and location, and this offence and call_email are created
                    saved_offence_instance = serializer.save()

                    # 3. Create relations between this offence and the alleged 0ffence(s)
                    for dict in request_data['alleged_offences']:
                        alleged_offence = SectionRegulation.objects.get(id=dict['id'])
                        saved_offence_instance.alleged_offences.add(alleged_offence)
                    saved_offence_instance.save()

                    # 4. Create relations between this offence and offender(s)

                    # TODO: log user action

                    # 4. Return Json
                    headers = self.get_success_headers(serializer.data)
                    return_serializer = OffenceSerializer(instance=saved_offence_instance)
                    return Response(
                        return_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers
                    )
                else:
                    pass

                # if request_data.get('renderer_data'):
                #     self.form_data(request)
                #
                # if request_data.get('report_type'):
                #     request_data.update({'report_type_id': request_data.get('report_type', {}).get('id')})
                #
                # serializer = SaveCallEmailSerializer(instance, data=request_data)
                # serializer.is_valid(raise_exception=True)
                # if serializer.is_valid():
                #     saved_instance = serializer.save()
                #     instance.log_user_action(
                #         ComplianceUserAction.ACTION_SAVE_CALL_EMAIL_.format(
                #             instance.number), request)
                #     headers = self.get_success_headers(serializer.data)
                #     return_serializer = CallEmailSerializer(instance=saved_instance)
                #     return Response(
                #         return_serializer.data,
                #         status=status.HTTP_201_CREATED,
                #         headers=headers
                #     )

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
