from django.conf import settings
from parkstay.models import (   CampgroundPriceHistory,
                                CampsiteClassPriceHistory,
                                Rate,
                                CampsiteStayHistory,
                                District,
                                CampsiteBooking,
                                BookingRange,
                                CampsiteBookingRange,
                                CampgroundBookingRange,
                                Campsite,
                                Campground,
                                Park,
                                PromoArea,
                                Feature,
                                Region,
                                CampsiteClass,
                                Booking,
                                CampsiteRate,
                                Contact,
                                CampgroundImage,
                                ClosureReason,
                                OpenReason,
                                PriceReason,
                                MaximumStayReason
                            )
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

    def get_status(self, obj):
        return dict(BookingRange.BOOKING_RANGE_CHOICES).get(obj.status)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop("method")
        except:
            method = 'get'
        try:
            original = kwargs.pop("original")
        except:
            original = False;
        super(BookingRangeSerializer, self).__init__(*args, **kwargs)
        if method == 'post':
            self.fields['status'] = serializers.ChoiceField(choices=BookingRange.BOOKING_RANGE_CHOICES)
        elif method == 'get':
            if not original:
                self.fields['status'] = serializers.SerializerMethodField()
            else:
                self.fields['range_start'] = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'])
                self.fields['range_end'] = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'],required=False)

class CampgroundBookingRangeSerializer(BookingRangeSerializer):

    class Meta:
        model = CampgroundBookingRange
        fields = (
            'id',
            'status',
            'closure_reason',
            'open_reason',
            'range_start',
            'range_end',
            'reason',
            'details',
            'editable',
            'campground'
        )
        read_only_fields = ('reason',)
        write_only_fields = (
            'campground'
        )

class CampsiteBookingRangeSerializer(BookingRangeSerializer):

    class Meta:
        model = CampsiteBookingRange
        fields = (
            'id',
            'status',
            'closure_reason',
            'open_reason',
            'range_start',
            'range_end',
            'reason',
            'details',
            'editable',
            'campsite'
        )
        read_only_fields = ('reason',)
        write_only_fields = (
            'campsite'
        )

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('name','phone_number')

class FeatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Feature
        fields = ('url','id','name','description','image')

class CampgroundImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=17)

    def get_image(self, obj):
        return self.context['request'].build_absolute_uri('/media{}'.format(obj.image.url.split(settings.MEDIA_ROOT)[1]))

    class Meta:
        model = CampgroundImage
        fields = ('id','image','campground')
        read_only_fields = ('id',)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        super(CampgroundImageSerializer, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['image'] = serializers.SerializerMethodField()

class ExistingCampgroundImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    image = serializers.URLField()
    class Meta:
        model = CampgroundImage
        fields = ('id','image','campground')
    

class CampgroundSerializer(serializers.HyperlinkedModelSerializer):
    address = serializers.JSONField()
    contact = ContactSerializer(required=False)
    images = CampgroundImageSerializer(many=True,required=False)
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
            'active',
            'current_closure',
            'campfires_allowed',
            'dog_permitted',
            'check_in',
            'check_out',
            'images'
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
            self.fields['images'] = CampgroundImageSerializer(many=True,required=False,method='get')

class CampsiteStayHistorySerializer(serializers.ModelSerializer):
    details = serializers.CharField(required=False)
    range_start = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'])
    range_end = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'],required=False)
    class Meta:
        model = CampsiteStayHistory
        fields = ('id','created','range_start','range_end','min_days','max_days','min_dba','max_dba','reason','details','campsite','editable')
        read_only_fields =('editable',)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        super(CampsiteStayHistorySerializer, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['reason'] = serializers.CharField(source='reason.text')

class CampsiteSerialiser(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(default='default',required=False)
    class Meta:
        model = Campsite
        fields = ('id','campground', 'name', 'type','campsite_class','price','features','wkb_geometry','campground_open','active','current_closure','can_add_rate','tents','parking_spaces','number_vehicles','min_people','max_people','dimensions','cs_tents','cs_parking_spaces','cs_number_vehicles','cs_min_people','cs_max_people','cs_dimensions')
        extra_kwargs = {'cs_tents': {'write_only': True},'cs_parking_spaces': {'write_only': True},'cs_number_vehicles': {'write_only': True},'cs_min_people': {'write_only': True},'cs_max_people': {'write_only': True},'cs_dimensions': {'write_only': True}}
        read_only_fields = ('tents','parking_spaces','number_vehicles','min_people','max_people','dimensions')

    def __init__(self, *args, **kwargs):
        try:
            formatted = bool(kwargs.pop('formatted'))
        except:
            formatted = False
        try:
            method = kwargs.pop('method')
        except:
            method = 'put'
        super(CampsiteSerialiser, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['features'] = FeatureSerializer(many=True)
        elif method == 'post':
            self.fields['features'] = serializers.HyperlinkedRelatedField(many=True,read_only=True,required=False,view_name='features-detail')
        elif method == 'put':
            self.fields['features'] = serializers.HyperlinkedRelatedField(many=True,allow_empty=True, queryset=Feature.objects.all(),view_name='feature-detail')

class RegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Region

class CampsiteClassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CampsiteClass
        fields = ('url','id','name','tents','parking_spaces','number_vehicles','min_people','max_people','dimensions','features','deleted','can_add_rate','campsites')
        read_only_fields = ('campsites','can_add_rate',)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        super(CampsiteClassSerializer, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['features'] = FeatureSerializer(many=True)
        elif method == 'post':
            self.fields['features'] = serializers.HyperlinkedRelatedField(required=False,many=True,allow_empty=True, queryset=Feature.objects.all(),view_name='feature-detail')

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

class RateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rate
        fields = ('url','id','adult','concession','child','infant','name')

class CampsiteRateSerializer(serializers.ModelSerializer):
    date_start = serializers.DateField(format='%d/%m/%Y')
    details = serializers.CharField(required=False)
    class Meta:
        model = CampsiteRate
        read_only_fields = ('date_end',)

class CampsiteRateReadonlySerializer(serializers.ModelSerializer):
    adult = serializers.DecimalField(max_digits=5, decimal_places=2,source='rate.adult')
    concession = serializers.DecimalField(max_digits=5, decimal_places=2,source='rate.concession')
    child = serializers.DecimalField(max_digits=5, decimal_places=2,source='rate.child')
    class Meta:
        model = CampsiteRate
        fields = ('id','adult','concession','child','date_start','date_end','rate','editable','deletable','update_level')

class RateDetailSerializer(serializers.Serializer):
    '''Used to validate rates from the frontend
    '''
    rate = serializers.IntegerField(required=False)
    adult = serializers.DecimalField(max_digits=5, decimal_places=2)
    concession = serializers.DecimalField(max_digits=5, decimal_places=2)
    child = serializers.DecimalField(max_digits=5, decimal_places=2)
    period_start = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'])
    reason = serializers.IntegerField()
    details = serializers.CharField(required=False)
    campsite = serializers.IntegerField(required=False)


    def validate_rate(self, value):
        if value:
            try:
                Rate.objects.get(id=value)
            except Rate.DoesNotExist:
                raise serializers.ValidationError('This rate does not exist')
        return value

class CampgroundPriceHistorySerializer(serializers.ModelSerializer):
    date_end = serializers.DateField(required=False)
    class Meta:
        model = CampgroundPriceHistory
        fields = ('id','date_start','date_end','rate_id','adult','concession','child','editable','deletable')
        read_only_fields = ('id','editable','deletable','adult','concession','child')

class CampsiteClassPriceHistorySerializer(serializers.ModelSerializer):
    date_end = serializers.DateField(required=False)
    class Meta:
        model = CampsiteClassPriceHistory
        fields = ('id','date_start','date_end','rate_id','adult','concession','child','editable','deletable')
        read_only_fields = ('id','editable','deletable','adult','concession','child')

# Reasons
# ============================
class ClosureReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClosureReason
        fields = ('id','text')

class OpenReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenReason
        fields = ('id','text')

class PriceReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceReason
        fields = ('id','text')

class MaximumStayReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaximumStayReason
        fields = ('id','text')
