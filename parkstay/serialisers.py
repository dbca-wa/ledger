from parkstay.models import CampsiteBooking,CampgroundBookingRange, Campsite, Campground, Park, PromoArea, Feature, Region, CampsiteClass, Booking, CampsiteRate, Contact
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

class BookingRangeSerializer(serializers.ModelSerializer):
    min_days = serializers.IntegerField(required=False,default=1)
    max_days = serializers.IntegerField(required=False,default=28)
    # Minimum and Maximum days that a booking can be made before arrival
    min_dba = serializers.IntegerField(required=False,default=0)
    max_dba = serializers.IntegerField(required=False,default=180)

    details = serializers.CharField(required=False)
    range_start = serializers.DateField(input_formats=['%d/%m/%Y'])
    range_end = serializers.DateField(input_formats=['%d/%m/%Y'],required=False)
    

class CampgroundBookingRangeSerializer(BookingRangeSerializer):
    # minimum/maximum number of campsites allowed for a booking
    min_sites = serializers.IntegerField(required=False,default=1)
    max_sites = serializers.IntegerField(required=False,default=12)
    
    class Meta:
        model = CampgroundBookingRange
        fields = (
            'id',
            'status',
            'range_start',
            'range_end',
            'details',
            'editable',
            'min_days',
            'max_days',
            'min_sites',
            'max_sites',
            'min_dba',
            'max_dba',
            'campground'
        )
        write_only_fields = (
            'campground'
        )
    def get_status(self, obj):
        return dict(CampgroundBookingRange.BOOKING_RANGE_CHOICES).get(obj.status)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop("method")
        except:
            method = 'get'
        super(CampgroundBookingRangeSerializer, self).__init__(*args, **kwargs)
        if method == 'post':
            self.fields['status'] = serializers.ChoiceField(choices=CampgroundBookingRange.BOOKING_RANGE_CHOICES)
        else:
            self.fields['status'] = serializers.SerializerMethodField()


class CampsiteBookingRangeSerializer(BookingRangeSerializer):
    
    class Meta:
        model = CampgroundBookingRange
        fields = (
            'id',
            'status',
            'range_start',
            'range_end',
            'details',
            'editable',
            'min_days',
            'max_days',
            'min_dba',
            'max_dba',
            'campsite'
        )
        write_only_fields = (
            'campsite'
        )
    def get_status(self, obj):
        return dict(CampsiteBookingRange.BOOKING_RANGE_CHOICES).get(obj.status)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop("method")
        except:
            method = 'get'
        super(CampgsiteBookingRangeSerializer, self).__init__(*args, **kwargs)
        if method == 'post':
            self.fields['status'] = serializers.ChoiceField(choices=CampsiteBookingRange.BOOKING_RANGE_CHOICES)
        else:
            self.fields['status'] = serializers.SerializerMethodField()

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('name','phone_number')

class CampgroundSerializer(serializers.HyperlinkedModelSerializer):
    site_type = serializers.SerializerMethodField()
    campground_type = serializers.SerializerMethodField()
    contact = ContactSerializer()
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
            'area_activities',
            'features',
            'driving_directions',
            'bookable_per_site',
            'active',
            'current_closure',
            #'campfires_allowed',
            'dog_permitted',
            'check_in',
            'check_out',
        )

    def get_site_type(self, obj):
        return dict(Campground.SITE_TYPE_CHOICES).get(obj.site_type)

    def get_campground_type(self, obj):
        return dict(Campground.CAMPGROUND_TYPE_CHOICES).get(obj.campground_type)

class CampsiteSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Campsite
        fields = ('id','campground', 'name', 'type','price', 'features', 'wkb_geometry')

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
