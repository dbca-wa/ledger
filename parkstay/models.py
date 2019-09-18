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
from django.db import transaction
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from django.conf import settings
from taggit.managers import TaggableManager
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save, post_save, pre_delete
from django.core.cache import cache
from ledger.payments.models import Invoice
from ledger.accounts.models import EmailUser


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


class Contact(models.Model):
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=255)
    description = models.TextField(null=True, blank=True)
    opening_hours = models.TextField(null=True)
    other_services = models.TextField(null=True)

    def __str__(self):
        return "{}: {}".format(self.name, self.phone_number)


class Park(models.Model):
    name = models.CharField(max_length=255)
    district = models.ForeignKey('District', null=True, on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)
    entry_fee_required = models.BooleanField(default=True)
    oracle_code = models.CharField(max_length=50, null=True, blank=True)
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.district)

    def clean(self, *args, **kwargs):
        if self.entry_fee_required and not self.oracle_code:
            raise ValidationError('A park entry oracle code is required if entry fee is required.')

    def save(self, *args, **kwargs):
        cache.delete('parks')
        self.full_clean()
        super(Park, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('name',),)


class PromoArea(models.Model):
    name = models.CharField(max_length=255, unique=True)
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)

    def __str__(self):
        return self.name


def update_campground_map_filename(instance, filename):
    return 'parkstay/campground_maps/{}/{}'.format(instance.id, filename)


