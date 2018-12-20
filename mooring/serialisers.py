from django.conf import settings
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from mooring.models import (MooringAreaPriceHistory,
                                MooringsiteClassPriceHistory,
                                Rate,
                                MooringsiteStayHistory,
                                District,
                                MooringsiteBooking,
                                BookingRange,
                                MooringAreaImage,
                                MooringsiteBookingRange,
                                MooringAreaBookingRange,
                                Mooringsite,
                                MooringArea,
                                MooringAreaGroup,
                                MarinePark,
                                PromoArea,
                                Feature,
                                Region,
                                MooringsiteClass,
                                Booking,
                                MooringsiteRate,
                                Contact,
                                MooringAreaImage,
                                ClosureReason,
                                OpenReason,
                                PriceReason,
                                MaximumStayReason,
                                MooringAreaStayHistory,
                                MarinaEntryRate,
                                BookingVehicleRego,
                                BookingHistory,
                           )
from rest_framework import serializers
import rest_framework_gis.serializers as gis_serializers
from drf_extra_fields.geo_fields import PointField

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class PromoAreaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
            model = PromoArea

class MooringAreaMooringsiteFilterSerializer(serializers.Serializer):
    """Serializer used by the campground availability map."""
    arrival = serializers.DateField(input_formats=['%Y/%m/%d'], allow_null=True)
    departure = serializers.DateField(input_formats=['%Y/%m/%d'], allow_null=True)
    num_adult = serializers.IntegerField(default=0)
    num_concession = serializers.IntegerField(default=0)
    num_child = serializers.IntegerField(default=0)
    num_infant = serializers.IntegerField(default=0)
    num_mooring = serializers.IntegerField(default=0)
    gear_type = serializers.ChoiceField(choices=('all', 'tent', 'caravan', 'campervan'), default='all')
    vessel_size = serializers.IntegerField(default=0)

class MooringsiteBookingSerializer(serializers.Serializer):
    """Serializer used by the booking creation process."""
    arrival = serializers.DateField(input_formats=['%Y/%m/%d'])
    departure = serializers.DateField(input_formats=['%Y/%m/%d'])
    num_adult = serializers.IntegerField(default=0)
    num_concession = serializers.IntegerField(default=0)
    num_child = serializers.IntegerField(default=0)
    num_infant = serializers.IntegerField(default=0)
    num_mooring = serializers.IntegerField(default=0)
    campground = serializers.IntegerField(default=0)
    campsite_class = serializers.IntegerField(default=0)
    campsite = serializers.IntegerField(default=0)
    vessel_size = serializers.IntegerField(default=0)

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

class MooringAreaBookingRangeSerializer(BookingRangeSerializer):

    class Meta:
        model = MooringAreaBookingRange
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
            'campground',
            'updated_on'
        )
        read_only_fields = ('reason',)
        write_only_fields = (
            'campground'
        )

class MooringsiteBookingRangeSerializer(BookingRangeSerializer):

    class Meta:
        model = MooringsiteBookingRange
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
        fields = '__all__'

class FeatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Feature
        fields = ('url','id','name','description','image')

class MooringAreaMapFeatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Feature
        fields = ('id', 'name', 'description', 'image')

class MooringAreaMapRegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name', 'abbreviation','wkb_geometry', 'zoom_level')

class MooringAreaMapDistrictSerializer(serializers.HyperlinkedModelSerializer):
    region = MooringAreaMapRegionSerializer(read_only=True)
    class Meta:
        model = District
        fields = ('id', 'name', 'abbreviation', 'region')

class MooringAreaMapMarinaSerializer(serializers.HyperlinkedModelSerializer):
    district = MooringAreaMapDistrictSerializer(read_only=True)
    class Meta:
        model = MarinePark 
        fields = ('id','name', 'entry_fee_required', 'district')

class MooringAreaMapFilterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MooringArea
        fields = ('id',)

class MooringAreaMapImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MooringAreaImage
        fields = ('image',)

class MooringAreaMapSerializer(gis_serializers.GeoFeatureModelSerializer):
    features = MooringAreaMapFeatureSerializer(read_only=True, many=True)
    park = MooringAreaMapMarinaSerializer(read_only=True)
    images = MooringAreaMapImageSerializer(read_only=True, many=True)
#    price_hint = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True, source='mooringsites__rates__rate__mooring__min')
#    price_hint = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = MooringArea
        geo_field = 'wkb_geometry'
        fields = (
            'id',
            'name',
            'description',
            'features',
            'mooring_type',
            'park',
            'info_url',
            'images',
            'vessel_size_limit',
            'vessel_draft_limit',
            'max_advance_booking'
#            'price_hint'
        )

