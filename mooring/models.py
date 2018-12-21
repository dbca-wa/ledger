from __future__ import unicode_literals

import os
import uuid
import base64
import binascii
import hashlib
from decimal import Decimal as D
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.db import IntegrityError, transaction, connection
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from django.conf import settings
from taggit.managers import TaggableManager
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save, post_save,pre_delete
from mooring.exceptions import BookingRangeWithinException
from django.core.cache import cache
from ledger.payments.models import Invoice
from ledger.accounts.models import EmailUser

# Create your models here.

PARKING_SPACE_CHOICES = (
    (0, 'Marinaing within site.'),
    (1, 'Marinaing for exclusive use of site occupiers next to site, but separated from tent space.'),
    (2, 'Marinaing for exclusive use of occupiers, short walk from tent space.'),
    (3, 'Shared parking (not allocated), short walk from tent space.')
)

NUMBER_VEHICLE_CHOICES = (
    (0, 'One vehicle'),
    (1, 'Two vehicles'),
    (2, 'One vehicle + small trailer'),
    (3, 'One vehicle + small trailer/large vehicle')
)

class Contact(models.Model):
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=255)
    description = models.TextField(null=True,blank=True)
    opening_hours = models.TextField(null=True)
    other_services = models.TextField(null=True)

    def __str__(self):
        return "{}: {}".format(self.name, self.phone_number)


class MarinePark(models.Model):

    ZOOM_LEVEL = (
        (0, 'default'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '4'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
        (11, '11'),
        (12, '12'),
        (13, '13'),
        (14, '14'),
        (15, '15'),
        (16, '16'),

    )

    name = models.CharField(max_length=255)
    district = models.ForeignKey('District', null=True, on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)
    entry_fee_required = models.BooleanField(default=True)
    oracle_code = models.CharField(max_length=50, null=True,blank=True)
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    zoom_level = models.IntegerField(choices=ZOOM_LEVEL,default=-1)

    def __str__(self):
        return '{} - {}'.format(self.name, self.district)

    def clean(self,*args,**kwargs):
        if self.entry_fee_required and not self.oracle_code:
            raise ValidationError('A park entry oracle code is required if entry fee is required.')

    def save(self,*args,**kwargs):
        cache.delete('parks')
        self.full_clean()
        super(MarinePark,self).save(*args,**kwargs)

    class Meta:
        unique_together = (('name',),)


class PromoArea(models.Model):
    name = models.CharField(max_length=255, unique=True)
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)

    def __str__(self):
        return self.name

def update_mooring_map_filename(instance, filename):
    return 'mooring/mooring_maps/{}/{}'.format(instance.id,filename)