class Campground(models.Model):

    CAMPGROUND_TYPE_CHOICES = (
        (0, 'Bookable Online'),
        (1, 'Not Bookable Online'),
        (2, 'Other Accomodation'),
        (3, 'Unpublished'),
    )
    CAMPGROUND_PRICE_LEVEL_CHOICES = (
        (0, 'Campground level'),
        (1, 'Campsite Class level'),
        (2, 'Campsite level'),
    )
    SITE_TYPE_CHOICES = (
        (0, 'Bookable Per Site'),
        (1, 'Bookable Per Site Type'),
        (2, 'Bookable Per Site Type (hide site number)'),
    )

    name = models.CharField(max_length=255, null=True)
    park = models.ForeignKey('Park', on_delete=models.PROTECT, related_name='campgrounds')
    ratis_id = models.IntegerField(default=-1)
    contact = models.ForeignKey('Contact', on_delete=models.PROTECT, blank=True, null=True)
    campground_type = models.SmallIntegerField(choices=CAMPGROUND_TYPE_CHOICES, default=3)
    promo_area = models.ForeignKey('PromoArea', on_delete=models.PROTECT, blank=True, null=True)
    site_type = models.SmallIntegerField(choices=SITE_TYPE_CHOICES, default=0)
    address = JSONField(null=True, blank=True)
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
    long_description = models.TextField(blank=True, null=True)

    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    dog_permitted = models.BooleanField(default=False)
    check_in = models.TimeField(default=time(14))
    check_out = models.TimeField(default=time(10))
    max_advance_booking = models.IntegerField(default=180)
    oracle_code = models.CharField(max_length=50, null=True, blank=True)
    campground_map = models.FileField(upload_to=update_campground_map_filename, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        cache.delete('campgrounds')
        cache.delete('campgrounds_dt')
        super(Campground, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('name', 'park'),)

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
    def current_closure_id(self):
        closure = self._get_current_closure()
        if closure:
            return closure.id
        return None

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
    def _is_open(self, period):
        '''Check if the campground is open on a specified datetime
        '''
        # Get all booking ranges
        range_qs = self.get_booking_ranges(period)
        try:
            range_qs.exclude(status=0).latest('updated_on')
        except CampgroundBookingRange.DoesNotExist:
            return True

        return False

    def _get_current_closure(self):
        closure_period = None
        period = datetime.now().date()
        if not self.active:
            closure = self.get_booking_ranges(period).exclude(status=0)
            if closure:
                closure_period = closure.latest('updated_on')
        return closure_period

    def get_booking_ranges(self, start_date, end_date=None, overlap=True, endless=False):
        if end_date is None:
            end_date = start_date + timedelta(days=1)
        params = [
            Q(range_end__gt=start_date) | Q(range_end__isnull=True)
        ]
        if not endless:
            params.append(Q(range_start__lt=end_date))
        if overlap:
            range_qs = self.booking_ranges.filter(*params)
        else:
            range_qs = self.booking_ranges.exclude(*params)
        return range_qs

    def close(self, data):
        closure = CampgroundBookingRange(**data)
        closure.save()

    def get_cheapest_rate(self):
        # Find the cheapest, current site rate for a campground.
        # Aggregate all sites:
        sites = [site for site in self.campsites.all()]
        if not sites:
            return None
        # Aggregate all current rates for those sites.
        rates = [rate for rate in site.rates.current() for site in sites]
        if rates:
            # Return the minimum adult rate:
            return min(rate.rate.adult for rate in rates)
        else:
            return None

    def createCampsitePriceHistory(self, data):
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

    def updatePriceHistory(self, original, _new):
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

    def deletePriceHistory(self, data):
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


def campground_image_path(instance, filename):
    return '/'.join(['parkstay', 'campground_images', filename])


class CampgroundGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(EmailUser, blank=True)
    campgrounds = models.ManyToManyField(Campground, blank=True)

    def __str__(self):
        return self.name


class CampgroundImage(models.Model):
    image = models.ImageField(max_length=255, upload_to=campground_image_path)
    campground = models.ForeignKey(Campground, related_name='images', on_delete=models.CASCADE)
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
        file_extension = self.get_file_extension(file_name, decoded_file)
        complete_file_name = "{}.{}".format(file_name, file_extension)
        uploaded_image = ContentFile(decoded_file, name=complete_file_name)
        return uploaded_image

    def save(self, *args, **kwargs):
        self.checksum = self._calculate_checksum(self.image)
        self.image.seek(0)
        if not self.pk:
            self.image = self.createImage(base64.b64encode(self.image.read()))
        else:
            orig = CampgroundImage.objects.get(pk=self.pk)
            if orig.image:
                if orig.checksum != self.checksum:
                    if os.path.isfile(orig.image.path):
                        os.remove(orig.image)
                    self.image = self.createImage(base64.b64encode(self.image.read()))
                else:
                    pass

        super(CampgroundImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            os.remove(self.image)
        except BaseException:
            pass
        super(CampgroundImage, self).delete(*args, **kwargs)


class BookingRange(models.Model):
    BOOKING_RANGE_CHOICES = (
        (0, 'Open'),        # not used
        (1, 'Closed'),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True, help_text='Used to check if the start and end dated were changed')

    status = models.SmallIntegerField(choices=BOOKING_RANGE_CHOICES, default=0)
    closure_reason = models.ForeignKey('ClosureReason', null=True, blank=True, on_delete=models.CASCADE)
    details = models.TextField(blank=True, null=True)
    range_start = models.DateField(blank=True, null=True)
    range_end = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    # Properties
    # ====================================
    @property
    def editable(self):
        today = datetime.now().date()
        if self.status != 0 and((self.range_start <= today and not self.range_end) or (self.range_start <= today and self.range_end > today) or (self.range_start > today and not self.range_end) or (self.range_start >= today <= self.range_end)):
            return True
        elif self.status == 0 and ((self.range_start <= today and not self.range_end) or self.range_start > today):
            return True
        return False

    @property
    def reason(self):
        return self.closure_reason.text

    # Methods
    # =====================================
    def _is_same(self, other):
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
        skip_validation = bool(kwargs.pop('skip_validation', False))
        if not skip_validation:
            self.full_clean()
        if self.status == 1 and not self.closure_reason:
            self.closure_reason = ClosureReason.objects.get(pk=1)

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

    reason = models.ForeignKey('MaximumStayReason', on_delete=models.CASCADE)
    details = models.TextField(blank=True, null=True)
    range_start = models.DateField(blank=True, null=True)
    range_end = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    # Properties
    # ====================================
    @property
    def editable(self):
        now = datetime.now().date()
        if (self.range_start <= now and not self.range_end) or (self.range_start <= now <= self.range_end):
            return True
        elif (self.range_start >= now and not self.range_end) or (self.range_start >= now <= self.range_end):
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
    campground = models.ForeignKey('Campground', on_delete=models.CASCADE, related_name='booking_ranges')
    # minimum/maximum number of campsites allowed for a booking
    min_sites = models.SmallIntegerField(default=1)
    max_sites = models.SmallIntegerField(default=12)

    # Properties
    # ====================================

    # Methods
    # =====================================
    def _is_same(self, other):
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
            # if self.range_start < datetime.now().date() and original.range_start != self.range_start:
            #    raise ValidationError('The start date can\'t be in the past')
        super(CampgroundBookingRange, self).clean(*args, **kwargs)


class Campsite(models.Model):
    campground = models.ForeignKey('Campground', db_index=True, on_delete=models.PROTECT, related_name='campsites')
    name = models.CharField(max_length=255)
    campsite_class = models.ForeignKey('CampsiteClass', on_delete=models.PROTECT, null=True, blank=True, related_name='campsites')
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    features = models.ManyToManyField('Feature')
    tent = models.BooleanField(default=True)
    campervan = models.BooleanField(default=False)
    caravan = models.BooleanField(default=False)
    min_people = models.SmallIntegerField(default=1)
    max_people = models.SmallIntegerField(default=12)
    max_vehicles = models.PositiveIntegerField(default=1)
    description = models.TextField(null=True)

    def __str__(self):
        return '{} - {}'.format(self.campground, self.name)

    class Meta:
        unique_together = (('campground', 'name'),)

    # Properties
    # ==============================
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
        closure = self.__get_current_closure()
        if closure:
            return 'Start: {} Reopen: {}'.format(closure.range_start.strftime('%d/%m/%Y'), closure.range_end.strftime('%d/%m/%Y') if closure.range_end else "")
        return ''

    @property
    def current_closure_id(self):
        closure = self.__get_current_closure()
        if closure:
            return closure.id
        return None

    # Methods
    # =======================================
    def __is_campground_open(self):
        return self.campground.active

    def _is_open(self, period):
        '''Check if the campsite is open on a specified datetime
        '''
        if self.__is_campground_open():
            # Get all closure ranges
            range_qs = self.get_booking_ranges(period)
            try:
                range_qs.exclude(status=0).latest('updated_on')
            except CampsiteBookingRange.DoesNotExist:
                return True

        return False

    def __get_current_closure(self):
        if self.__is_campground_open():
            closure_period = None
            period = datetime.now().date()
            if not self.active:
                closure = self.get_booking_ranges(period).exclude(status=0).latest('updated_on')
                closure_period = closure
            return closure_period
        else:
            return self.campground._get_current_closure()

    def get_booking_ranges(self, start_date, end_date=None, overlap=True, endless=False):
        if end_date is None:
            end_date = start_date + timedelta(days=1)
        params = [
            Q(range_end__gt=start_date) | Q(range_end__isnull=True)
        ]
        if not endless:
            params.append(Q(range_start__lt=end_date))
        if overlap:
            range_qs = self.booking_ranges.filter(*params)
        else:
            range_qs = self.booking_ranges.exclude(*params)
        return range_qs

    def close(self, data):
        closure = CampsiteBookingRange(**data)
        closure.save()

    @staticmethod
    def bulk_create(number, data):
        try:
            created_campsites = []
            with transaction.atomic():
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
                        for attr in ['tent', 'campervan', 'caravan', 'min_people', 'max_people', 'description']:
                            if attr not in data:
                                setattr(c, attr, getattr(c.campsite_class, attr))
                        c.features = c.campsite_class.features.all()
                        c.save()
                    created_campsites.append(c)
            return created_campsites
        except Exception:
            raise


class CampsiteBookingRange(BookingRange):
    campsite = models.ForeignKey('Campsite', on_delete=models.PROTECT, related_name='booking_ranges')

    # Properties
    # ====================================

    # Methods
    # =====================================
    def _is_same(self, other):
        if not isinstance(other, CampsiteBookingRange) and self.id != other.id:
            return False
        if self.range_start == other.range_start and self.range_end == other.range_end:
            return True
        return False

    def clean(self, *args, **kwargs):
        if self.pk:
            original = CampsiteBookingRange.objects.get(pk=self.pk)
            if not original.editable:
                raise ValidationError('This Booking Range is not editable')
            # if self.range_start < datetime.now().date() and original.range_start != self.range_start:
            #    raise ValidationError('The start date can\'t be in the past')
        super(CampsiteBookingRange, self).clean(*args, **kwargs)

    def __str__(self):
        return '{}: {} {} - {}'.format(self.campsite, self.status, self.range_start, self.range_end)


class CampsiteStayHistory(StayHistory):
    campsite = models.ForeignKey('Campsite', on_delete=models.PROTECT, related_name='stay_history')


class CampgroundStayHistory(StayHistory):
    campground = models.ForeignKey('Campground', on_delete=models.PROTECT, related_name='stay_history')


class Feature(models.Model):
    TYPE_CHOICES = (
        (0, 'Campground'),
        (1, 'Campsite'),
        (2, 'Not Linked')
    )
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    image = models.ImageField(null=True)
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=2, help_text="Set the model where the feature is located.")

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

    def delete(self, permanently=False, using=None):
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
    def createCampsitePriceHistory(self, data):
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

    def updatePriceHistory(self, original, _new):
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

    def deletePriceHistory(self, data):
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
        (2, 'Black booking'),
        (3, 'Temporary reservation')
    )

    campsite = models.ForeignKey('Campsite', db_index=True, on_delete=models.PROTECT)
    date = models.DateField(db_index=True)
    booking = models.ForeignKey('Booking', related_name="campsites", on_delete=models.CASCADE, null=True)
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


