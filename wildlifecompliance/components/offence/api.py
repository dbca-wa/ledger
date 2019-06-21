import traceback

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import viewsets, filters, serializers, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from ledger.accounts.models import EmailUser
from wildlifecompliance.components.call_email.models import Location
from wildlifecompliance.components.call_email.serializers import LocationSerializer
from wildlifecompliance.components.main.api import save_location
from wildlifecompliance.components.offence.models import Offence, SectionRegulation
from wildlifecompliance.components.offence.serializers import OffenceSerializer, SectionRegulationSerializer, \
    SaveOffenceSerializer, SaveOffenderSerializer
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
                serializer.is_valid(raise_exception=True)
                saved_offence_instance = serializer.save()  # Here, relations between this offence and location, and this offence and call_email are created

                # 3. Create relations between this offence and the alleged 0ffence(s)
                for dict in request_data['alleged_offences']:
                    alleged_offence = SectionRegulation.objects.get(id=dict['id'])
                    saved_offence_instance.alleged_offences.add(alleged_offence)
                saved_offence_instance.save()

                # 4. Create relations between this offence and offender(s)
                for dict in request_data['offenders']:
                    offender = EmailUser.objects.get(id=dict['id'])
                    serializer_offender = SaveOffenderSerializer(data={'offence_id': saved_offence_instance.id, 'person_id': offender.id})
                    serializer_offender.is_valid(raise_exception=True)
                    serializer_offender.save()

                # TODO: log user action

                # 4. Return Json
                headers = self.get_success_headers(serializer.data)
                return_serializer = OffenceSerializer(instance=saved_offence_instance)
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
