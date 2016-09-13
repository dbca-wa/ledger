from parkstay.models import CampsiteBooking, Campsite, Campground, Park
from rest_framework import serializers

class CampsiteBookingSerialiser(Serializer.HyperlinkedModelSerializer)
    class Meta:
        model = CampsiteBooking
        fields = ('campsite', 'date', 'booking_type')

class CampsiteSerialiser(Serializer.HyperlinkedModelSerializer)
    class Meta:
        model = Campsite
        fields = ('campground', 'name', 'campsite_class', 'features', 'max_people')
"""
class CampgroundSerialiser((Serializer.HyperlinkedModelSerializer)
    class Meta:
        model = Campground
        fields = ('', '', '', '', '')
"""