class CampsiteRateManager(models.Manager):
    """Define a custom model manager for CampsiteRate objects, having a
    method to filter on "current" rates only (i.e. those without a date_end
    OR a date_end >= today, AND a date_start <= today.
    Assuming business rules are applied correctly, this should return one rate.
    """
    def current(self):
        return self.filter(Q(date_end__gte=date.today()) | Q(date_end__isnull=True)).filter(date_start__lte=date.today())


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
    reason = models.ForeignKey('PriceReason', on_delete=models.CASCADE)
    details = models.TextField(null=True, blank=True)
    update_level = models.SmallIntegerField(choices=UPDATE_LEVEL_CHOICES, default=0)
    objects = CampsiteRateManager()

    def get_rate(self, num_adult=0, num_concession=0, num_child=0, num_infant=0):
        return self.rate.adult * num_adult + self.rate.concession * num_concession + \
            self.rate.child * num_child + self.rate.infant * num_infant

    def __str__(self):
        return '{} - ({})'.format(self.campsite, self.rate)

    class Meta:
        unique_together = (('campsite', 'rate', 'date_start', 'date_end'),)

    # Properties
    # =======createCampsitePriceHistory==========================
    @property
    def deletable(self):
        today = datetime.now().date()
        if self.date_start >= today:
            return True
        return False

    @property
    def editable(self):
        today = datetime.now().date()
        if (self.date_start > today and not self.date_end) or (self.date_start > today <= self.date_end):
            return True
        return False

    # Methods
    # =================================
    def update(self, data):
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
    legacy_name = models.CharField(max_length=255, blank=True, null=True)
    arrival = models.DateField()
    departure = models.DateField()
    details = JSONField(null=True, blank=True)
    booking_type = models.SmallIntegerField(choices=BOOKING_TYPE_CHOICES, default=0)
    expiry_time = models.DateTimeField(blank=True, null=True)
    cost_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    override_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    override_reason = models.ForeignKey('DiscountReason', null=True, blank=True, on_delete=models.CASCADE)
    override_reason_info = models.TextField(blank=True, null=True)
    overridden_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT, blank=True, null=True, related_name='overridden_bookings')
    campground = models.ForeignKey('Campground', null=True, on_delete=models.PROTECT)
    is_canceled = models.BooleanField(default=False)
    send_invoice = models.BooleanField(default=False)
    cancellation_reason = models.TextField(null=True, blank=True)
    cancelation_time = models.DateTimeField(null=True, blank=True)
    confirmation_sent = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    canceled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True, related_name='canceled_bookings')

    # Properties
    # =================================
    @property
    def num_days(self):
        return (self.departure - self.arrival).days

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
        return '{} adult{}, {} concession{}, {} child{}, {} infant{}'.format(
            num_adult, '' if num_adult == 1 else 's',
            num_concession, '' if num_concession == 1 else 's',
            num_child, '' if num_child == 1 else 'ren',
            num_infant, '' if num_infant == 1 else 's',
        )

    @property
    def num_guests(self):
        if self.details:
            num_adult = self.details.get('num_adult', 0)
            num_concession = self.details.get('num_concession', 0)
            num_infant = self.details.get('num_infant', 0)
            num_child = self.details.get('num_child', 0)
            return num_adult + num_concession + num_infant + num_child
        return 0

    @property
    def guests(self):
        if self.details:
            num_adult = self.details.get('num_adult', 0)
            num_concession = self.details.get('num_concession', 0)
            num_infant = self.details.get('num_infant', 0)
            num_child = self.details.get('num_child', 0)
            return {
                "adults": num_adult,
                "concession": num_concession,
                "infants": num_infant,
                "children": num_child
            }
        return {
            "adults": 0,
            "concession": 0,
            "infants": 0,
            "children": 0
        }

    @property
    def first_campsite(self):
        cb = self.campsites.all().first()
        return cb.campsite if cb else None

    @property
    def first_campsite_list(self):
        cbs = self.campsites.distinct('campsite')
        first_campsite_list = []
        for item in cbs:
            first_campsite_list.append(item.campsite)
        return first_campsite_list

    @property
    def discount(self):
        return (self.cost_total - self.override_price)

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
            status = ''
            parts = payment_status.split('_')
            for p in parts:
                status += '{} '.format(p.title())
            status = status.strip()
            if self.is_canceled:
                if payment_status == 'over_paid' or payment_status == 'paid':
                    return 'Canceled - Payment ({})'.format(status)
                else:
                    return 'Canceled'
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
    def clean(self, *args, **kwargs):
        # Check for existing bookings in current date range
        arrival = self.arrival
        departure = self.departure
        customer = self.customer

        other_bookings = Booking.objects.filter(Q(departure__gt=arrival, departure__lte=departure) | Q(arrival__gte=arrival, arrival__lt=departure), customer=customer)
        if self.pk:
            other_bookings.exclude(id=self.pk)
        if customer and other_bookings and self.booking_type != 3:
            raise ValidationError('You cannot make concurrent bookings.')
        if not self.campground.oracle_code:
            raise ValidationError('Campground does not have an Oracle code.')
        if self.campground.park.entry_fee_required and not self.campground.park.oracle_code:
            raise ValidationError('Park does not have an Oracle code.')
        super(Booking, self).clean(*args, **kwargs)

    def __str__(self):
        return '{}: {} - {}'.format(self.customer, self.arrival, self.departure)

    def __check_payment_amount(self):
        amount = D('0.0')

        if self.active_invoice:
            amount = self.active_invoice.payment_amount
        elif self.legacy_id:
            amount = D(self.cost_total)

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
            if self.override_reason and self.override_price == 0:
                return 'paid'
            else:
                return 'unpaid'

        if self.override_price:
            if self.override_price < amount:
                return 'over_paid'
            elif self.override_price > amount:
                return 'partially_paid'
            else:
                return "paid"
        else:
            if self.cost_total < amount:
                return 'over_paid'
            elif self.cost_total > amount:
                return 'partially_paid'
            else:
                return "paid"

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
        else:
            return "Not Refunded"

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

    def cancelBooking(self, reason, user=None):
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

    def _generate_history(self, user=None):
        campsites = list(set([x.campsite.name for x in self.campsites.all()]))
        vehicles = [{'rego': x.rego, 'type': x.type, 'entry_fee': x.entry_fee, 'park_entry_fee': x.park_entry_fee} for x in self.regos.all()]
        BookingHistory.objects.create(
            booking=self,
            updated_by=user,
            arrival=self.arrival,
            departure=self.departure,
            details=self.details,
            cost_total=self.cost_total,
            confirmation_sent=self.confirmation_sent,
            campground=self.campground.name,
            campsites=campsites,
            vehicles=vehicles,
            invoice=self.active_invoice
        )

    @property
    def vehicle_payment_status(self):
        # Get current invoice
        inv = None
        payment_dict = []
        temp_invoices = [self.active_invoice] if self.active_invoice else []

        if len(temp_invoices) == 1 or self.legacy_id:
            if not self.legacy_id:
                inv = temp_invoices[0]
            # Get all lines
            total_paid = D('0.0')
            total_due = D('0.0')
            lines = []
            if not self.legacy_id:
                lines = inv.order.lines.filter(oracle_code=self.campground.park.oracle_code)

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
                    # pass
                    if self.override_reason and self.override_price == 0:
                        paid = True
                    else:
                        paid = False

                if self.override_price:
                    if self.override_price <= total_paid:
                        paid = True
                    else:
                        paid = False

                else:
                    required_total = D('0.0')
                    for k, v in price_dict.items():
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
    booking = models.ForeignKey(Booking,related_name='history', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    arrival = models.DateField()
    departure = models.DateField()
    details = JSONField()
    cost_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    confirmation_sent = models.BooleanField()
    campground = models.CharField(max_length=100)
    campsites = JSONField()
    vehicles = JSONField()
    updated_by = models.ForeignKey(EmailUser, on_delete=models.PROTECT, blank=True, null=True)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.PROTECT)