class MooringArea(models.Model):

    MOORING_TYPE_CHOICES = (
        (0, 'Bookable Online'),
        (1, 'Not Bookable Online'),
        (2, 'Public'),
        (3, 'Unpublished'),
    )

    CAMPGROUND_PRICE_LEVEL_CHOICES = (
        (0, 'Mooring level'),
        (1, 'Mooringsite Class level'),
#        (2, 'Mooringsite level'),
    )

    SITE_TYPE_CHOICES = (
        (0, 'Bookable Per Site'),
       (1, 'Bookable Per Site Type'),
        #(2, 'Bookable Per Site Type (hide site number)'),
    )

    name = models.CharField(max_length=255, null=True)
    park = models.ForeignKey('MarinePark', on_delete=models.PROTECT, related_name='marineparks')
    ratis_id = models.IntegerField(default=-1)
    contact = models.ForeignKey('Contact', on_delete=models.PROTECT, blank=True, null=True)
    mooring_type = models.SmallIntegerField(choices=MOORING_TYPE_CHOICES, default=3)
    promo_area = models.ForeignKey('PromoArea', on_delete=models.PROTECT,blank=True, null=True)
    site_type = models.SmallIntegerField(choices=SITE_TYPE_CHOICES, default=0)
    address = JSONField(null=True,blank=True)
    features = models.ManyToManyField('Feature')
    description = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    area_activities = models.TextField(blank=True, null=True)

    # Tags for communications methods available and access type
    tags = TaggableManager(blank=True)
    driving_directions = models.TextField(blank=True, null=True)
    fees = models.TextField(blank=True, null=True)
    othertransport = models.TextField(blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    price_level = models.SmallIntegerField(choices=CAMPGROUND_PRICE_LEVEL_CHOICES, default=0)
    info_url = models.CharField(max_length=255, blank=True)
    long_description = models.TextField(blank=True,null=True)

    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    dog_permitted = models.BooleanField(default=False)
    check_in = models.TimeField(default=time(14))
    check_out = models.TimeField(default=time(10))
    max_advance_booking = models.IntegerField(default =180)
    oracle_code = models.CharField(max_length=50,null=True,blank=True)
    mooring_map = models.FileField(upload_to=update_mooring_map_filename,null=True,blank=True)
    vessel_size_limit = models.IntegerField(default=0)
    vessel_draft_limit = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        cache.delete('marina')
        cache.delete('marina_dt')
        super(MooringArea,self).save(*args,**kwargs)

    class Meta:
        unique_together = (('name', 'park'),)
        verbose_name = 'Mooring'
        verbose_name_plural = 'Moorings'

    # Properties
    # =======================================
    @property
    def region(self):
        return self.park.district.region.name

    @property
    def district(self):
        return self.park.district.name

    @property
    def active(self):
        return self._is_open(datetime.now().date())

    @property
    def current_closure(self):
        closure = self._get_current_closure()
        if closure:
            return 'Start: {} Reopen: {}'.format(closure.range_start.strftime('%d/%m/%Y'), closure.range_end.strftime('%d/%m/%Y') if closure.range_end else "")
        return ''

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

    @property
    def campsite_classes(self):
        return list(set([c.campsite_class.id for c in self.campsites.all()]))

    @property
    def first_image(self):
        images = self.images.all()
        if images.count():
            return images[0]
        return None

    @property
    def email(self):
        if self.contact:
            return self.contact.email
        return None

    @property
    def telephone(self):
        if self.contact:
            return self.contact.phone_number
        return None

    # Methods
    # =======================================
    def _is_open(self,period):
        '''Check if the campground is open on a specified datetime
        '''
        open_ranges, closed_ranges = None, None
        # Get all booking ranges
        try:
            open_ranges = self.booking_ranges.filter(Q(status=0),Q(range_start__lte=period), Q(range_end__gte=period) | Q(range_end__isnull=True) ).latest('updated_on')
        except MooringAreaBookingRange.DoesNotExist:
            pass
        try:
            closed_ranges = self.booking_ranges.filter(Q(range_start__lte=period),~Q(status=0),Q(range_end__gte=period) | Q(range_end__isnull=True) ).latest('updated_on')
        except MooringAreaBookingRange.DoesNotExist:
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
            closure = self.booking_ranges.filter(Q(range_start__lte=period),~Q(status=0),Q(range_end__isnull=True) |Q(range_end__gte=period)).order_by('updated_on')
            if closure:
                closure_period = closure[0]
        return closure_period

    def open(self, data):
        if self.active:
            raise ValidationError('This campground is already open.')
        b = MooringAreaBookingRange(**data)
        try:
            within = MooringAreaBookingRange.objects.filter(Q(campground=b.campground),Q(status=0),Q(range_start__lte=b.range_start), Q(range_end__gte=b.range_start) | Q(range_end__isnull=True) ).latest('updated_on')
            if within:
                within.updated_on = timezone.now()
                within.save(skip_validation=True)

        except MooringAreaBookingRange.DoesNotExist:
        #if (self.__get_current_closure().range_start <= b.range_start and not self.__get_current_closure().range_end) or (self.__get_current_closure().range_start <= b.range_start <= self.__get_current_closure().range_end):
        #    self.__get_current_closure().delete()
            b.save()

    def close(self, data):
        b = MooringAreaBookingRange(**data)
        try:
            within = MooringAreaBookingRange.objects.filter(Q(campground=b.campground),~Q(status=0),Q(range_start__lte=b.range_start), Q(range_end__gte=b.range_start) | Q(range_end__isnull=True) ).latest('updated_on')
            if within:
                within.updated_on = timezone.now()
                within.save(skip_validation=True)
                if within.range_start != b.range_start or within.range_end != b.range_end:
                    raise ValidationError('{} is already closed.'.format(within.campground.name))
            else:
                b.save()
        except MooringAreaBookingRange.DoesNotExist:
            b.save()
        except:
            raise


    def createMooringsitePriceHistory(self,data):
        '''Create Multiple campsite rates
        '''
        try:
            with transaction.atomic():
                for c in self.campsites.all():
                    cr = MooringsiteRate(**data)
                    cr.campsite = c
                    cr.save()
        except Exception as e:
            raise

    def updatePriceHistory(self,original,_new):
        '''Update Multiple campsite rates
        '''
        try:
            rates = MooringsiteRate.objects.filter(**original)
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
            rates = MooringsiteRate.objects.filter(**data)
            campsites = self.campsites.all()
            with transaction.atomic():
                for r in rates:
                    if r.campsite in campsites and r.update_level == 0:
                        r.delete()
        except Exception as e:
            raise

def campground_image_path(instance, filename):
    return '/'.join(['mooring', 'campground_images', filename])

class MooringAreaGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(EmailUser,blank=True)
#    campgrounds = models.ManyToManyField(MooringArea,blank=True)
    moorings = models.ManyToManyField(MooringArea,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Mooring Group'
        verbose_name_plural = 'Mooring Groups'

class MooringAreaImage(models.Model):
    image = models.ImageField(max_length=255, upload_to=campground_image_path)
    campground = models.ForeignKey(MooringArea, related_name='images')
    checksum = models.CharField(blank=True, max_length=255, editable=False)

    class Meta:
        ordering = ('id',)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension

    def strip_b64_header(self, content):
        if ';base64,' in content:
            header, base64_data = content.split(';base64,')
            return base64_data
        return content

    def _calculate_checksum(self, content):
        checksum = hashlib.md5()
        checksum.update(content.read())
        return base64.b64encode(checksum.digest())

    def createImage(self, content):
        base64_data = self.strip_b64_header(content)
        try:
            decoded_file = base64.b64decode(base64_data)
        except (TypeError, binascii.Error):
            raise ValidationError(self.INVALID_FILE_MESSAGE)
        file_name = str(uuid.uuid4())[:12]
        file_extension = self.get_file_extension(file_name,decoded_file)
        complete_file_name = "{}.{}".format(file_name, file_extension)
        uploaded_image = ContentFile(decoded_file, name=complete_file_name)
        return uploaded_image

    def save(self, *args, **kwargs):
        self.checksum = self._calculate_checksum(self.image)
        self.image.seek(0)
        if not self.pk:
            self.image = self.createImage(base64.b64encode(self.image.read()))
        else:
            orig = MooringAreaImage.objects.get(pk=self.pk)
            if orig.image:
                if orig.checksum != self.checksum:
                    if os.path.isfile(orig.image.path):
                        os.remove(orig.image)
                    self.image = self.createImage(base64.b64encode(self.image.read()))
                else:
                    pass

        super(MooringAreaImage,self).save(*args,**kwargs)

    def delete(self, *args, **kwargs):
        try:
            os.remove(self.image)
        except:
            pass
        super(MooringAreaImage,self).delete(*args,**kwargs)

class BookingRange(models.Model):
    BOOKING_RANGE_CHOICES = (
        (0, 'Open'),
        (1, 'Closed'),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True,help_text='Used to check if the start and end dated were changed')

    status = models.SmallIntegerField(choices=BOOKING_RANGE_CHOICES, default=0)
    closure_reason = models.ForeignKey('ClosureReason',null=True,blank=True)
    open_reason = models.ForeignKey('OpenReason',null=True,blank=True)
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
        if self.status != 0 and((self.range_start <= today and not self.range_end) or (self.range_start <= today and self.range_end > today) or (self.range_start > today and not self.range_end) or ( self.range_start >= today <= self.range_end)):
            return True
        elif self.status == 0 and ((self.range_start <= today and not self.range_end) or self.range_start > today):
            return True
        return False

    @property
    def reason(self):
        if self.status == 0:
            return self.open_reason.text
        return self.closure_reason.text

    # Methods
    # =====================================
    def _is_same(self,other):
        if not isinstance(other, BookingRange) and self.id != other.id:
            return False
        if self.range_start == other.range_start and self.range_end == other.range_end:
            return True
        return False

    def clean(self, *args, **kwargs):
        print(self.__dict__)
        if self.range_end and self.range_end < self.range_start:
            raise ValidationError('The end date cannot be before the start date.')

    def save(self, *args, **kwargs):
        skip_validation = bool(kwargs.pop('skip_validation',False))
        if not skip_validation:
            self.full_clean()
        if self.status == 1 and not self.closure_reason:
            self.closure_reason = ClosureReason.objects.get(pk=1)
        elif self.status == 0 and not self.open_reason:
            self.open_reason = OpenReason.objects.get(pk=1)

        super(BookingRange, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {} - {}'.format(self.status, self.range_start, self.range_end)

class StayHistory(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    # minimum/maximum consecutive days allowed for a booking
    min_days = models.SmallIntegerField(default=1)
    max_days = models.SmallIntegerField(default=28)
    # Minimum and Maximum days that a booking can be made before arrival
    min_dba = models.SmallIntegerField(default=0)
    max_dba = models.SmallIntegerField(default=180)

    reason = models.ForeignKey('MaximumStayReason')
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

class MooringAreaBookingRange(BookingRange):
    campground = models.ForeignKey('MooringArea', on_delete=models.CASCADE,related_name='booking_ranges')
    # minimum/maximum number of campsites allowed for a booking
    min_sites = models.SmallIntegerField(default=1)
    max_sites = models.SmallIntegerField(default=12)

    # Properties
    # ====================================

    # Methods
    # =====================================
    def _is_same(self,other):
        if not isinstance(other, MooringAreaBookingRange) and self.id != other.id:
            return False
        if self.range_start == other.range_start and self.range_end == other.range_end:
            return True
        return False

    def clean(self, *args, **kwargs):
        original = None

        # Preventing ranges within other ranges
        within = MooringAreaBookingRange.objects.filter(Q(campground=self.campground),~Q(pk=self.pk),Q(status=self.status),Q(range_start__lte=self.range_start), Q(range_end__gte=self.range_start) | Q(range_end__isnull=True) )
        #if within:
            #raise BookingRangeWithinException('This Booking Range is within the range of another one')
        if self.pk:
            original = MooringAreaBookingRange.objects.get(pk=self.pk)
            if not original.editable:
                raise ValidationError('This Booking Range is not editable')
            if self.range_start < datetime.now().date() and original.range_start != self.range_start:
                raise ValidationError('The start date can\'t be in the past')
        super(MooringAreaBookingRange,self).clean(*args, **kwargs)


class Mooringsite(models.Model):
    mooringarea = models.ForeignKey('MooringArea', db_index=True, on_delete=models.PROTECT, related_name='campsites')
    name = models.CharField(max_length=255)
    mooringsite_class = models.ForeignKey('MooringsiteClass', on_delete=models.PROTECT, null=True,blank=True, related_name='campsites')
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    features = models.ManyToManyField('Feature')
    tent = models.BooleanField(default=True)
    campervan = models.BooleanField(default=False)
    caravan = models.BooleanField(default=False)
    min_people = models.SmallIntegerField(default=1)
    max_people = models.SmallIntegerField(default=12)
    description = models.TextField(null=True)

    def __str__(self):
        return '{} - {}'.format(self.mooringarea, self.name)

    class Meta:
        unique_together = (('mooringarea', 'name'),)

    # Properties
    # ==============================
    @property
    def type(self):
        return self.mooringsite_class.name

    @property
    def price(self):
        return 'Set at {}'.format(self.mooringarea.get_price_level_display())

    @property
    def can_add_rate(self):
        return self.mooringarea.price_level == 2

    @property
    def active(self):
        return self._is_open(datetime.now().date())

    @property
    def campground_open(self):
        return self.__is_campground_open()

    @property
    def current_closure(self):
        closure = self.__get_current_closure()
        if closure:
            return 'Start: {} End: {}'.format(closure.range_start.strftime('%d/%m/%Y'), closure.range_end.strftime('%d/%m/%Y') if closure.range_end else "")
        return ''
    # Methods
    # =======================================
    def __is_campground_open(self):
        return self.mooringarea.active

    def _is_open(self,period):
        '''Check if the campsite is open on a specified datetime
        '''
        if self.__is_campground_open():
            open_ranges, closed_ranges = None, None
            # Get all booking ranges
            try:
                open_ranges = self.booking_ranges.filter(Q(status=0),Q(range_start__lte=period), Q(range_end__gte=period) | Q(range_end__isnull=True) ).latest('updated_on')
            except MooringsiteBookingRange.DoesNotExist:
                pass
            try:
                closed_ranges = self.booking_ranges.filter(Q(range_start__lte=period),~Q(status=0),Q(range_end__gte=period) | Q(range_end__isnull=True) ).latest('updated_on')
            except MooringsiteBookingRange.DoesNotExist:
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
        b = MooringsiteBookingRange(**data)
        try:
            within = MooringsiteBookingRange.objects.filter(Q(campsite=b.campsite),Q(status=0),Q(range_start__lte=b.range_start), Q(range_end__gte=b.range_start) | Q(range_end__isnull=True) ).latest('updated_on')
            if within:
                within.updated_on = timezone.now()
                within.save(skip_validation=True)
        except MooringsiteBookingRange.DoesNotExist:
            b.save()

    def close(self, data):
        if not self.active:
            raise ValidationError('This is already closed.')
        b = MooringsiteBookingRange(**data)
        try:
            within = MooringsiteBookingRange.objects.filter(Q(campsite=b.campsite),~Q(status=0),Q(range_start__lte=b.range_start), Q(range_end__gte=b.range_start) | Q(range_end__isnull=True) ).latest('updated_on')
            if within:
                within.updated_on = timezone.now()
                within.save(skip_validation=True)
        except MooringsiteBookingRange.DoesNotExist:
            b.save()

    @staticmethod
    def bulk_create(number,data):
        try:
            created_campsites = []
            with transaction.atomic():
                campsites = []
                latest = 0
                current_campsites = Mooringsite.objects.filter(campground=data['campground'])
                cs_numbers = [int(c.name) for c in current_campsites if c.name.isdigit()]
                if cs_numbers:
                    latest = max(cs_numbers)
                for i in range(number):
                    latest += 1
                    c = Mooringsite(**data)
                    name = str(latest)
                    if len(name) == 1:
                        name = '0{}'.format(name)
                    c.name = name
                    c.save()
                    if c.campsite_class:
                        for attr in ['tent', 'campervan', 'caravan', 'min_people', 'max_people', 'description']:
                            if attr not in data:
                                setattr(c, attr, getattr(c.campsite_class, attr))
                        c.features = c.campsite_class.features.all()
                        c.save()
                    created_campsites.append(c)
            return created_campsites
        except Exception:
            raise

class MooringsiteBookingRange(BookingRange):
    campsite = models.ForeignKey('Mooringsite', on_delete=models.PROTECT,related_name='booking_ranges')

    # Properties
    # ====================================

    # Methods
    # =====================================
    def _is_same(self,other):
        if not isinstance(other, MooringsiteBookingRange) and self.id != other.id:
            return False
        if self.range_start == other.range_start and self.range_end == other.range_end:
            return True
        return False

    def clean(self, *args, **kwargs):
        original = None
        # Preventing ranges within other ranges
        within = MooringsiteBookingRange.objects.filter(Q(campsite=self.campsite),~Q(pk=self.pk),Q(status=self.status),Q(range_start__lte=self.range_start), Q(range_end__gte=self.range_start) | Q(range_end__isnull=True) )
        if within:
            raise BookingRangeWithinException('This Booking Range is within the range of another one')
        if self.pk:
            original = MooringsiteBookingRange.objects.get(pk=self.pk)
            if not original.editable:
                raise ValidationError('This Booking Range is not editable')
            if self.range_start < datetime.now().date() and original.range_start != self.range_start:
                raise ValidationError('The start date can\'t be in the past')

    def __str__(self):
        return '{}: {} {} - {}'.format(self.campsite, self.status, self.range_start, self.range_end)

class MooringsiteStayHistory(StayHistory):
    campsite = models.ForeignKey('Mooringsite', on_delete=models.PROTECT,related_name='stay_history')

class MooringAreaStayHistory(StayHistory):
    mooringarea = models.ForeignKey('MooringArea', on_delete=models.PROTECT,related_name='stay_history')

class Feature(models.Model):
    TYPE_CHOICES = (
        (0, 'Campground'),
        (1, 'Mooringsite'),
        (2, 'Not Linked')
    )
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    image = models.ImageField(null=True)
    type = models.SmallIntegerField(choices=TYPE_CHOICES,default=2,help_text="Set the model where the feature is located.")

    def __str__(self):
        return self.name


class Region(models.Model):

    ZOOM_LEVEL = (
        (0, 'default'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '4'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
        (11, '11'),
        (12, '12'),
        (13, '13'),
        (14, '14'),
        (15, '15'),
        (16, '16'),

    )


    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=16, null=True, unique=True)
    ratis_id = models.IntegerField(default=-1)
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    zoom_level = models.IntegerField(choices=ZOOM_LEVEL,default=-1)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=16, null=True, unique=True)
    region = models.ForeignKey('Region', on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)

    def __str__(self):
        return self.name


class MooringsiteClass(models.Model):

    name = models.CharField(max_length=255, unique=True)
    camp_unit_suitability = TaggableManager()
    tent = models.BooleanField(default=True)
    campervan = models.BooleanField(default=False)
    caravan = models.BooleanField(default=False)
    min_people = models.SmallIntegerField(default=1)
    max_people = models.SmallIntegerField(default=12)
    features = models.ManyToManyField('Feature')
    deleted = models.BooleanField(default=False)
    description = models.TextField(null=True)
    max_vehicles = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

    def delete(self, permanently=False,using=None):
        if not permanently:
            self.deleted = True
            self.save()
        else:
            super(MooringsiteClass, self).delete(using)

    # Property
    # ===========================
    def can_add_rate(self):
        can_add = False
        campsites = self.campsites.all()
        for c in campsites:
            if c.mooringarea.price_level == 1:
                can_add = True
                break
        return can_add

    # Methods
    # ===========================
    def createMooringsitePriceHistory(self,data):
        '''Create Multiple campsite rates
        '''
        try:
            with transaction.atomic():
                for c in self.campsites.all():
                    cr = MooringsiteRate(**data)
                    cr.campsite = c
                    cr.save()
        except Exception as e:
            raise

    def updatePriceHistory(self,original,_new):
        '''Update Multiple campsite rates
        '''
        try:
            rates = MooringsiteRate.objects.filter(**original)
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
            rates = MooringsiteRate.objects.filter(**data)
            campsites = self.campsites.all()
            with transaction.atomic():
                for r in rates:
                    if r.campsite in campsites and r.update_level == 1:
                        r.delete()
        except Exception as e:
            raise


class MooringsiteBooking(models.Model):
    BOOKING_TYPE_CHOICES = (
        (0, 'Reception booking'),
        (1, 'Internet booking'),
        (2, 'Black booking'),
        (3, 'Temporary reservation')
    )

    campsite = models.ForeignKey('Mooringsite', db_index=True, on_delete=models.PROTECT)
    date = models.DateField(db_index=True)
    booking = models.ForeignKey('Booking',related_name="campsites", on_delete=models.CASCADE, null=True)
    booking_type = models.SmallIntegerField(choices=BOOKING_TYPE_CHOICES, default=0)

    def __str__(self):
        return '{} - {}'.format(self.campsite, self.date)

    class Meta:
        unique_together = (('campsite', 'date'),)


class Rate(models.Model):
    mooring = models.DecimalField(max_digits=8, decimal_places=2, default='10.00', unique=False)
    adult = models.DecimalField(max_digits=8, decimal_places=2, default='10.00', blank=True, null=True, unique=False)
    concession = models.DecimalField(max_digits=8, decimal_places=2, default='6.60', blank=True, null=True, unique=False)
    child = models.DecimalField(max_digits=8, decimal_places=2, default='2.20', blank=True, null=True, unique=False)
    infant = models.DecimalField(max_digits=8, decimal_places=2, default='0', blank=True, null=True, unique=False)

    def __str__(self):
        return 'Mooring: ${} '.format(self.mooring,)
        #return 'adult: ${}, concession: ${}, child: ${}, infant: ${}'.format(self.adult, self.concession, self.child, self.infant)

    #class Meta:
    #    unique_together = (('adult', 'concession', 'child', 'infant'),)

    # Properties
    # =================================
    @property
    def name(self):
        return 'Mooring: ${} '.format(self.mooring,)
        #return 'adult: ${}, concession: ${}, child: ${}, infant: ${}'.format(self.adult, self.concession, self.child, self.infant)

class MooringsiteRate(models.Model):
    RATE_TYPE_CHOICES = (
        (0, 'Standard'),
        (1, 'Discounted'),
    )

    UPDATE_LEVEL_CHOICES = (
        (0, 'Mooring level'),
        (1, 'Mooring site Class level'),
        (2, 'Mooring site level'),
    )

    PRICE_MODEL_CHOICES = (
        (0, 'Price per Person'),
        (1, 'Fixed Price'),
    )

    campsite = models.ForeignKey('Mooringsite', on_delete=models.PROTECT, related_name='rates')
    rate = models.ForeignKey('Rate', on_delete=models.PROTECT)
    allow_public_holidays = models.BooleanField(default=True)
    date_start = models.DateField(default=date.today)
    date_end = models.DateField(null=True, blank=True)
    rate_type = models.SmallIntegerField(choices=RATE_TYPE_CHOICES, default=0)
    price_model = models.SmallIntegerField(choices=PRICE_MODEL_CHOICES, default=0)
    reason = models.ForeignKey('PriceReason')
    details = models.TextField(null=True,blank=True)
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
        for attr, value in data.items():
            setattr(self, attr, value)
        self.save()


class Booking(models.Model):
    BOOKING_TYPE_CHOICES = (
        (0, 'Reception booking'),
        (1, 'Internet booking'),
        (2, 'Black booking'),
        (3, 'Temporary reservation')
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True)
    legacy_id = models.IntegerField(unique=True, blank=True, null=True)
    legacy_name = models.CharField(max_length=255, blank=True,null=True)
    arrival = models.DateField()
    departure = models.DateField()
    details = JSONField(null=True, blank=True)
    booking_type = models.SmallIntegerField(choices=BOOKING_TYPE_CHOICES, default=0)
    expiry_time = models.DateTimeField(blank=True, null=True)
    cost_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    override_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    override_reason = models.ForeignKey('DiscountReason', null=True, blank=True)
    override_reason_info = models.TextField(blank=True, null=True)
    overridden_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT, blank=True, null=True, related_name='overridden_bookings')
    mooringarea = models.ForeignKey('MooringArea', null=True)
    is_canceled = models.BooleanField(default=False)
    send_invoice = models.BooleanField(default=False)
    cancellation_reason = models.TextField(null=True,blank=True)
    cancelation_time = models.DateTimeField(null=True,blank=True)
    confirmation_sent = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    canceled_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT, blank=True, null=True,related_name='canceled_bookings')

    # Properties
    # =================================
    @property
    def num_days(self):
        return (self.departure-self.arrival).days

    @property
    def stay_dates(self):
        count = self.num_days
        return '{} to {} ({} day{})'.format(self.arrival.strftime('%d/%m/%Y'), self.departure.strftime('%d/%m/%Y'), count, '' if count == 1 else 's')

    @property
    def stay_guests(self):
        num_adult = self.details.get('num_adult', 0)
        num_concession = self.details.get('num_concession', 0)
        num_infant = self.details.get('num_infant', 0)
        num_child = self.details.get('num_child', 0)
        num_mooring = self.details.get('num_mooring', 0)
        return '{} adult{}, {} concession{}, {} child{}, {} infant{}, {} mooring{}'.format(
            num_adult, '' if num_adult == 1 else 's',
            num_concession, '' if num_concession == 1 else 's',
            num_child, '' if num_child == 1 else 'ren',
            num_infant, '' if num_infant == 1 else 's',
            num_mooring, '' if num_mooring == 1 else 's',
        )

    @property
    def num_guests(self):
        if self.details:
            num_adult = self.details.get('num_adult', 0)
            num_concession = self.details.get('num_concession', 0)
            num_infant = self.details.get('num_infant', 0)
            num_child = self.details.get('num_child', 0)
            num_mooring = self.details.get('num_mooring', 0)
            return num_adult + num_concession + num_infant + num_child + num_mooring
        return 0

    @property
    def guests(self):
        if self.details:
            num_adult = self.details.get('num_adult', 0)
            num_concession = self.details.get('num_concession', 0)
            num_infant = self.details.get('num_infant', 0)
            num_child = self.details.get('num_child', 0)
            num_mooring = self.details.get('num_mooring', 0)
            return {
                "adults" : num_adult,
                "concession" : num_concession,
                "infants" : num_infant,
                "children": num_child,
                "mooring" : num_mooring
            }
        return {
            "adults" : 0,
            "concession" : 0,
            "infants" : 0,
            "children": 0,
            "mooring" : 0,
        }

    @property
    def first_campsite(self):
        cb = self.campsites.all().first()
        return cb.campsite if cb else None

    @property
    def editable(self):
        today = datetime.now().date()
        if today <= self.departure:
            if not self.is_canceled:
                return True
        return False

    @property
    def campsite_id_list(self):
        return list(set([x['campsite'] for x in self.campsites.all().values('campsite')]))

    @property
    def campsite_name_list(self):
        return list(set(self.campsites.values_list('campsite__name', flat=True)))

    @property
    def paid(self):
        if self.legacy_id and self.invoices.count() < 1:
            return True
        else:
            payment_status = self.__check_payment_status()
            if payment_status == 'paid' or payment_status == 'over_paid':
                return True
        return False

    @property
    def unpaid(self):
        if self.legacy_id and self.invoices.count() < 1:
            return False
        else:
            payment_status = self.__check_payment_status()
            if payment_status == 'unpaid':
                return True
        return False

    @property
    def amount_paid(self):
        return self.__check_payment_amount()

    @property
    def refund_status(self):
        return self.__check_refund_status()

    @property
    def outstanding(self):
        return self.__outstanding_amount()

    @property
    def status(self):
        if (self.legacy_id and self.invoices.count() >= 1) or not self.legacy_id:
            payment_status = self.__check_payment_status()
            status =  ''
            parts = payment_status.split('_')
            for p in parts:
                status += '{} '.format(p.title())
            status = status.strip()
            if self.is_canceled:
                if payment_status == 'over_paid' or payment_status == 'paid':
                    return 'Cancelled - Payment ({})'.format(status)
                else:
                    return 'Cancelled'
            else:
                return status
        return 'Paid'

    @property
    def confirmation_number(self):
        return 'PS{}'.format(self.pk)

    @property
    def active_invoice(self):
        active_invoices = Invoice.objects.filter(reference__in=[x.invoice_reference for x in self.invoices.all()]).order_by('-created')
        return active_invoices[0] if active_invoices else None

    @property
    def has_history(self):
        return self.history.count() > 0

    # Methods
    # =================================
    def clean(self,*args,**kwargs):
        #Check for existing bookings in current date range
        arrival = self.arrival
        departure = self.departure
        customer = self.customer

        other_bookings = Booking.objects.filter(Q(departure__gt=arrival,departure__lte=departure) | Q(arrival__gte=arrival,arrival__lt=departure),customer=customer)
        if self.pk:
            other_bookings.exclude(id=self.pk)
        if customer and other_bookings and self.booking_type != 3:
            raise ValidationError('You cannot make concurrent bookings.')
        #if not self.mooringarea.oracle_code:
        #    raise ValidationError('Campground does not have an Oracle code.')
        if self.mooringarea.park.entry_fee_required and not self.mooringarea.park.oracle_code:
            raise ValidationError('MarinePark does not have an Oracle code.')
        super(Booking,self).clean(*args,**kwargs)

    def __str__(self):
        return '{}: {} - {}'.format(self.customer, self.arrival, self.departure)

    def __check_payment_amount(self):
        invoices = []
        amount = D('0.0')
        references = [i.invoice_reference for i in self.invoices.all()]
        #invoices = Invoice.objects.filter(reference__in=references,voided=False)
        if self.active_invoice:
            amount = self.active_invoice.payment_amount
        elif self.legacy_id:
            amount =  D(self.cost_total)
        return amount

    def __check_payment_status(self):
        invoices = []
        amount = D('0.0')
        references = self.invoices.all().values('invoice_reference')
        for r in references:
            try:
                invoices.append(Invoice.objects.get(reference=r.get("invoice_reference")))
            except Invoice.DoesNotExist:
                pass
        for i in invoices:
            if not i.voided:
                amount += i.payment_amount

        if amount == 0:
            return 'unpaid'
        if self.cost_total < amount:
            return 'over_paid'
        elif self.cost_total > amount:
            return 'partially_paid'
        else:return "paid"

    def __check_refund_status(self):
        invoices = []
        amount = D('0.0')
        refund_amount = D('0.0')
        references = self.invoices.all().values_list('invoice_reference', flat=True)
        invoices = Invoice.objects.filter(reference__in=references)
        for i in invoices:
            if i.voided:
                amount += i.total_payment_amount
                refund_amount += i.refund_amount

        if amount == 0:
            return 'Not Paid'
        if refund_amount > 0 and amount > refund_amount:
            return 'Partially Refunded'
        elif refund_amount == amount:
            return 'Refunded'
        else:return "Not Refunded"

    def __outstanding_amount(self):
        invoices = []
        amount = D('0.0')
        references = self.invoices.all().values('invoice_reference')
        for r in references:
            try:
                invoices.append(Invoice.objects.get(reference=r.get("invoice_reference")))
            except Invoice.DoesNotExist:
                pass
        for i in invoices:
            if not i.voided:
                amount += i.balance

        return amount

    def cancelBooking(self,reason,user=None):
        if not reason:
            raise ValidationError('A reason is needed before canceling a booking')
        today = datetime.now().date()
        if today > self.departure:
            raise ValidationError('You cannot cancel a booking past the departure date.')
        self._generate_history(user=user)
        if user:
            self.canceled_by = user
        self.cancellation_reason = reason
        self.is_canceled = True
        self.cancelation_time = timezone.now()
        self.campsites.all().delete()
        references = self.invoices.all().values('invoice_reference')
        for r in references:
            try:
                i = Invoice.objects.get(reference=r.get("invoice_reference"))
                i.voided = True
                i.save()
            except Invoice.DoesNotExist:
                pass

        self.save()

    def _generate_history(self,user=None):
        campsites = list(set([x.campsite.name for x in self.campsites.all()]))
        vessels = [{'rego':x.rego,'type':x.type,'entry_fee':x.entry_fee,'park_entry_fee':x.park_entry_fee} for x in self.regos.all()]
        BookingHistory.objects.create(
            booking = self,
            updated_by=user,
            arrival = self.arrival,
            departure = self.departure,
            details = self.details,
            cost_total = self.cost_total,
            confirmation_sent = self.confirmation_sent,
            campground = self.mooringarea.name,
            campsites = campsites,
            vessels = vessels,
            invoice=self.active_invoice
        )
    
    @property
    def vehicle_payment_status(self):
        # Get current invoice
        inv  = None
        payment_dict = []
        references = [i.invoice_reference for i in self.invoices.all()]
        #temp_invoices = Invoice.objects.filter(reference__in=references,voided=False)
        temp_invoices = [self.active_invoice] if self.active_invoice else []
        if len(temp_invoices) == 1 or self.legacy_id:
            if not self.legacy_id:
                inv = temp_invoices[0]
            # Get all lines 
            total_paid = D('0.0')
            total_due = D('0.0')
            lines = []
            if not self.legacy_id:
                lines = inv.order.lines.filter(oracle_code=self.mooringarea.park.oracle_code)

            price_dict = {}
            for line in lines:
                total_paid += line.paid
                total_due += line.unit_price_incl_tax * line.quantity
                price_dict[line.oracle_code] = line.unit_price_incl_tax

            remainder_amount = total_due - total_paid
            # Allocate amounts to each vehicle
            for r in self.regos.all():
                paid = False
                show_paid = True
                if self.legacy_id:
                    paid = False
                elif not r.park_entry_fee:
                    show_paid = False
                    paid = True
                elif remainder_amount == 0:
                    paid = True
                elif total_paid == 0:
                    pass
                else:
                    required_total = D('0.0')
                    for k,v in price_dict.items():
                        required_total += D(v)
                    if required_total <= total_paid:
                        total_paid -= required_total
                        paid = True
                data = {
                    'Rego': r.rego.upper(),
                    'Type': r.get_type_display(),
                    'original_type': r.type,
                    'Fee': r.entry_fee,
                }
                if show_paid:
                    data['Paid'] = 'pass_required' if not r.entry_fee and not self.legacy_id else 'Yes' if paid else 'No'
                payment_dict.append(data)
        else:
            pass
        return payment_dict

class BookingHistory(models.Model):
    booking = models.ForeignKey(Booking,related_name='history')
    created = models.DateTimeField(auto_now_add=True)
    arrival = models.DateField()
    departure = models.DateField()
    details = JSONField()
    cost_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    confirmation_sent = models.BooleanField()
    campground = models.CharField(max_length=100)
    campsites = JSONField()
    vessels = JSONField()
    updated_by = models.ForeignKey(EmailUser,on_delete=models.PROTECT, blank=True, null=True)
    invoice=models.ForeignKey(Invoice,null=True,blank=True)

class OutstandingBookingRecipient(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email

class BookingInvoice(models.Model):
    booking = models.ForeignKey(Booking, related_name='invoices')
    invoice_reference = models.CharField(max_length=50, null=True, blank=True, default='')

    def __str__(self):
        return 'Booking {} : Invoice #{}'.format(self.id,self.invoice_reference)

    # Properties
    # ==================
    @property
    def active(self):
        try:
            invoice = Invoice.objects.get(reference=self.invoice_reference)
            return False if invoice.voided else True
        except Invoice.DoesNotExist:
            pass
        return False

class BookingVehicleRego(models.Model):
    """docstring for BookingVehicleRego."""
    VEHICLE_CHOICES = (
#        ('vehicle','Vehicle'),
        ('vessel','Vessel'),
#        ('motorbike','Motorcycle'),
#        ('concession','Vehicle (concession)')
    )

    booking = models.ForeignKey(Booking, related_name = "regos")
    rego = models.CharField(max_length=50)
    type = models.CharField(max_length=10,choices=VEHICLE_CHOICES)
    entry_fee = models.BooleanField(default=False)
    park_entry_fee = models.BooleanField(default=False)

    class Meta:
        unique_together = ('booking','rego')

class MarinaEntryRate(models.Model):

    vehicle = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    concession = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    motorbike = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    period_start = models.DateField()
    period_end = models.DateField(null=True,blank=True)
    reason = models.ForeignKey("PriceReason",on_delete=models.PROTECT)
    details = models.TextField(null = True, blank= True)

    def clean(self,*args,**kwargs):
        if self.reason.id == 1 and not self.details:
            raise ValidationError("Details cannot be empty if reason is Other")
        super(MarinaEntryRate,self).clean(*args,**kwargs)

    def save(self, *args,**kwargs):
        self.full_clean()
        super(MarinaEntryRate,self).save(*args,**kwargs)

    @property
    def editable(self):
        today = datetime.now().date()
        return (self.period_start > today and not self.period_end) or ( self.period_start > today <= self.period_end)


# REASON MODELS
# =====================================
class Reason(models.Model):
    text = models.TextField()
    editable = models.BooleanField(default=True,editable=False)

    class Meta:
        ordering = ('id',)
        abstract = True

    # Properties
    # ==============================
    def code(self):
        return self.__get_code()

    # Methods
    # ==============================
    def __get_code(self):
        length = len(str(self.id))
        val = '0'
        return '{}{}'.format((val*(4-length)),self.id)

class MaximumStayReason(Reason):
    pass

class ClosureReason(Reason):
    pass

class OpenReason(Reason):
    pass

class PriceReason(Reason):
    pass
class DiscountReason(Reason):
    pass

# VIEWS
# =====================================
class ViewPriceHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    date_start = models.DateField()
    date_end = models.DateField()
    rate_id = models.IntegerField()
    mooring = models.DecimalField(max_digits=8, decimal_places=2)
    adult = models.DecimalField(max_digits=8, decimal_places=2)
    concession = models.DecimalField(max_digits=8, decimal_places=2)
    child = models.DecimalField(max_digits=8, decimal_places=2)
    details = models.TextField()
    reason_id = models.IntegerField()
    infant = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        abstract =True

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

    @property
    def reason(self):
        reason = ''
        if self.reason_id:
            reason = self.reason_id
        return reason

class MooringAreaPriceHistory(ViewPriceHistory):
    class Meta:
        managed = False
        db_table = 'mooring_mooringarea_pricehistory_v'
        ordering = ['-date_start',]

class MooringsiteClassPriceHistory(ViewPriceHistory):
    class Meta:
        managed = False
        db_table = 'mooring_mooringsiteclass_pricehistory_v'
        ordering = ['-date_start',]

# LISTENERS
# ======================================
class MooringAreaBookingRangeListener(object):
    """
    Event listener for MooringAreaBookingRange 
    """

    @staticmethod
    @receiver(pre_save, sender=MooringAreaBookingRange)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = MooringAreaBookingRange.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

            if not instance._is_same(original_instance):
                instance.updated_on = timezone.now()
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = MooringAreaBookingRange.objects.filter(~Q(id=instance.id),Q(campground=instance.campground),Q(range_start__lte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True) )
                for w in within:
                    w.range_end = instance.range_start
                    w.save(skip_validation=True)
            except MooringAreaBookingRange.DoesNotExist:
                pass
        if instance.status == 0 and not instance.range_end:
            try:
                another_open = MooringAreaBookingRange.objects.filter(campground=instance.campground,range_start=instance.range_start+timedelta(days=1),status=0).latest('updated_on')
                instance.range_end = instance.range_start
            except MooringAreaBookingRange.DoesNotExist:
                pass

    @staticmethod
    @receiver(post_delete, sender=MooringAreaBookingRange)
    def _post_delete(sender, instance, **kwargs):
        today = datetime.now().date()
        if instance.status != 0 and instance.range_end:
            try:
                linked_open = MooringAreaBookingRange.objects.filter(range_start=instance.range_end + timedelta(days=1), status=0).order_by('updated_on')
                if instance.range_start >= today:
                    if linked_open:
                        linked_open = linked_open[0]
                        linked_open.range_start = instance.range_start
                    else:
                        linked_open = None
                else:
                    if linked_open:
                        linked_open = linked_open[0]
                        linked_open.range_start = today
                    else:
                        linked_open = None
                if linked_open:
                    linked_open.save(skip_validation=True)
            except MooringAreaBookingRange.DoesNotExist:
                pass
        elif instance.status != 0 and not instance.range_end:
            try:
                if instance.range_start >= today:
                    MooringAreaBookingRange.objects.create(campground=instance.campground,range_start=instance.range_start,status=0)
                else:
                    MooringAreaBookingRange.objects.create(campsite=instance.campground,range_start=today,status=0)
            except:
                pass
        cache.delete('campgrounds_dt')

    @staticmethod
    @receiver(post_save, sender=MooringAreaBookingRange)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            pass

        # Check if its a closure and has an end date to create new opening range
        if instance.status != 0 and instance.range_end:
            another_open = MooringAreaBookingRange.objects.filter(campground=instance.campground,range_start=datetime.now().date()+timedelta(days=1),status=0)
            if not another_open:
                try:
                    MooringAreaBookingRange.objects.create(campground=instance.campground,range_start=instance.range_end+timedelta(days=1),status=0)
                except BookingRangeWithinException as e:
                    pass

class MarinaAreaListener(object):
    """
    Event listener for Campgrounds
    """

    @staticmethod
    @receiver(pre_save, sender=MooringArea)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = MarinePark.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=MooringArea)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            # Create an opening booking range on creation of Campground
             MooringAreaBookingRange.objects.create(campground=instance,range_start=datetime.now().date(),status=0)
        else:
            pass
            #if original_instance.price_level != instance.price_level:
                # Get all campsites
            #    today = datetime.now().date()
            #    campsites = instance.campsites.all()
            #    campsite_list = campsites.values_list('id', flat=True)
            #    rates = MooringsiteRate.objects.filter(campsite__in=campsite_list,update_level=original_instance.price_level)
            #    current_rates = rates.filter(Q(date_end__isnull=True),Q(date_start__lte =  today)).update(date_end=today)
            #    future_rates = rates.filter(date_start__gt = today).delete()
            #    if instance.price_level == 1:
            #        #Check if there are any existant campsite class rates
            #        for c in campsites:
            #            try:
            #                ch = MooringsiteClassPriceHistory.objects.get(Q(date_end__isnull=True),id=c.campsite_class_id,date_start__lte = today)
            #                cr = MooringsiteRate(campsite=c,rate_id=ch.rate_id,date_start=today + timedelta(days=1))
            #                cr.save()
            #            except MooringsiteClassPriceHistory.DoesNotExist:
             #               pass
             #           except Exception:
             #               pass

class MooringsiteBookingRangeListener(object):
    """
    Event listener for MooringsiteBookingRange
    """

    @staticmethod
    @receiver(pre_save, sender=MooringsiteBookingRange)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = MooringsiteBookingRange.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

            if not instance._is_same(original_instance):
                instance.updated_on = timezone.now()
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = MooringsiteBookingRange.objects.get(Q(campsite=instance.campsite),Q(range_start__lte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True) )
                within.range_end = instance.range_start
                within.save(skip_validation=True)
            except MooringsiteBookingRange.DoesNotExist:
                pass
        if instance.status == 0 and not instance.range_end:
            try:
                another_open = MooringsiteBookingRange.objects.filter(campsite=instance.campsite,range_start=instance.range_start+timedelta(days=1),status=0).latest('updated_on')
                instance.range_end = instance.range_start
            except MooringsiteBookingRange.DoesNotExist:
                pass

    @staticmethod
    @receiver(post_delete, sender=MooringsiteBookingRange)
    def _post_delete(sender, instance, **kwargs):
        today = datetime.now().date()
        if instance.status != 0 and instance.range_end:
            try:
                linked_open = MooringsiteBookingRange.objects.get(range_start=instance.range_end + timedelta(days=1), status=0)
                if instance.range_start >= today:
                    if linked_open:
                        linked_open = linked_open[0]
                        linked_open.range_start = instance.range_start
                    else:
                        linked_open = None
                else:
                    if linked_open:
                        linked_open = linked_open[0]
                        linked_open.range_start = today
                    else:
                        linked_open = None
                if linked_open:
                    linked_open.save(skip_validation=True)
            except MooringsiteBookingRange.DoesNotExist:
                pass
        elif instance.status != 0 and not instance.range_end:
            try:
                if instance.range_start >= today:
                    MooringsiteBookingRange.objects.create(campsite=instance.campsite,range_start=instance.range_start,status=0)
                else:
                    MooringsiteBookingRange.objects.create(campsite=instance.campsite,range_start=today,status=0)
            except:
                pass

    @staticmethod
    @receiver(post_save, sender=MooringsiteBookingRange)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            pass

        # Check if its a closure and has an end date to create new opening range
        if instance.status != 0 and instance.range_end:
            another_open = MooringsiteBookingRange.objects.filter(campsite=instance.campsite,range_start=datetime.now().date()+timedelta(days=1),status=0)

            if not another_open:
                try:
                    MooringsiteBookingRange.objects.create(campsite=instance.campsite,range_start=instance.range_end+timedelta(days=1),status=0)
                except BookingRangeWithinException as e:
                    pass

class BookingListener(object):
    """
    Event listener for Bookings
    """

    @staticmethod
    @receiver(pre_save, sender=Booking)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Booking.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            instance.full_clean()

class MooringsiteListener(object):
    """
    Event listener for Mooringsites
    """

    @staticmethod
    @receiver(pre_save, sender=Mooringsite)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Mooringsite.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Mooringsite)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            # Create an opening booking range on creation of Campground
             MooringsiteBookingRange.objects.create(campsite=instance,range_start=datetime.now().date(),status=0)

