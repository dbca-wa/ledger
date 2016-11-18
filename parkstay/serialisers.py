from parkstay.models import CampsiteStayHistory,District, CampsiteBooking,CampsiteBookingRange,CampgroundBookingRange, Campsite, Campground, Park, PromoArea, Feature, Region, CampsiteClass, Booking, CampsiteRate, Contact
from rest_framework import serializers

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District

class ParkSerializer(serializers.HyperlinkedModelSerializer):
    district = DistrictSerializer()
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

    details = serializers.CharField(required=False)
    range_start = serializers.DateField(input_formats=['%d/%m/%Y'])
    range_end = serializers.DateField(input_formats=['%d/%m/%Y'],required=False)
    

class CampgroundBookingRangeSerializer(BookingRangeSerializer):
    
    class Meta:
        model = CampgroundBookingRange
        fields = (
            'id',
            'status',
            'range_start',
            'range_end',
            'details',
            'editable',
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
        try:
            original = kwargs.pop("original")
        except:
            original = False;
        super(CampgroundBookingRangeSerializer, self).__init__(*args, **kwargs)
        if method == 'post':
            self.fields['status'] = serializers.ChoiceField(choices=CampgroundBookingRange.BOOKING_RANGE_CHOICES)
        elif method == 'get':
            if not original:
                self.fields['status'] = serializers.SerializerMethodField()
            else:
                self.fields['range_start'] = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'])
                self.fields['range_end'] = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'],required=False)


class CampsiteBookingRangeSerializer(BookingRangeSerializer):
    
    class Meta:
        model = CampsiteBookingRange
        fields = (
            'id',
            'status',
            'range_start',
            'range_end',
            'details',
            'editable',
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
        super(CampsiteBookingRangeSerializer, self).__init__(*args, **kwargs)
        if method == 'post':
            self.fields['status'] = serializers.ChoiceField(choices=CampsiteBookingRange.BOOKING_RANGE_CHOICES)
        else:
            self.fields['status'] = serializers.SerializerMethodField()

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('name','phone_number')

class FeatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Feature
        fields = ('url','id','name','description','image')

class CampgroundSerializer(serializers.HyperlinkedModelSerializer):
    address = serializers.JSONField()
    contact = ContactSerializer(required=False)
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
            'price_level',
            'description',
            'promo_area',
            'ratis_id',
            'area_activities',
            'features',
            'driving_directions',
            'bookable_per_site',
            'active',
            'current_closure',
            'campfires_allowed',
            'dog_permitted',
            'check_in',
            'check_out',
        )

    def get_site_type(self, obj):
        return dict(Campground.SITE_TYPE_CHOICES).get(obj.site_type)

    def get_address(self, obj):
        if not obj.address:
            return {}
        return obj.address

    def get_price_level(self, obj):
        return dict(Campground.CAMPGROUND_PRICE_LEVEL_CHOICES).get(obj.price_level)

    def get_campground_type(self, obj):
        return dict(Campground.CAMPGROUND_TYPE_CHOICES).get(obj.campground_type)

    def __init__(self, *args, **kwargs):
        try:
            formatted = bool(kwargs.pop('formatted'))
        except:
            formatted = False
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        super(CampgroundSerializer, self).__init__(*args, **kwargs)
        if formatted:
            self.fields['site_type'] = serializers.SerializerMethodField()
            self.fields['campground_type'] = serializers.SerializerMethodField()
            self.fields['price_level'] = serializers.SerializerMethodField()
        if method == 'get':
            self.fields['features'] = FeatureSerializer(many=True)
            self.fields['address'] = serializers.SerializerMethodField()

class CampsiteStayHistorySerializer(serializers.ModelSerializer):
    details = serializers.CharField(required=False)
    range_start = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'])
    range_end = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'],required=False)
    class Meta:
        model = CampsiteStayHistory
        fields = ('id','created','range_start','range_end','min_days','max_days','min_dba','max_dba','details','campsite','editable')

class CampsiteSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Campsite
        fields = ('id','campground', 'name', 'type','price', 'features', 'wkb_geometry','campground_open','active', 'current_closure')

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