class OutstandingBookingRecipient(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email


class BookingInvoice(models.Model):
    booking = models.ForeignKey(Booking, related_name='invoices', on_delete=models.PROTECT)
    invoice_reference = models.CharField(max_length=50, null=True, blank=True, default='')

    def __str__(self):
        return 'Booking {} : Invoice #{}'.format(self.id, self.invoice_reference)

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
        ('vehicle', 'Vehicle'),
        ('motorbike', 'Motorcycle'),
        ('concession', 'Vehicle (concession)')
    )
    booking = models.ForeignKey(Booking, related_name = "regos", on_delete=models.CASCADE)
    rego = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=VEHICLE_CHOICES)
    entry_fee = models.BooleanField(default=False)
    park_entry_fee = models.BooleanField(default=False)

    class Meta:
        unique_together = ('booking', 'rego')


class ParkEntryRate(models.Model):

    vehicle = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    concession = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    motorbike = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    period_start = models.DateField()
    period_end = models.DateField(null=True, blank=True)
    reason = models.ForeignKey("PriceReason", on_delete=models.PROTECT)
    details = models.TextField(null=True, blank=True)

    def clean(self, *args, **kwargs):
        if self.reason.id == 1 and not self.details:
            raise ValidationError("Details cannot be empty if reason is Other")
        super(ParkEntryRate, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ParkEntryRate, self).save(*args, **kwargs)

    @property
    def editable(self):
        today = datetime.now().date()
        return (self.period_start > today and not self.period_end) or (self.period_start > today <= self.period_end)