class MarineParkRegionMapSerializer(serializers.Serializer):
 #   name = MooringAreaMapDistrictSerializer(read_only=True, many=True)
 #   abbreviation = MooringAreaMapDistrictSerializer(read_only=True)
#    region =MooringAreaMapDistrictSerializer(read_only=True, many=True)
#    ratis_id =MooringAreaMapDistrictSerializer(read_only=True, many=True)
    total = serializers.IntegerField()
    park__district__region = serializers.IntegerField()
    park__district__region__name = serializers.CharField()
    park__district__region__wkb_geometry = PointField()

    class Meta:
#        model = MooringArea
#        geo_field = 'park_id__wkb_geometry'
        fields = (
            'total',
            'park__district__region__wkb_geometry',
            'park__district__region',
            'park__district__region__name',
        )

class MarineParkMapSerializer(serializers.Serializer):
 #   name = MooringAreaMapDistrictSerializer(read_only=True, many=True)
 #   abbreviation = MooringAreaMapDistrictSerializer(read_only=True)
#    region =MooringAreaMapDistrictSerializer(read_only=True, many=True)
#    ratis_id =MooringAreaMapDistrictSerializer(read_only=True, many=True)
    total = serializers.IntegerField()
    park_id__name =  serializers.CharField()
    park_id__wkb_geometry = PointField()
    #park__district__region__name = serializers.CharField()

    class Meta:
#        model = MooringArea 
#        geo_field = 'park_id__wkb_geometry'
        fields = (
            'park_id__name',
            'total',
            'park_id__wkb_geometry',
        )

class MooringAreaImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=17)

    def get_image(self, obj):
        return self.context['request'].build_absolute_uri(format(obj.image.url.split(settings.MEDIA_ROOT)[0]))

    class Meta:
        model = MooringAreaImage
        fields = ('id','image','campground')
        read_only_fields = ('id',)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        super(MooringAreaImageSerializer, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['image'] = serializers.SerializerMethodField()

class ExistingMooringAreaImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    image = serializers.URLField()
    class Meta:
        model = MooringAreaImage
        fields = ('id','image','campground')

class MooringAreaDatatableSerializer(serializers.ModelSerializer):
    park = serializers.SerializerMethodField()
    class Meta:
        model = MooringArea
        fields = (
            'id',
            'name',
            'park',
            'district',
            'region',
            'ratis_id',
            'active',
            'current_closure',
            'mooring_type'
        )

    def get_park(self,obj):
        return obj.park.name

class MooringAreaGroupSerializer(serializers.ModelSerializer):
   class Meta:
        model = MooringAreaGroup
        fields = ('id',
                  'name',
                  'members',
                  'moorings'
        )

class MooringAreaSerializer(serializers.ModelSerializer):
    address = serializers.JSONField()
    images = MooringAreaImageSerializer(read_only=True, many=True,required=False)
    mooring_map = serializers.FileField(read_only=True,required=False,allow_empty_file=True)
    mooring_group = serializers.PrimaryKeyRelatedField(many=True, required=False, read_only=True,  allow_null=True) 

    class Meta:
        model = MooringArea
        fields = (
            'url',
            'id',
            'site_type',
            'mooring_type',
            'name',
            'address',
            'contact',
            'park',
            'district',
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
            'images',
            'max_advance_booking',
            'oracle_code',
            'mooring_map',
            'additional_info',
            'mooring_group',
            'vessel_size_limit',
            'vessel_draft_limit'
        )
        read_only_fields = ('mooring_group',)

    def get_site_type(self, obj):
        return dict(MooringArea.SITE_TYPE_CHOICES).get(obj.site_type)

    def get_address(self, obj):
        if not obj.address:
            return {}
        return obj.address

    def get_park(self,obj):
        return obj.park.name

    def get_price_level(self, obj):
        return dict(MooringArea.CAMPGROUND_PRICE_LEVEL_CHOICES).get(obj.price_level)

    def get_campground_type(self, obj):
#        return dict(MooringArea.MOORING_TYPE_CHOICES).get(obj.campground_type)
        return dict(MooringArea.MOORING_TYPE_CHOICES).get(obj.mooring_type)

    def __init__(self, *args, **kwargs):
        try:
            formatted = bool(kwargs.pop('formatted'))
        except:
            formatted = False
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        super(MooringAreaSerializer, self).__init__(*args, **kwargs)
        if formatted:
            self.fields['site_type'] = serializers.SerializerMethodField()
            self.fields['mooring_type'] = serializers.SerializerMethodField()
            self.fields['price_level'] = serializers.SerializerMethodField()
            self.fields['park'] = serializers.SerializerMethodField()
        if method == 'get':
            self.fields['features'] = FeatureSerializer(many=True)
            self.fields['address'] = serializers.SerializerMethodField()
            self.fields['images'] = MooringAreaImageSerializer(many=True,required=False,method='get')

class MarinaSerializer(serializers.HyperlinkedModelSerializer):
    district = DistrictSerializer()
    #marineparks = MooringAreaSerializer(many=True)
    class Meta:
        model = MarinePark 
        fields = ('id','district', 'url', 'name', 'entry_fee_required', 'entry_fee_required','marineparks')

class MooringsiteStayHistorySerializer(serializers.ModelSerializer):
    details = serializers.CharField(required=False)
    range_start = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'])
    range_end = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'],required=False)
    class Meta:
        model = MooringsiteStayHistory
        fields = ('id','created','range_start','range_end','min_days','max_days','min_dba','max_dba','reason','details','campsite','editable')
        read_only_fields =('editable',)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        super(MooringsiteStayHistorySerializer, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['reason'] = serializers.CharField(source='reason.text')

class MooringAreaStayHistorySerializer(serializers.ModelSerializer):
    details = serializers.CharField(required=False)
    range_start = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'])
    range_end = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'],required=False)
    class Meta:
        model = MooringAreaStayHistory
        fields = ('id','created','range_start','range_end','min_days','max_days','min_dba','max_dba','reason','details','mooringarea','editable')
        read_only_fields =('editable',)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        super(MooringAreaStayHistorySerializer, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['reason'] = serializers.CharField(source='reason.text')

class MooringsiteSerialiser(serializers.ModelSerializer):
    name = serializers.CharField(default='default',required=False)
    class Meta:
        model = Mooringsite
        fields = ('id','mooringarea', 'name', 'type','mooringsite_class','price','features','wkb_geometry','campground_open','active','current_closure','can_add_rate','tent','campervan','caravan','min_people','max_people','description',)

    def __init__(self, *args, **kwargs):
        try:
            formatted = bool(kwargs.pop('formatted'))
        except:
            formatted = False
        try:
            method = kwargs.pop('method')
        except:
            method = 'put'
        super(MooringsiteSerialiser, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['features'] = FeatureSerializer(many=True)
        elif method == 'post':
            self.fields['features'] = serializers.HyperlinkedRelatedField(many=True,read_only=True,required=False,view_name='features-detail')
        elif method == 'put':
            self.fields['features'] = serializers.HyperlinkedRelatedField(many=True,allow_empty=True, queryset=Feature.objects.all(),view_name='feature-detail')

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region

class MooringsiteClassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MooringsiteClass
        fields = ('url','id','name','tent','campervan','min_people','max_people','max_vehicles','caravan','description','features','deleted','can_add_rate','campsites')
        read_only_fields = ('campsites','can_add_rate',)

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        try:
            campsite_ids = kwargs.pop('campsite_ids')
        except:
            campsite_ids = False

        super(MooringsiteClassSerializer, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['features'] = FeatureSerializer(many=True)
        elif method == 'post':
            self.fields['features'] = serializers.HyperlinkedRelatedField(required=False,many=True,allow_empty=True, queryset=Feature.objects.all(),view_name='feature-detail')
        elif method == 'put':
            self.fields['features'] = serializers.HyperlinkedRelatedField(required=False,many=True,allow_empty=True, queryset=Feature.objects.all(),view_name='feature-detail')
        if campsite_ids:
            self.fields['campsites'] = serializers.SerializerMethodField()

    def get_campsites(self,obj):
        return [c.id for c in obj.campsites.all()]

class MooringsiteBookingSerialiser(serializers.HyperlinkedModelSerializer):
    booking_type = serializers.SerializerMethodField()
    class Meta:
        model = MooringsiteBooking
        fields = ('campsite', 'date', 'booking_type')

    def get_booking_type(self, obj):
        return dict(MooringsiteBooking.BOOKING_TYPE_CHOICES).get(obj.booking_type)

class BookingRegoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingVehicleRego
        fields = ('rego','type','booking', 'entry_fee')

class BookingSerializer(serializers.ModelSerializer):
    campground_name = serializers.CharField(source='mooringarea.name',read_only=True)
    campground_region = serializers.CharField(source='mooringarea.region',read_only=True)
    campground_site_type = serializers.CharField(source='mooringarea.site_type',read_only=True)
    campsites = serializers.SerializerMethodField()
    invoices = serializers.SerializerMethodField()
    regos = BookingRegoSerializer(many=True,read_only=True)

    class Meta:
        model = Booking
        fields = ('id','legacy_id','legacy_name','arrival','departure','details','cost_total','override_price','override_reason','override_reason_info','mooringarea','campground_name','campground_region','campground_site_type','campsites','invoices','is_canceled','guests','regos','vehicle_payment_status','refund_status','amount_paid')
        read_only_fields = ('vehicle_payment_status','refund_status')


    def get_invoices(self,obj):
        return [i.invoice_reference for i in obj.invoices.all()]

    def get_campsites(self,obj):
        return obj.campsite_id_list

    def __init__(self,*args,**kwargs):
        try:
            method = kwargs.pop('method')
        except :
            method = "get"
        super(BookingSerializer,self).__init__(*args,**kwargs)
        #if method == 'get':
        #    self.fields['campground'] = MooringAreaSerializer()

class RateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rate
        fields = ('url','id','mooring','adult','concession','child','infant','name')

class MooringsiteRateSerializer(serializers.ModelSerializer):
    date_start = serializers.DateField(format='%d/%m/%Y')
    details = serializers.CharField(required=False)
    class Meta:
        model = MooringsiteRate
        read_only_fields = ('date_end',)

class MooringsiteRateReadonlySerializer(serializers.ModelSerializer):
    adult = serializers.DecimalField(max_digits=5, decimal_places=2,source='rate.adult')
    concession = serializers.DecimalField(max_digits=5, decimal_places=2,source='rate.concession')
    child = serializers.DecimalField(max_digits=5, decimal_places=2,source='rate.child')
    infant = serializers.DecimalField(max_digits=5, decimal_places=2,source='rate.infant')
    class Meta:
        model = MooringsiteRate
        fields = ('id','adult','concession','child','infant','date_start','date_end','rate','editable','deletable','update_level')

class RateDetailSerializer(serializers.Serializer):
    '''Used to validate rates from the frontend
    '''
    rate = serializers.IntegerField(required=False)
    mooring = serializers.DecimalField(max_digits=5, decimal_places=2)
    adult = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default='0.00') 
    concession = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default='0.00')
    child = serializers.DecimalField(max_digits=5, decimal_places=2,  required=False, default='0.00')
    infant = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default='0.00')
    period_start = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'])
    reason = serializers.IntegerField()
    details = serializers.CharField(required=False,allow_blank=True)
    campsite = serializers.IntegerField(required=False)

    def validate_rate(self, value):
        if value:
            try:
                Rate.objects.get(id=value)
            except Rate.DoesNotExist:
                raise serializers.ValidationError('This rate does not exist')
        return value

    def validate(self,obj):
        if obj.get('reason') == 1 and not obj.get('details'):
            raise serializers.ValidationError('Details required if reason is other.')
        return obj

class MooringAreaPriceHistorySerializer(serializers.ModelSerializer):
    date_end = serializers.DateField(required=False)
    details = serializers.CharField(required=False,allow_blank=True)
    class Meta:
        model = MooringAreaPriceHistory
        fields = ('id','date_start','date_end','rate_id','mooring','adult','concession','child','infant','editable','deletable','reason','details')
        read_only_fields = ('id','editable','deletable','mooring','adult','concession','child','infant')

    def validate(self,obj):
        if obj.get('reason') == 1 and not obj.get('details'):
            raise serializers.ValidationError('Details required if the reason is other.')
        return obj


    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop('method')
        except:
            method = 'get'
        super(MooringAreaPriceHistorySerializer, self).__init__(*args, **kwargs)
        if method == 'post':
            self.fields['reason'] = serializers.IntegerField(write_only=True)

class MooringsiteClassPriceHistorySerializer(serializers.ModelSerializer):
    date_end = serializers.DateField(required=False)
    details = serializers.CharField(required=False,allow_blank=True)
    class Meta:
        model = MooringsiteClassPriceHistory
        fields = ('id','date_start','date_end','rate_id','adult','concession','child','infant','editable','deletable','reason','details')
        read_only_fields = ('id','editable','deletable','adult','concession','child','infant')

    def validate(self,obj):
        if obj.get('reason') == 1 and not obj.get('details'):
            raise serializers.ValidationError('Details is rtequired if the reason is other.')
        return obj

    def __init__(self, *args, **kwargs):
        try:
            method = kwargs.pop('method')
        except:
            method = 'get'
        super(MooringsiteClassPriceHistorySerializer, self).__init__(*args, **kwargs)
        if method == 'post':
            self.fields['reason'] = serializers.IntegerField()

class MarinaEntryRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarinaEntryRate
        fields = ("id","period_start","period_end","reason","details","vehicle","concession","motorbike","editable")
        read_only_fields =('editable',)
    def __init__(self, *args, **kwargs):
        from mooring.serialisers import PriceReasonSerializer
        try:
            method = kwargs.pop('method')
        except:
            method = 'post'
        super(MarinaEntryRateSerializer, self).__init__(*args, **kwargs)
        if method == 'get':
            self.fields['reason'] = PriceReasonSerializer(read_only=True)
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

class AccountsAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    profile_addresses = AccountsAddressSerializer(many=True,read_only=True)
    #postcode = serializers.CharField(source='profile_addresses.postcode',read_only=True)
    class Meta:
        model = EmailUser
        fields = ('id','email','first_name','last_name','phone_number','mobile_number','profile_addresses')


# Bulk Pricing
# ==========================
class BulkPricingSerializer(serializers.Serializer):
    TYPE_CHOICES = (
        ('Marina','Marina'),
        ('Mooringsite Type','Mooringsite Type')
    )
    park = serializers.IntegerField(required=False)
    campgrounds = serializers.ListField(
       child=serializers.IntegerField()
    )
    campsiteType = serializers.IntegerField(required=False)
    adult = serializers.DecimalField(max_digits=8, decimal_places=2)
    concession = serializers.DecimalField(max_digits=8, decimal_places=2)
    child = serializers.DecimalField(max_digits=8, decimal_places=2)
    period_start = serializers.DateField(format='%d/%m/%Y',input_formats=['%d/%m/%Y'])
    reason = serializers.IntegerField()
    details =serializers.CharField(required=False)
    type = serializers.ChoiceField(choices=TYPE_CHOICES)

    def validate_park(self, val):
        try:
            park = Marina.objects.get(pk=int(val))
        except Marina.DoesNotExist:
            raise
        return val

    def validate_campgrounds(self,val):
        for v in val:
            try:
                MooringArea.objects.get(pk=v)
            except MooringArea.DoesNotExist:
                raise
        return val

    def validate_reason(self, val):
        reason = None
        try:
            reason = PriceReason.objects.get(pk=int(val))
        except PriceReason.DoesNotExist:
            raise
        return val

    def validate(self,obj):
        if obj.get('reason') == 1  and not obj.get('details'):
            raise serializers.ValidationError('Details required if reason is other.')
        return obj

class ReportSerializer(serializers.Serializer):
    start = serializers.DateTimeField(input_formats=['%d/%m/%Y'])
    end = serializers.DateTimeField(input_formats=['%d/%m/%Y'])

class BookingSettlementReportSerializer(serializers.Serializer):
    date = serializers.DateTimeField(input_formats=['%d/%m/%Y'])

class BookingHistorySerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(source='updated_by.get_full_name')
    invoice = serializers.CharField(source='invoice.reference')

    class Meta:
        model = BookingHistory
        fields = (
            'created',
            'arrival',
            'departure',
            'details',
            'cost_total',
            'campground',
            'campsites',
            'updated_by',
            'invoice',
            'vehicles'
        )

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'iso_3166_1_a2',
            'printable_name',
            'name',
            'display_order'
        )

# User Serializers
# --------------------------
class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id',
            'line1',
            'locality',
            'state',
            'country',
            'postcode'
        ) 

    def validate(self, obj):
        if not obj.get('state'):
            raise serializers.ValidationError('State is required.')
        return obj

class UserSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer()
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'last_name',
            'first_name',
            'email',
            'residential_address',
            'phone_number',
            'mobile_number',
        )

class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'last_name',
            'first_name',
        )

class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'phone_number',
            'mobile_number',
        )

    def validate(self, obj):
        if not obj.get('phone_number') and not obj.get('mobile_number'):
            raise serializers.ValidationError('You must provide a mobile/phone number')
        return obj


#class ContactSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = EmailUser
#        fields = (
#            'id',
#            'email',
#            'phone_number',
#            'mobile_number',
#            'name',
#        )
#
#    def validate(self, obj):
#        if not obj.get('phone_number') and not obj.get('mobile_number'):
#            raise serializers.ValidationError('You must provide a mobile/phone number')
#        return obj

class OracleSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=['%d/%m/%Y','%Y-%m-%d'])
    override = serializers.BooleanField(default=False)

