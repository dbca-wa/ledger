from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.

class Park(models.Model):
    name = models.CharField(max_length=255)
    district = models.ForeignKey('District', null=True, on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)
    
    def __str__(self):
        return '{} - {}'.format(self.name, self.district)

    class Meta:
        unique_together = (('name',),)


class PromoArea(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Campground(models.Model):
    CAMPGROUND_TYPE_CHOICES = (
        (0, 'Campground: no bookings'),
        (1, 'Campground: book online'),
        (2, 'Campground: book by phone'),
        (3, 'Other accomodation')
    )

    SITE_TYPE_CHOICES = (
        (0, 'Unnumbered Site'),
        (1, 'Numbered site')
    )

    name = models.CharField(max_length=255, null=True)
    park = models.ForeignKey('Park', on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)
    campground_type = models.SmallIntegerField(choices=CAMPGROUND_TYPE_CHOICES, default=0)
    promo_area = models.ForeignKey('PromoArea', on_delete=models.PROTECT, null=True)
    site_type = models.SmallIntegerField(choices=SITE_TYPE_CHOICES, default=0)
    address = JSONField(null=True)
    features = models.ManyToManyField('CampgroundFeature')
    description = models.TextField(blank=True, null=True)
    rules = models.TextField(blank=True, null=True)
    area_activities = models.TextField(blank=True, null=True)
    driving_directions = models.TextField(blank=True, null=True)
    fees = models.TextField(blank=True, null=True)
    othertransport = models.TextField(blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    is_published = models.BooleanField(default=False)
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    metakeywords = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'park'),)
    

class Campsite(models.Model):
    campground = models.ForeignKey('Campground', db_index=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    campsite_class = models.ForeignKey('CampsiteClass', on_delete=models.PROTECT)
    max_people = models.SmallIntegerField(default=6)
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    min_days = models.SmallIntegerField(default=1)
    max_days = models.SmallIntegerField(default=28)

    def __str__(self):
        return '{} - {}'.format(self.campground, self.name)

    class Meta:
        unique_together = (('campground', 'name'),)


class CampgroundFeature(models.Model):
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
    tents = models.SmallIntegerField(default=0)
    parking_spaces = models.SmallIntegerField(default=0)
    min_people = models.SmallIntegerField(default=1)
    max_people = models.SmallIntegerField(default=12)
    allow_campervan = models.BooleanField(default=False)
    allow_trailer = models.BooleanField(default=False)
    allow_generator = models.BooleanField(default=False)

    def __str__(self):
        return self.name


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
    rate_adult = models.DecimalField(max_digits=8, decimal_places=2, default='10.00')
    rate_concession = models.DecimalField(max_digits=8, decimal_places=2, default='6.60')
    rate_child = models.DecimalField(max_digits=8, decimal_places=2, default='2.20')
    rate_infant = models.DecimalField(max_digits=8, decimal_places=2, default='0')
    
    def __str__(self):
        return 'adult: ${}, concession: ${}, child: ${}, infant: ${}'.format(self.rate_adult, self.rate_concession, self.rate_child, self.rate_infant)


class CampsiteRate(models.Model):
    RATE_TYPE_CHOICES = (
        (0, 'Standard'),
        (1, 'Discounted'),
    )

    PRICE_MODEL_CHOICES = (
        (0, 'Price per Person'),
        (1, 'Fixed Price'),
    )
    campsite = models.ForeignKey('Campsite', on_delete=models.PROTECT)
    rate = models.ForeignKey('Rate', on_delete=models.PROTECT)
    allow_public_holidays = models.BooleanField(default=True)
    date_start = models.DateField()
    date_end = models.DateField()
    rate_type = models.SmallIntegerField(choices=RATE_TYPE_CHOICES, default=0)
    price_model = models.SmallIntegerField(choices=PRICE_MODEL_CHOICES, default=0)
   
    def get_rate(self, num_adult=0, num_concession=0, num_child=0, num_infant=0):
        return self.rate.rate_adult*num_adult + self.rate.rate_concession*num_concession + \
                self.rate.rate_child*num_child + self.rate.rate_infant*num_infant

    def __str__(self):
        return '{} - ({})'.format(self.campsite, self.rate)

    class Meta:
        unique_together = (('campsite', 'rate'))


class Booking(models.Model):
    legacy_id = models.IntegerField(unique=True)
    legacy_name = models.CharField(max_length=255, blank=True)
    arrival = models.DateField()
    departure = models.DateField()
    details = JSONField(null=True)
    cost_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    campsite_rate = models.ForeignKey(CampsiteRate, db_index=True, on_delete=models.PROTECT)
    campground = models.ForeignKey('Campground', null=True)