# REASON MODELS
# =====================================
class Reason(models.Model):
    text = models.TextField()
    editable = models.BooleanField(default=True, editable=False)

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
        return '{}{}'.format((val * (4 - length)), self.id)


class MaximumStayReason(Reason):
    pass


class ClosureReason(Reason):
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
    adult = models.DecimalField(max_digits=8, decimal_places=2)
    concession = models.DecimalField(max_digits=8, decimal_places=2)
    child = models.DecimalField(max_digits=8, decimal_places=2)
    details = models.TextField()
    reason_id = models.IntegerField()
    infant = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        abstract = True

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
        if (self.date_start > today and not self.date_end) or (self.date_start > today <= self.date_end):
            return True
        return False

    @property
    def reason(self):
        reason = ''
        if self.reason_id:
            reason = self.reason_id
        return reason


class CampgroundPriceHistory(ViewPriceHistory):
    class Meta:
        managed = False
        db_table = 'parkstay_campground_pricehistory_v'
        ordering = ['-date_start', ]


class CampsiteClassPriceHistory(ViewPriceHistory):
    class Meta:
        managed = False
        db_table = 'parkstay_campsiteclass_pricehistory_v'
        ordering = ['-date_start', ]

# LISTENERS
# ======================================


class CampgroundListener(object):
    """
    Event listener for Campgrounds
    """

    @staticmethod
    @receiver(pre_save, sender=Campground)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Campground.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Campground)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            # Create an opening booking range on creation of Campground
            CampgroundBookingRange.objects.create(campground=instance, range_start=datetime.now().date(), status=0)
        else:
            if original_instance.price_level != instance.price_level:
                # Get all campsites
                today = datetime.now().date()
                campsites = instance.campsites.all()
                campsite_list = campsites.values_list('id', flat=True)
                rates = CampsiteRate.objects.filter(campsite__in=campsite_list, update_level=original_instance.price_level)
                current_rates = rates.filter(Q(date_end__isnull=True), Q(date_start__lte=today))
                current_rates.update(date_end=today)
                future_rates = rates.filter(date_start__gt=today)
                future_rates.delete()

                if instance.price_level == 1:
                    # Check if there are any existant campsite class rates
                    for c in campsites:
                        try:
                            ch = CampsiteClassPriceHistory.objects.get(Q(date_end__isnull=True), id=c.campsite_class_id, date_start__lte=today)
                            cr = CampsiteRate(campsite=c, rate_id=ch.rate_id, date_start=today + timedelta(days=1))
                            cr.save()
                        except CampsiteClassPriceHistory.DoesNotExist:
                            pass
                        except Exception:
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


