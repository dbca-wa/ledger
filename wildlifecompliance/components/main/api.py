from wildlifecompliance.components.call_email.models import Location
from wildlifecompliance.components.call_email.serializers import LocationSerializer


def save_location(location_request_data, *args, **kwargs):
    if location_request_data.get('id'):
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
        location_serializer = LocationSerializer(
            data=location_request_data,
            partial=True
        )
        location_serializer.is_valid(raise_exception=True)
        if location_serializer.is_valid():
            location_instance = location_serializer.save()
    return location_serializer.data
