from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.db import IntegrityError, transaction, connection
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from taggit.managers import TaggableManager
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save, post_save
from parkstay.exceptions import BookingRangeWithinException

# Create your models here.

PARKING_SPACE_CHOICES = (
    (0, 'Parking within site.'),
    (1, 'Parking for exclusive use of site occupiers next to site, but separated from tent space.'),
    (2, 'Parking for exclusive use of occupiers, short walk from tent space.'),
    (3, 'Shared parking (not allocated), short walk from tent space.')
)

NUMBER_VEHICLE_CHOICES = (
    (0, 'One vehicle'),
    (1, 'Two vehicles'),
    (2, 'One vehicle + small trailer'),
    (3, 'One vehicle + small trailer/large vehicle')
)

class CustomerContact(models.Model):
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=255)
    description = models.TextField()
    opening_hours = models.TextField()
    other_services = models.TextField()


class Park(models.Model):
    name = models.CharField(max_length=255)
    district = models.ForeignKey('District', null=True, on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)
    entry_fee_required = models.BooleanField(default=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.district)

    class Meta:
        unique_together = (('name',),)


class PromoArea(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=12)

    def __str__(self):
        return "{}: {}".format(self.name, self.phone_number)

class Campground(models.Model):
    CAMPGROUND_TYPE_CHOICES = (
        (0, 'Campground: no bookings'),
        (1, 'Campground: book online'),
        (2, 'Campground: book by phone'),
        (3, 'Other accomodation'),
        (4, 'Not Published')
    )
    CAMPGROUND_PRICE_LEVEL_CHOICES = (
        (0, 'Campground level'),
        (1, 'Campsite Class level'),
        (2, 'Campsite level'),
    )
    SITE_TYPE_CHOICES = (
        (0, 'Unnumbered Site'),
        (1, 'Numbered site')
    )

    name = models.CharField(max_length=255, null=True)
    park = models.ForeignKey('Park', on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)
    contact = models.ForeignKey('Contact', on_delete=models.PROTECT, blank=True, null=True)
    campground_type = models.SmallIntegerField(choices=CAMPGROUND_TYPE_CHOICES, default=0)
    promo_area = models.ForeignKey('PromoArea', on_delete=models.PROTECT,blank=True, null=True)
    site_type = models.SmallIntegerField(choices=SITE_TYPE_CHOICES, default=0)
    address = JSONField(null=True)
    features = models.ManyToManyField('Feature')
    description = models.TextField(blank=True, null=True)
    area_activities = models.TextField(blank=True, null=True)
    # Tags for communications methods available and access type
    tags = TaggableManager(blank=True)
    driving_directions = models.TextField(blank=True, null=True)
    fees = models.TextField(blank=True, null=True)
    othertransport = models.TextField(blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    price_level = models.SmallIntegerField(choices=CAMPGROUND_PRICE_LEVEL_CHOICES, default=0)
    customer_contact = models.ForeignKey('CustomerContact', blank=True, null=True, on_delete=models.PROTECT)

    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    bookable_per_site = models.BooleanField(default=False)
    bookable_online = models.BooleanField(default=False)
    dog_permitted = models.BooleanField(default=False)
    check_in = models.TimeField(default=time(14))
    check_out = models.TimeField(default=time(10))

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'park'),)

    # Properties
    # =======================================
    @property
    def region(self):
        return self.park.district.region.name

    @property
    def active(self):
        return self._is_open(datetime.now().date())

    @property
    def current_closure(self):
        closure = self._get_current_closure()
        if closure:
            return 'Start: {} End: {}'.format(closure.range_start, closure.range_end)

    @property
    def dog_permitted(self):
        try:
            self.features.get(name='NO DOGS')
            return False
        except Feature.DoesNotExist:
            return True

    @property
    def campfires_allowed(self):
        try:
            self.features.get(name='NO CAMPFIRES')
            return False
        except Feature.DoesNotExist:
            return True

    # Methods
    # =======================================
    def _is_open(self,period):
        '''Check if the campground is open on a specified datetime
        '''
        open_ranges, closed_ranges = None, None
        # Get all booking ranges
        try:
            open_ranges = self.booking_ranges.filter(Q(status=0),Q(range_start__lte=period), Q(range_end__gte=period) | Q(range_end__isnull=True) ).latest('updated_on')
        except CampgroundBookingRange.DoesNotExist:
            pass
        try:
            closed_ranges = self.booking_ranges.filter(Q(range_start__lte=period),~Q(status=0),Q(range_end__gte=period) | Q(range_end__isnull=True) ).latest('updated_on')
        except CampgroundBookingRange.DoesNotExist:
            return True if open_ranges else False

        if not open_ranges:
            return False
        if open_ranges.updated_on > closed_ranges.updated_on:
            return True
        return False

    def _get_current_closure(self):
        closure_period = None
        period = datetime.now().date()
        if not self.active:
            closure = self.booking_ranges.get(Q(range_start__lte=period),~Q(status=0),Q(range_end__isnull=True) |Q(range_end__gte=period))
            closure_period = closure
        return closure_period

    def open(self, data):
        if self.active:
            raise ValidationError('This campground is already open.')
        b = CampgroundBookingRange(**data)
        try:
            within = CampgroundBookingRange.objects.filter(Q(campground=b.campground),Q(status=0),Q(range_start__lte=b.range_start), Q(range_end__gte=b.range_start) | Q(range_end__isnull=True) ).latest('updated_on')
            if within:
                within.updated_on = timezone.now()
                within.save()
        except CampgroundBookingRange.DoesNotExist:
        #if (self.__get_current_closure().range_start <= b.range_start and not self.__get_current_closure().range_end) or (self.__get_current_closure().range_start <= b.range_start <= self.__get_current_closure().range_end):
        #    self.__get_current_closure().delete()
            b.save()

    def close(self, data):
        if not self.active:
            raise ValidationError('This campground is already closed.')
        b = CampgroundBookingRange(**data)
        try:
            within = CampgroundBookingRange.objects.filter(Q(campground=b.campground),~Q(status=0),Q(range_start__lte=b.range_start), Q(range_end__gte=b.range_start) | Q(range_end__isnull=True) ).latest('updated_on')
            if within:
                within.updated_on = timezone.now()
                within.save()
        except CampgroundBookingRange.DoesNotExist:
            b.save()

    def createCampsitePriceHistory(self,data):
        '''Create Multiple campsite rates
        '''
        try:
            with transaction.atomic():
                for c in self.campsites.all():
                    cr = CampsiteRate(**data)
                    cr.campsite = c
                    cr.save()
        except Exception as e:
            raise

    def updatePriceHistory(self,original,_new):
        '''Update Multiple campsite rates
        '''
        try:
            rates = CampsiteRate.objects.filter(**original)
            campsites = self.campsites.all()
            with transaction.atomic():
                for r in rates:
                    if r.campsite in campsites and r.update_level == 0:
                        r.update(_new)
        except Exception as e:
            raise

    def deletePriceHistory(self,data):
        '''Delete Multiple campsite rates
        '''
        try:
            rates = CampsiteRate.objects.filter(**data)
            campsites = self.campsites.all()
            with transaction.atomic():
                for r in rates:
                    if r.campsite in campsites and r.update_level == 0:
                        r.delete()
        except Exception as e:
            raise