class CampsiteListener(object):
    """
    Event listener for Campsites
    """

    @staticmethod
    @receiver(pre_save, sender=Campsite)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Campsite.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Campsite)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if not original_instance:
            # Create an opening booking range on creation of Campground
            CampsiteBookingRange.objects.create(campsite=instance, range_start=datetime.now().date(), status=0)


class CampsiteRateListener(object):
    """
    Event listener for Campsite Rate
    """

    @staticmethod
    @receiver(pre_save, sender=CampsiteRate)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = CampsiteRate.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = CampsiteRate.objects.get(Q(campsite=instance.campsite),Q(date_start__lte=instance.date_start), Q(date_end__gte=instance.date_start) | Q(date_end__isnull=True) )

                #Sets the end_date as latest start_date - 1 day
                within.date_end = instance.date_start - timedelta(days=1)
                within.save()
            except CampsiteRate.DoesNotExist:
                pass
            # check if there is a newer record and set the end date as the previous record minus 1 day
            # This condition is triggered when a date is chose before the latest start_date
            x = CampsiteRate.objects.filter(Q(campsite=instance.campsite),Q(date_start__gte=instance.date_start), Q(date_end__gte=instance.date_start) | Q(date_end__isnull=True) ).order_by('-date_start')

            if x:
                x = x[0]
                instance.date_end = x.date_start - timedelta(days=1)

    @staticmethod
    @receiver(pre_delete, sender=CampsiteRate)
    def _pre_delete(sender, instance, **kwargs):
        if not instance.date_end:
            c = CampsiteRate.objects.filter(campsite=instance.campsite).order_by('-date_start').exclude(id=instance.id)
            if c:
                c = c[0]
                c.date_end = None
                c.save()


