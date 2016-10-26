from parkstay.models import CampsiteBooking, Campsite, Campground, Park, PromoArea, Feature, Region, CampsiteClass, Booking, CampsiteRate
from rest_framework import serializers

class ParkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Park

class PromoAreaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
            model = PromoArea

class CampgroundCampsiteFilterSerializer(serializers.Serializer):
    arrival = serializers.DateField(input_formats=['%Y/%m/%d'])
    departure = serializers.DateField(input_formats=['%Y/%m/%d'])
    num_adult = serializers.IntegerField(default=0)
    num_concession = serializers.IntegerField(default=0)
    num_child = serializers.IntegerField(default=0)
    num_infant = serializers.IntegerField(default=0)

class CampgroundSerializer(serializers.HyperlinkedModelSerializer):
    site_type = serializers.SerializerMethodField()
    campground_type = serializers.SerializerMethodField()
    class Meta:
        model = Campground
        fields = (
            'url',
            'id',
            'site_type',
            'campground_type',
            'name',
            'address',
            'contact',
            'park',
            'region',
            'wkb_geometry',
            'description',
            'promo_area',
            'ratis_id',
            'regulations',
            'area_activities',
            'features',
            'driving_directions',
            'bookable_per_site',
            'active',
            #'campfires_allowed',
            'dog_permitted',
            'check_in',
            'check_out',
            'no_booking_start',
            'no_booking_end',
            'min_dba',
            'max_dba'
        )

    def get_site_type(self, obj):
        return dict(Campground.SITE_TYPE_CHOICES).get(obj.site_type)

    def get_campground_type(self, obj):
        return dict(Campground.CAMPGROUND_TYPE_CHOICES).get(obj.campground_type)

class CampsiteSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Campsite
        fields = ('campground', 'name', 'campsite_class', 'features', 'max_people')

class FeatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Feature

class RegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Region

class CampsiteClassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CampsiteClass

class CampsiteBookingSerialiser(serializers.HyperlinkedModelSerializer):
    booking_type = serializers.SerializerMethodField()
    class Meta:
        model = CampsiteBooking
        fields = ('campsite', 'date', 'booking_type')

    def get_booking_type(self, obj):
        return dict(CampsiteBooking.BOOKING_TYPE_CHOICES).get(obj.booking_type)

class BookingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Booking

class CampsiteRateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CampsiteRate
