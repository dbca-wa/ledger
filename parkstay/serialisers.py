from parkstay.models import CampsiteBooking, Campsite, Campground, Park, PromoArea, CampgroundFeature, Region, CampsiteClass, Booking, CampsiteRate
from rest_framework import serializers

class ParkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Park

class PromoAreaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
            model = PromoArea

class CampgroundSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Campground

class CampsiteSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Campsite
        fields = ('campground', 'name', 'campsite_class', 'features', 'max_people')

class CampgroundFeatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
                model = CampgroundFeature

class RegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
                model = Region

class CampsiteClassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
                model = CampsiteClass

class CampsiteBookingSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CampsiteBooking
        fields = ('campsite', 'date', 'booking_type')

class BookingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
                model = Booking

class CampsiteRateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
                model = CampsiteRate