class BookingRange(models.Model):
    BOOKING_RANGE_CHOICES = (
        (0, 'Open'),
        (1, 'Closed due to natural disaster'),
        (2, 'Closed for maintenance'),
        (3, 'Other'),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True,help_text='Used to check if the start and end dated were changed')

    status = models.SmallIntegerField(choices=BOOKING_RANGE_CHOICES, default=0)
    details = models.TextField(blank=True,null=True)
    range_start = models.DateField(blank=True, null=True)
    range_end = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    # Properties
    # ====================================
    @property
    def editable(self):
        today = datetime.now().date()
        if self.status != 0 and((self.range_start > today and not self.range_end) or ( self.range_start > datetime.now().date() <= self.range_end)):
            return True
        elif self.status == 0 and (self.range_start <= today and not self.range_end):
            return True
        return False

    # Methods
    # =====================================
    def _is_same(self,other):
        if not isinstance(other, BookingRange) and self.id != other.id:
            return False
        if self.range_start == other.range_start and self.range_end == other.range_end:
            return True
        return False

    def save(self, *args, **kwargs):
        self.full_clean()

        super(BookingRange, self).save(*args, **kwargs)

class StayHistory(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    # minimum/maximum consecutive days allowed for a booking
    min_days = models.SmallIntegerField(default=1)
    max_days = models.SmallIntegerField(default=28)
    # Minimum and Maximum days that a booking can be made before arrival
    min_dba = models.SmallIntegerField(default=0)
    max_dba = models.SmallIntegerField(default=180)

    details = models.TextField(blank=True,null=True)
    range_start = models.DateField(blank=True, null=True)
    range_end = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    # Properties
    # ====================================
    @property
    def editable(self):
        now = datetime.now().date()
        if (self.range_start <= now and not self.range_end) or ( self.range_start <= now <= self.range_end):
            return True
        elif (self.range_start >= now and not self.range_end) or ( self.range_start >= now <= self.range_end):
            return True
        return False

    # Methods
    # =====================================
    def clean(self, *args, **kwargs):
        if self.min_days < 1:
            raise ValidationError('The minimum days should be greater than 0.')
        if self.max_days > 28:
            raise ValidationError('The maximum days should not be grater than 28.')

class CampgroundBookingRange(BookingRange):
    campground = models.ForeignKey('Campground', on_delete=models.CASCADE,related_name='booking_ranges')
    # minimum/maximum number of campsites allowed for a booking
    min_sites = models.SmallIntegerField(default=1)
    max_sites = models.SmallIntegerField(default=12)

    # Properties
    # ====================================

    # Methods
    # =====================================
    def _is_same(self,other):
        if not isinstance(other, CampgroundBookingRange) and self.id != other.id:
            return False
        if self.range_start == other.range_start and self.range_end == other.range_end:
            return True
        return False

    def clean(self, *args, **kwargs):
        original = None
        if self.pk:
            original = CampgroundBookingRange.objects.get(pk=self.pk)
            if not original.editable:
                raise ValidationError('This Booking Range is not editable')

        # Preventing ranges within other ranges
        within = CampgroundBookingRange.objects.filter(Q(campground=self.campground),~Q(pk=self.pk),Q(status=self.status),Q(range_start__lte=self.range_start), Q(range_end__gte=self.range_start) | Q(range_end__isnull=True) )
        if within:
            raise BookingRangeWithinException('This Booking Range is within the range of another one')
        if self.range_start < datetime.now().date() and original.range_start != self.range_start:
            raise ValidationError('The start date can\'t be in the past')

class Campsite(models.Model):
    campground = models.ForeignKey('Campground', db_index=True, on_delete=models.PROTECT, related_name='campsites')
    name = models.CharField(max_length=255)
    campsite_class = models.ForeignKey('CampsiteClass', on_delete=models.PROTECT, null=True,blank=True, related_name='campsites')
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    features = models.ManyToManyField('Feature')
    cs_tents = models.SmallIntegerField(default=0)
    cs_parking_spaces = models.SmallIntegerField(choices=PARKING_SPACE_CHOICES, default=0)
    cs_number_vehicles = models.SmallIntegerField(choices=NUMBER_VEHICLE_CHOICES, default=0)
    cs_min_people = models.SmallIntegerField(default=1)
    cs_max_people = models.SmallIntegerField(default=12)
    cs_dimensions = models.CharField(max_length=12, default='6x4')

    def __str__(self):
        return '{} - {}'.format(self.campground, self.name)

    class Meta:
        unique_together = (('campground', 'name'),)

    # Properties
    # ==============================
    property
    def tents(self):
        return self.campsite_class.tents if self.campsite_class else self.cs_tents

    property
    def parking_spaces(self):
        return self.campsite_class.parking_spaces if self.campsite_class else self.cs_parking_spaces

    property
    def number_vehicles(self):
        return self.campsite_class.number_vehicles if self.campsite_class else self.cs_number_vehicles

    property
    def min_people(self):
        return self.campsite_class.min_people if self.campsite_class else self.cs_min_people

    property
    def max_people(self):
        return self.campsite_class.max_people if self.campsite_class else self.cs_max_people

    property
    def dimensions(self):
        return self.campsite_class.dimensions if self.campsite_class else self.cs_dimensions

    @property
    def type(self):
        return self.campsite_class.name

    @property
    def price(self):
        return 'Set at {}'.format(self.campground.get_price_level_display()) 

    @property
    def can_add_rate(self):
        return self.campground.price_level == 2

    @property
    def active(self):
        return self._is_open(datetime.now().date())

    @property
    def campground_open(self):
        return self.__is_campground_open()

    @property
    def current_closure(self):
        closure = self._get_current_closure()
        if closure:
            return 'Start: {} End: {}'.format(closure.range_start, closure.range_end)
    # Methods
    # =======================================
    def __is_campground_open(self):
        return self.campground.active

    def _is_open(self,period):
        '''Check if the campsite is open on a specified datetime
        '''
        if self.__is_campground_open():
            open_ranges, closed_ranges = None, None
            # Get all booking ranges
            try:
                open_ranges = self.booking_ranges.filter(Q(status=0),Q(range_start__lte=period), Q(range_end__gte=period) | Q(range_end__isnull=True) ).latest('updated_on')
            except CampsiteBookingRange.DoesNotExist:
                pass
            try:
                closed_ranges = self.booking_ranges.filter(Q(range_start__lte=period),~Q(status=0),Q(range_end__gte=period) | Q(range_end__isnull=True) ).latest('updated_on')
            except CampsiteBookingRange.DoesNotExist:
                return True if open_ranges else False

            if not open_ranges:
                return False
            if open_ranges.updated_on > closed_ranges.updated_on:
                return True
        return False

    def __get_current_closure(self):
        if self.__is_campground_open():
            closure_period = None
            period = datetime.now().date()
            if not self.active:
                closure = self.booking_ranges.get(Q(range_start__lte=period),~Q(status=0),Q(range_end__isnull=True) |Q(range_end__gte=period))
                closure_period = closure
            return closure_period
        else:
            return self.campground._get_current_closure()

    def open(self, data):
        if not self.campground_open:
            raise ValidationError('You can\'t open this campsite until the campground is open')
        if self.active:
            raise ValidationError('This campsite is already open.')
        b = CampsiteBookingRange(**data)
        try:
            within = CampsiteBookingRange.objects.filter(Q(campsite=b.campsite),Q(status=0),Q(range_start__lte=b.range_start), Q(range_end__gte=b.range_start) | Q(range_end__isnull=True) ).latest('updated_on')
            if within:
                within.updated_on = timezone.now()
                within.save()
        except CampsiteBookingRange.DoesNotExist:
        #if (self.__get_current_closure().range_start <= b.range_start and not self.__get_current_closure().range_end) or (self.__get_current_closure().range_start <= b.range_start <= self.__get_current_closure().range_end):
        #    self.__get_current_closure().delete()
            b.save()

    def close(self, data):
        if not self.active:
            raise ValidationError('This campsite is already closed.')
        b = CampsiteBookingRange(**data)
        try:
            within = CampsiteBookingRange.objects.filter(Q(campsite=b.campsite),~Q(status=0),Q(range_start__lte=b.range_start), Q(range_end__gte=b.range_start) | Q(range_end__isnull=True) ).latest('updated_on')
            if within:
                within.updated_on = timezone.now()
                within.save()
        except CampsiteBookingRange.DoesNotExist:
            b.save()
    
    @staticmethod
    def bulk_create(number,data):
        try:
            created_campsites = []
            with transaction.atomic():
                campsites = []
                latest = 0
                current_campsites = Campsite.objects.filter(campground=data['campground'])
                cs_numbers = [int(c.name) for c in current_campsites if c.name.isdigit()]
                if cs_numbers:
                    latest = max(cs_numbers)
                for i in range(number):
                    latest += 1
                    c = Campsite(**data)
                    name = str(latest)
                    if len(name) == 1:
                        name = '0{}'.format(name)
                    c.name = name
                    c.save()
                    if c.campsite_class:
                        c.features = c.campsite_class.features.all()
                        c.save()
                    created_campsites.append(c)
            return created_campsites
        except Exception:
            raise

class CampsiteBookingRange(BookingRange):
    campsite = models.ForeignKey('Campsite', on_delete=models.PROTECT,related_name='booking_ranges')

    # Properties
    # ====================================

    # Methods
    # =====================================
    def _is_same(self,other):
        if not isinstance(other, CampsiteBookingRange) and self.id != other.id:
            return False
        if self.range_start == other.range_start and self.range_end == other.range_end:
            return True
        return False

    def clean(self, *args, **kwargs):
        original = None
        if self.pk:
            original = CampsiteBookingRange.objects.get(pk=self.pk)
            if not original.editable:
                raise ValidationError('This Booking Range is not editable')

        # Preventing ranges within other ranges
        within = CampsiteBookingRange.objects.filter(Q(campsite=self.campsite),~Q(pk=self.pk),Q(status=self.status),Q(range_start__lte=self.range_start), Q(range_end__gte=self.range_start) | Q(range_end__isnull=True) )
        if within:
            raise BookingRangeWithinException('This Booking Range is within the range of another one')
        if self.range_start < datetime.now().date() and original.range_start != self.range_start:
            raise ValidationError('The start date can\'t be in the past')

class CampsiteStayHistory(StayHistory):
    campsite = models.ForeignKey('Campsite', on_delete=models.PROTECT,related_name='stay_history')


class Feature(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    image = models.ImageField(null=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=16, null=True, unique=True)
    ratis_id = models.IntegerField(default=-1)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=16, null=True, unique=True)
    region = models.ForeignKey('Region', on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)

    def __str__(self):
        return self.name


class CampsiteClass(models.Model):

    name = models.CharField(max_length=255, unique=True)
    camp_unit_suitability = TaggableManager()
    tents = models.SmallIntegerField(default=0)
    parking_spaces = models.SmallIntegerField(choices=PARKING_SPACE_CHOICES, default=0)
    number_vehicles = models.SmallIntegerField(choices=NUMBER_VEHICLE_CHOICES, default=0)
    min_people = models.SmallIntegerField(default=1)
    max_people = models.SmallIntegerField(default=12)
    dimensions = models.CharField(max_length=12, default='6x4')
    features = models.ManyToManyField('Feature')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def delete(self, permanently=False,using=None):
        if not permanently:
            self.deleted = True
            self.save()
        else:
            super(CampsiteClass, self).delete(using)

    # Property
    # ===========================
    def can_add_rate(self):
        can_add = False
        campsites = self.campsites.all()
        for c in campsites:
            if c.campground.price_level == 1:
                can_add = True
                break
        return can_add

    # Methods
    # ===========================
    def createCampsitePriceHistory(self,data):
        '''Create Multiple campsite rates
        '''
        try:
            with transaction.atomic():
                for c in self.campsites.all():
                    cr = CampsiteRate(**data)
                    cr.campsite = c
                    cr.save()
        except Exception as e:
            raise

    def updatePriceHistory(self,original,_new):
        '''Update Multiple campsite rates
        '''
        try:
            rates = CampsiteRate.objects.filter(**original)
            campsites = self.campsites.all()
            with transaction.atomic():
                for r in rates:
                    if r.campsite in campsites and r.update_level == 1:
                        r.update(_new)
        except Exception as e:
            raise

    def deletePriceHistory(self,data):
        '''Delete Multiple campsite rates
        '''
        try:
            rates = CampsiteRate.objects.filter(**data)
            campsites = self.campsites.all()
            with transaction.atomic():
                for r in rates:
                    if r.campsite in campsites and r.update_level == 1:
                        r.delete()
        except Exception as e:
            raise
class CampsiteBooking(models.Model):
    BOOKING_TYPE_CHOICES = (
        (0, 'Reception booking'),
        (1, 'Internet booking'),
        (2, 'Black booking')
    )

    campsite = models.ForeignKey('Campsite', db_index=True, on_delete=models.PROTECT)
    date = models.DateField(db_index=True)
    booking = models.ForeignKey('Booking', on_delete=models.PROTECT, null=True)
    booking_type = models.SmallIntegerField(choices=BOOKING_TYPE_CHOICES, default=0)

    def __str__(self):
        return '{} - {}'.format(self.campsite, self.date)

    class Meta:
        unique_together = (('campsite', 'date'),)


class Rate(models.Model):
    adult = models.DecimalField(max_digits=8, decimal_places=2, default='10.00')
    concession = models.DecimalField(max_digits=8, decimal_places=2, default='6.60')
    child = models.DecimalField(max_digits=8, decimal_places=2, default='2.20')
    infant = models.DecimalField(max_digits=8, decimal_places=2, default='0')

    def __str__(self):
        return 'adult: ${}, concession: ${}, child: ${}, infant: ${}'.format(self.adult, self.concession, self.child, self.infant)

    class Meta:
        unique_together = (('adult', 'concession', 'child', 'infant'),)

    # Properties
    # =================================
    @property
    def name(self):
        return 'adult: ${}, concession: ${}, child: ${}, infant: ${}'.format(self.adult, self.concession, self.child, self.infant)

class CampsiteRate(models.Model):
    RATE_TYPE_CHOICES = (
        (0, 'Standard'),
        (1, 'Discounted'),
    )

    UPDATE_LEVEL_CHOICES = (
        (0, 'Campground level'),
        (1, 'Campsite Class level'),
        (2, 'Campsite level'),
    )
    PRICE_MODEL_CHOICES = (
        (0, 'Price per Person'),
        (1, 'Fixed Price'),
    )
    campsite = models.ForeignKey('Campsite', on_delete=models.PROTECT, related_name='rates')
    rate = models.ForeignKey('Rate', on_delete=models.PROTECT)
    allow_public_holidays = models.BooleanField(default=True)
    date_start = models.DateField(default=date.today)
    date_end = models.DateField(null=True, blank=True)
    rate_type = models.SmallIntegerField(choices=RATE_TYPE_CHOICES, default=0)
    price_model = models.SmallIntegerField(choices=PRICE_MODEL_CHOICES, default=0)
    update_level = models.SmallIntegerField(choices=UPDATE_LEVEL_CHOICES, default=0)

    def get_rate(self, num_adult=0, num_concession=0, num_child=0, num_infant=0):
        return self.rate.adult*num_adult + self.rate.concession*num_concession + \
                self.rate.child*num_child + self.rate.infant*num_infant

    def __str__(self):
        return '{} - ({})'.format(self.campsite, self.rate)

    class Meta:
        unique_together = (('campsite', 'rate', 'date_start','date_end'),)

    # Properties
    # =================================
    @property
    def deletable(self):
        today = datetime.now().date()
        if self.date_start >= today:
            return True
        return False

    @property
    def editable(self):
        today = datetime.now().date()
        if (self.date_start > today and not self.date_end) or ( self.date_start > today <= self.date_end):
            return True
        return False

    # Methods
    # =================================
    def update(self,data):
        print('here')
        for attr, value in data.items():
            print('{} {}'.format(attr, value))
            setattr(self, attr, value)
        self.save()

class Booking(models.Model):
    legacy_id = models.IntegerField(unique=True)
    legacy_name = models.CharField(max_length=255, blank=True)
    arrival = models.DateField()
    departure = models.DateField()
    details = JSONField(null=True)
    cost_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    campground = models.ForeignKey('Campground', null=True)

# VIEWS
# =====================================
class CampgroundPriceHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    date_start = models.DateField()
    date_end = models.DateField()
    rate_id = models.IntegerField()
    adult = models.DecimalField(max_digits=8, decimal_places=2)
    concession = models.DecimalField(max_digits=8, decimal_places=2)
    child = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'parkstay_campground_pricehistory_v'
        ordering = ['-date_start',]

    # Properties
    # ====================================
    @property
    def deletable(self):
        today = datetime.now().date()
        if self.date_start >= today:
            return True
        return False

    @property
    def editable(self):
        today = datetime.now().date()
        if (self.date_start > today and not self.date_end) or ( self.date_start > today <= self.date_end):
            return True
        return False

class CampsiteClassPriceHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    date_start = models.DateField()
    date_end = models.DateField()
    rate_id = models.IntegerField()
    adult = models.DecimalField(max_digits=8, decimal_places=2)
    concession = models.DecimalField(max_digits=8, decimal_places=2)
    child = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'parkstay_campsiteclass_pricehistory_v'
        ordering = ['-date_start',]

    # Properties
    # ====================================
    @property
    def deletable(self):
        today = datetime.now().date()
        if self.date_start >= today:
            return True
        return False

    @property
    def editable(self):
        today = datetime.now().date()
        if (self.date_start > today and not self.date_end) or ( self.date_start > today <= self.date_end):
            return True
        return False
# LISTENERS
# ======================================
class CampgroundBookingRangeListener(object):
    """
    Event listener for CampgroundBookingRange
    """

    @staticmethod
    @receiver(pre_save, sender=CampgroundBookingRange)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = CampgroundBookingRange.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

            if not instance._is_same(original_instance):
                instance.updated_on = timezone.now()
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = CampgroundBookingRange.objects.get(~Q(id=instance.id),Q(campground=instance.campground),Q(range_start__lte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True) )
                within.range_end = instance.range_start
                within.save()
            except CampgroundBookingRange.DoesNotExist:
                pass
        if instance.status == 0 and not instance.range_end:
            try:
                another_open = CampgroundBookingRange.objects.filter(campground=instance.campground,range_start=instance.range_start+timedelta(days=1),status=0).latest('updated_on')
                instance.range_end = instance.range_start
            except CampgroundBookingRange.DoesNotExist:
                pass

    @staticmethod
    @receiver(post_delete, sender=CampgroundBookingRange)
    def _post_delete(sender, instance, **kwargs):
        today = datetime.now().date()
        if instance.status != 0 and instance.range_end:
            try:
                linked_open = CampgroundBookingRange.objects.get(range_start=instance.range_end + timedelta(days=1), status=0)
                if instance.range_start >= today:
                    linked_open.range_start = instance.range_start
                else:
                     linked_open.range_start = today
                linked_open.save()
            except CampgroundBookingRange.DoesNotExist:
                pass
        elif instance.status != 0 and not instance.range_end:
            try:
                if instance.range_start >= today:
                    CampgroundBookingRange.objects.create(campground=instance.campground,range_start=instance.range_start,status=0)
                else:
                    CampgroundBookingRange.objects.create(campsite=instance.campground,range_start=today,status=0)
            except:
                pass

    @staticmethod
    @receiver(post_save, sender=CampgroundBookingRange)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            pass

        # Check if its a closure and has an end date to create new opening range
        if instance.status != 0 and instance.range_end:
            another_open = CampgroundBookingRange.objects.filter(campground=instance.campground,range_start=datetime.now().date()+timedelta(days=1),status=0)
            if not another_open:
                try:
                    CampgroundBookingRange.objects.create(campground=instance.campground,range_start=instance.range_end+timedelta(days=1),status=0)
                except BookingRangeWithinException as e:
                    pass

class CampgroundListener(object):
    """
    Event listener for Campgrounds
    """

    @staticmethod
    @receiver(pre_save, sender=Campground)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Campground.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Campground)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            # Create an opening booking range on creation of Campground
             CampgroundBookingRange.objects.create(campground=instance,range_start=datetime.now().date(),status=0)
        else:
            if original_instance.price_level != instance.price_level:
                # Get all campsites
                today = datetime.now().date()
                campsites = instance.campsites.all()
                campsite_list = campsites.values_list('id', flat=True)
                rates = CampsiteRate.objects.filter(campsite__in=campsite_list,update_level=original_instance.price_level)
                current_rates = rates.filter(Q(date_end__isnull=True),Q(date_start__lte =  today)).update(date_end=today)
                future_rates = rates.filter(date_start__gt = today).delete()
                if instance.price_level == 1:
                    #Check if there are any existant campsite class rates
                    for c in campsites:
                        try:
                            ch = CampsiteClassPriceHistory.objects.get(Q(date_end__isnull=True),id=c.campsite_class_id,date_start__lte = today)
                            cr = CampsiteRate(campsite=c,rate_id=ch.rate_id,date_start=today + timedelta(days=1))
                            cr.save()
                        except CampsiteClassPriceHistory.DoesNotExist:
                            pass 
                        except Exception:
                            pass 