class MooringsiteRateListener(object):
    """
    Event listener for Mooringsite Rate
    """

    @staticmethod
    @receiver(pre_save, sender=MooringsiteRate)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = MooringsiteRate.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = MooringsiteRate.objects.get(Q(campsite=instance.campsite),Q(date_start__lte=instance.date_start), Q(date_end__gte=instance.date_start) | Q(date_end__isnull=True) )
                within.date_end = instance.date_start - timedelta(days=2)
                within.save()
            except MooringsiteRate.DoesNotExist:
                pass
            # check if there is a newer record and set the end date as the previous record minus 1 day
            x = MooringsiteRate.objects.filter(Q(campsite=instance.campsite),Q(date_start__gte=instance.date_start), Q(date_end__gte=instance.date_start) | Q(date_end__isnull=True) ).order_by('date_start')
            if x:
                x = x[0]
                instance.date_end = x.date_start - timedelta(days=2)

    @staticmethod
    @receiver(pre_delete, sender=MooringsiteRate)
    def _pre_delete(sender, instance, **kwargs):
        if not instance.date_end:
            c = MooringsiteRate.objects.filter(campsite=instance.campsite).order_by('-date_start').exclude(id=instance.id)
            if c:
                c = c[0] 
                c.date_end = None
                c.save() 