class CampsiteStayHistoryListener(object):
    """
    Event listener for Campsite Stay History
    """

    @staticmethod
    @receiver(pre_save, sender=CampsiteStayHistory)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = CampsiteStayHistory.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = CampsiteStayHistory.objects.get(Q(campsite=instance.campsite), Q(range_start__lte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True))
                within.range_end = instance.range_start - timedelta(days=1)
                within.save()
            except CampsiteStayHistory.DoesNotExist:
                pass

    @staticmethod
    @receiver(post_delete, sender=CampsiteStayHistory)
    def _post_delete(sender, instance, **kwargs):
        if not instance.range_end:
            CampsiteStayHistory.objects.filter(range_end=instance.range_start - timedelta(days=1), campsite=instance.campsite).update(range_end=None)


class CampgroundStayHistoryListener(object):
    """
    Event listener for Campground Stay History
    """

    @staticmethod
    @receiver(pre_save, sender=CampgroundStayHistory)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = CampgroundStayHistory.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                within = CampgroundStayHistory.objects.get(Q(campground=instance.campground), Q(range_start__lte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True))
                within.range_end = instance.range_start - timedelta(days=2)
                within.save()
            except CampgroundStayHistory.DoesNotExist:
                pass

            # check if there is a newer record and set the end date as the previous record minus 1 day
            x = CampgroundStayHistory.objects.filter(Q(campground=instance.campground), Q(range_start__gte=instance.range_start), Q(range_end__gte=instance.range_start) | Q(range_end__isnull=True)).order_by('range_start')
            if x:
                x = x[0]
                instance.date_end = x.date_start - timedelta(days=2)

    @staticmethod
    @receiver(pre_delete, sender=CampgroundStayHistory)
    def _pre_delete(sender, instance, **kwargs):
        if not instance.range_end:
            c = CampgroundStayHistory.objects.filter(campground=instance.campground).order_by('-range_start').exclude(id=instance.id)
            if c:
                c = c[0]
                c.date_end = None
                c.save()