class CampsiteBookingRangeListener(object):
    """
    Event listener for CampsiteBookingRange
    """

    @staticmethod
    @receiver(pre_save, sender=CampsiteBookingRange)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = CampsiteBookingRange.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

            if not instance._is_same(original_instance):
                instance.updated_on = timezone.now()
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = CampsiteBookingRange.objects.get(Q(campsite=instance.campsite),Q(range_start__lte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True) )
                within.range_end = instance.range_start
                within.save()
            except CampsiteBookingRange.DoesNotExist:
                pass
        if instance.status == 0 and not instance.range_end:
            try:
                another_open = CampsiteBookingRange.objects.filter(campsite=instance.campsite,range_start=instance.range_start+timedelta(days=1),status=0).latest('updated_on')
                instance.range_end = instance.range_start
            except CampsiteBookingRange.DoesNotExist:
                pass

    @staticmethod
    @receiver(post_delete, sender=CampsiteBookingRange)
    def _post_delete(sender, instance, **kwargs):
        today = datetime.now().date()
        if instance.status != 0 and instance.range_end:
            try:
                linked_open = CampsiteBookingRange.objects.get(range_start=instance.range_end + timedelta(days=1), status=0)
                if instance.range_start >= today:
                    linked_open.range_start = instance.range_start
                else:
                     linked_open.range_start = today
                linked_open.save()
            except CampsiteBookingRange.DoesNotExist:
                pass
        elif instance.status != 0 and not instance.range_end:
            try:
                if instance.range_start >= today:
                    CampsiteBookingRange.objects.create(campsite=instance.campsite,range_start=instance.range_start,status=0)
                else:
                    CampsiteBookingRange.objects.create(campsite=instance.campsite,range_start=today,status=0)
            except:
                pass

    @staticmethod
    @receiver(post_save, sender=CampsiteBookingRange)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            pass

        # Check if its a closure and has an end date to create new opening range
        if instance.status != 0 and instance.range_end:
            another_open = CampsiteBookingRange.objects.filter(campsite=instance.campsite,range_start=datetime.now().date()+timedelta(days=1),status=0)
            if not another_open:
                try:
                    CampsiteBookingRange.objects.create(campsite=instance.campsite,range_start=instance.range_end+timedelta(days=1),status=0)
                except BookingRangeWithinException as e:
                    pass

class CampsiteListener(object):
    """
    Event listener for Campsites
    """

    @staticmethod
    @receiver(pre_save, sender=Campsite)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Campsite.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Campsite)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            # Create an opening booking range on creation of Campground
             CampsiteBookingRange.objects.create(campsite=instance,range_start=datetime.now().date(),status=0)

class CampsiteRateListener(object):
    """
    Event listener for Campsite Rate
    """

    @staticmethod
    @receiver(pre_save, sender=CampsiteRate)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = CampsiteRate.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = CampsiteRate.objects.get(Q(campsite=instance.campsite),Q(date_start__lte=instance.date_start), Q(date_end__gte=instance.date_start) | Q(date_end__isnull=True) )
                within.date_end = instance.date_start - timedelta(days=2)
                within.save()
            except CampsiteRate.DoesNotExist:
                pass

    @staticmethod
    @receiver(post_delete, sender=CampsiteRate)
    def _post_delete(sender, instance, **kwargs): 
        if not instance.date_end:
            CampsiteRate.objects.filter(date_end=instance.date_start- timedelta(days=2),campsite=instance.campsite).update(date_end=None)