class MooringsiteStayHistoryListener(object):
    """
    Event listener for Mooringsite Stay History
    """

    @staticmethod
    @receiver(pre_save, sender=MooringsiteStayHistory)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = MooringsiteStayHistory.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = MooringsiteStayHistory.objects.get(Q(campsite=instance.campsite),Q(range_start__lte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True) )
                within.range_end = instance.range_start - timedelta(days=1)
                within.save()
            except MooringsiteStayHistory.DoesNotExist:
                pass

    @staticmethod
    @receiver(post_delete, sender=MooringsiteStayHistory)
    def _post_delete(sender, instance, **kwargs):
        if not instance.range_end:
            MooringsiteStayHistory.objects.filter(range_end=instance.range_start- timedelta(days=1),campsite=instance.campsite).update(range_end=None)

class MarinaAreaStayHistoryListener(object):
    """
    Event listener for Campground Stay History
    """

    @staticmethod
    @receiver(pre_save, sender=MooringAreaStayHistory)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = MooringAreaStayHistory.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = MooringAreaStayHistory.objects.get(Q(mooringarea=instance.mooringarea),Q(range_start__lte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True) )
                within.range_end = instance.range_start - timedelta(days=2)
                within.save()
            except MooringAreaStayHistory.DoesNotExist:
                pass

            # check if there is a newer record and set the end date as the previous record minus 1 day
            x = MooringAreaStayHistory.objects.filter(Q(mooringarea=instance.mooringarea),Q(range_start__gte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True) ).order_by('range_start')
            if x:
                x = x[0]
                instance.date_end = x.date_start - timedelta(days=2)

    @staticmethod
    @receiver(pre_delete, sender=MooringAreaStayHistory)
    def _pre_delete(sender, instance, **kwargs):
        if not instance.range_end:
            c = MooringAreaStayHistory.objects.filter(mooringarea=instance.mooringarea).order_by('-range_start').exclude(id=instance.id)
            if c:
                c = c[0]
                c.date_end = None
                c.save()

