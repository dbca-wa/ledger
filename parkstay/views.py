
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateView

from parkstay.serialisers import CampsiteBookingSerialiser, CampsiteSerialiser
from parkstay.models import Campground, CampsiteBooking, Campsite, CampsiteRate, Booking

from django_ical.views import ICalFeed
from rest_framework import viewsets
from datetime import datetime, timedelta
from collections import OrderedDict

class CampsiteBookingSelector(TemplateView):
    template_name = 'ps/campsite_booking_selector.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

def get_campsite_bookings(request):
    # FIXME: port this junk to rest_framework

    ground = Campground.objects.get(pk=request.GET['ground_id'])
    start_date = datetime.strptime(request.GET['arrival'], '%Y/%m/%d').date()
    end_date = datetime.strptime(request.GET['departure'], '%Y/%m/%d').date()
    length = max(0, (end_date-start_date).days)
    
    bookings_qs =   CampsiteBooking.objects.filter(
                        campsite__campground=ground, 
                        date__gte=start_date, 
                        date__lt=end_date
                    ).order_by('date', 'campsite__name')
    sites_qs = Campsite.objects.filter(campground=ground).order_by('name')
    rates_qs = CampsiteRate.objects.filter(campground=ground)

    rates_map = {r.campsite_class_id: r.cost_per_day for r in rates_qs}
    sites_map = OrderedDict([(s.name, rates_map[s.campsite_class_id]) for s in sites_qs])
    bookings_map = {}

    result = {
        'arrival': start_date,
        'days': length,
        'adults': 1,
        'children': 0,
        'maxAdults': 30,
        'maxChildren': 30,
        'sites': []
    }
    for k, v in sites_map.items():
        site = {
            'name': k,
            'type': ground.campground_type,
            'price': '${}'.format(v*length),
            'availability': [[True, '${}'.format(v), v] for i in range(length)]
        }
        result['sites'].append(site)
        bookings_map[k] = site
    
    # strike out existing bookings
    for b in bookings_qs:
        offset = (b.date-start_date).days
        bookings_map[b.campsite.name]['availability'][offset][0] = False
        bookings_map[b.campsite.name]['availability'][offset][1] = 'Closed' if b.booking_type == 2 else 'Sold'
        bookings_map[b.campsite.name]['price'] = False

    return JsonResponse(result)


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