class ParkEntryRateListener(object):
    """
    Event listener for ParkEntryRate
    """

    @staticmethod
    @receiver(pre_save, sender=ParkEntryRate)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = ParkEntryRate.objects.filter(pk=instance.pk)
            if original_instance.exists():
                setattr(instance, "_original_instance", original_instance.first())
            price_before = ParkEntryRate.objects.filter(period_start__lt=instance.period_start).order_by("-period_start")
            if price_before:
                price_before = price_before[0]

                price_before.period_end = instance.period_start - timedelta(days=1)
                #price_before.period_end = instance.period_start

                instance.period_start = instance.period_start
                #instance.period_start = instance.period_start + timedelta(days=1)

                price_before.save()
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                price_before = ParkEntryRate.objects.filter(period_start__lt=instance.period_start).order_by("-period_start")
                if price_before:
                    price_before = price_before[0]

                    price_before.period_end = instance.period_start - timedelta(days=1)
                    price_before.save()
                    instance.period_start = instance.period_start

                #     price_before.period_end = instance.period_start
                #     price_before.save()
                #     instance.period_start = instance.period_start + timedelta(days=1)
                price_after = ParkEntryRate.objects.filter(period_start__gt=instance.period_start).order_by("period_start")
                if price_after:
                    price_after = price_after[0]
                    instance.period_end = price_after.period_start - timedelta(days=1)
            except Exception as e:
                pass

    @staticmethod
    @receiver(post_delete, sender=ParkEntryRate)
    def _post_delete(sender, instance, **kwargs):
        price_before = ParkEntryRate.objects.filter(period_start__lt=instance.period_start).order_by("-period_start")
        price_after = ParkEntryRate.objects.filter(period_start__gt=instance.period_start).order_by("period_start")
        if price_after:
            price_after = price_after[0]
            if price_before:
                price_before = price_before[0]
                price_before.period_end = price_after.period_start - timedelta(days=1)
                price_before.save()
        elif price_before:
            price_before = price_before[0]
            price_before.period_end = None
            price_before.save()