class MarinaEntryRateListener(object):
    """
    Event listener for MarinaEntryRate
    """

    @staticmethod
    @receiver(pre_save, sender=MarinaEntryRate)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = MarinaEntryRate.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
            price_before = MarinaEntryRate.objects.filter(period_start__lt=instance.period_start).order_by("-period_start")
            if price_before:
                price_before = price_before[0]
                price_before.period_end = instance.period_start
                instance.period_start = instance.period_start + timedelta(days=1)
                price_before.save()
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                price_before = MarinaEntryRate.objects.filter(period_start__lt=instance.period_start).order_by("-period_start")
                if price_before:
                    price_before = price_before[0]
                    price_before.period_end = instance.period_start
                    price_before.save()
                    instance.period_start = instance.period_start + timedelta(days=1)
                price_after = MarinaEntryRate.objects.filter(period_start__gt=instance.period_start).order_by("period_start")
                if price_after:
                    price_after = price_after[0]
                    instance.period_end = price_after.period_start - timedelta(days=1)
            except Exception as e:
                pass

    @staticmethod
    @receiver(post_delete, sender=MarinaEntryRate)
    def _post_delete(sender, instance, **kwargs):
        price_before = MarinaEntryRate.objects.filter(period_start__lt=instance.period_start).order_by("-period_start")
        price_after = MarinaEntryRate.objects.filter(period_start__gt=instance.period_start).order_by("period_start")
        if price_after:
            price_after = price_after[0]
            if price_before:
                price_before = price_before[0]
                price_before.period_end =  price_after.period_start - timedelta(days=1)
                price_before.save()
        elif price_before:
            price_before = price_before[0]
            price_before.period_end = None
            price_before.save()
