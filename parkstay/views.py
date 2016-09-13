
from django.shortcuts import render
from rest_framework import viewsets
from parkstay.serialisers import CampsiteBookingSerialiser, CampsiteSerialiser
from parkstay.models import CampsiteBooking, Campsite, Booking
from django_ical.views import ICalFeed


class CampgroundFeed(ICalFeed):
    timezone = 'UTC+8'

    def items(self):
#        return CampsiteBooking.objects.filter(campsite__campground__name='Yardie Creek').order_by('-date','campsite__name') 
        return Booking.objects.filter(campground__name='Yardie Creek').order_by('-arrival','campground__name')

    def item_title(self, item):
        return item.legacy_name

    def item_start_datetime(self, item):
        return item.arrival

    def item_end_datetime(self, item):
        return item.departure

    def item_location(self, item):
        return '{} - {}'.format(item.campground.name, ', '.join([
            x[0] for x in item.campsitebooking_set.values_list('campsite__name').distinct()
        ] )) 


# Create your views here.
class CampsiteBookingViewSet(viewsets.ModelViewSet):
    queryset = CampsiteBooking.objects.all()
    serializer_class = CampsiteBookingSerialiser

class CampsiteViewSet(viewsets.ModelViewSet):
    queryset = Campsite.objects.all()
    serializer_class = CampsiteSerialiser
