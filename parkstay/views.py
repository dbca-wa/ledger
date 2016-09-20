
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateView
from django.conf import settings

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
    """Fetch campsite availability for a campground."""
    # FIXME: port this junk to rest_framework

    # convert GET parameters to objects
    ground = Campground.objects.get(pk=request.GET['ground_id'])
    start_date = datetime.strptime(request.GET['arrival'], '%Y/%m/%d').date()
    end_date = datetime.strptime(request.GET['departure'], '%Y/%m/%d').date()
    
    # get a length of the stay (in days), capped if necessary to the request maximum
    length = max(0, (end_date-start_date).days)
    if length > settings.PS_MAX_BOOKING_LENGTH:
        length = settings.PS_MAX_BOOKING_LENGTH
        end_date = start_date+timedelta(days=settings.PS_MAX_BOOKING_LENGTH)
    
    # fetch all of the single-day CampsiteBooking objects within the date range for the campground
    bookings_qs =   CampsiteBooking.objects.filter(
                        campsite__campground=ground, 
                        date__gte=start_date, 
                        date__lt=end_date
                    ).order_by('date', 'campsite__name')
    # fetch all the campsites and applicable rates for the campground
    sites_qs = Campsite.objects.filter(campground=ground).order_by('name')
    rates_qs = CampsiteRate.objects.filter(campground=ground)

    # make a map of campsite class to cost
    rates_map = {r.campsite_class_id: r.cost_per_day for r in rates_qs}

    # from our campsite queryset, generate a digest for each site
    sites_map = OrderedDict([(s.name, (s.pk, s.campsite_class, rates_map[s.campsite_class_id])) for s in sites_qs])
    bookings_map = {}

    # create our result object, which will be returned as JSON
    result = {
        'arrival': start_date.strftime('%Y/%m/%d'),
        'days': length,
        'adults': 1,
        'children': 0,
        'maxAdults': 30,
        'maxChildren': 30,
        'sites': [],
        'classes': {}
    }

    # make an entry under sites for each site
    for k, v in sites_map.items():
        site = {
            'name': k,
            'id': v[0],
            'type': ground.campground_type,
            'class': v[1].pk,
            'price': '${}'.format(v[2]*length),
            'availability': [[True, '${}'.format(v[2]), v[2]] for i in range(length)]
        }
        result['sites'].append(site)
        bookings_map[k] = site
        if v[1].pk not in result['classes']:
            result['classes'][v[1].pk] = v[1].name
    
    # strike out existing bookings
    for b in bookings_qs:
        offset = (b.date-start_date).days
        bookings_map[b.campsite.name]['availability'][offset][0] = False
        bookings_map[b.campsite.name]['availability'][offset][1] = 'Closed' if b.booking_type == 2 else 'Sold'
        bookings_map[b.campsite.name]['price'] = False

    return JsonResponse(result)


def get_campsite_class_bookings(request):
    """Fetch campsite availability for a campground, grouped by campsite class."""
    # FIXME: port this junk to rest_framework maybe?

    # convert GET parameters to objects
    ground = Campground.objects.get(pk=request.GET['ground_id'])
    start_date = datetime.strptime(request.GET['arrival'], '%Y/%m/%d').date()
    end_date = datetime.strptime(request.GET['departure'], '%Y/%m/%d').date()
    
    # get a length of the stay (in days), capped if necessary to the request maximum
    length = max(0, (end_date-start_date).days)
    if length > settings.PS_MAX_BOOKING_LENGTH:
        length = settings.PS_MAX_BOOKING_LENGTH
        end_date = start_date+timedelta(days=settings.PS_MAX_BOOKING_LENGTH)
    
    # fetch all of the single-day CampsiteBooking objects within the date range for the campground
    bookings_qs =   CampsiteBooking.objects.filter(
                        campsite__campground=ground, 
                        date__gte=start_date, 
                        date__lt=end_date
                    ).order_by('date', 'campsite__name')
    # fetch all the campsites and applicable rates for the campground
    sites_qs = Campsite.objects.filter(campground=ground)
    rates_qs = CampsiteRate.objects.filter(campground=ground)

    # make a map of campsite class to cost
    rates_map = {r.campsite_class_id: r.cost_per_day for r in rates_qs}
    
    # from our campsite queryset, generate a distinct list of campsite classes
    classes = [x for x in sites_qs.distinct('campsite_class__name').order_by('campsite_class__name').values_list('pk', 'campsite_class', 'campsite_class__name')]
    
    classes_map = {}
    bookings_map = {}

    # create our result object, which will be returned as JSON
    result = {
        'arrival': start_date.strftime('%Y/%m/%d'),
        'days': length,
        'adults': 1,
        'children': 0,
        'maxAdults': 30,
        'maxChildren': 30,
        'sites': [],
        'classes': {}
    }

    # make an entry under sites for each campsite class
    for c in classes:
        rate = rates_map[c[1]]
        site = {
            'name': c[2],
            'id': None,
            'type': ground.campground_type,
            'price': '{}'.format(rate*length),
            'availability': [[True, '${}'.format(rate), rate, [0, 0]] for i in range(length)],
            'breakdown': OrderedDict()
        }
        result['sites'].append(site)
        classes_map[c[1]] = site

    # make a map of class IDs to site IDs
    class_sites_map = {}
    for s in sites_qs:
        if s.campsite_class.pk not in class_sites_map:
            class_sites_map[s.campsite_class.pk] = set()

        class_sites_map[s.campsite_class.pk].add(s.pk)
        rate = rates_map[s.campsite_class.pk]
        classes_map[s.campsite_class.pk]['breakdown'][s.pk] = [[True, '${}'.format(rate), rate] for i in range(length)]

    # store number of campsites in each class
    class_sizes = {k: len(v) for k, v in class_sites_map.items()}

    

    # strike out existing bookings
    for b in bookings_qs:
        offset = (b.date-start_date).days
        key = b.campsite.campsite_class.pk

        # clear the campsite from the class sites map
        if b.campsite.pk in class_sites_map[key]:
            class_sites_map[key].remove(b.campsite.pk)

        classes_map[key]['breakdown'][b.campsite.pk][offset][0] = False
        classes_map[key]['breakdown'][b.campsite.pk][offset][1] = 'Closed' if (b.booking_type == 2) else 'Sold'

        # update the availability status based on 
        book_offset = 1 if (b.booking_type == 2) else 0
        classes_map[key]['availability'][offset][3][book_offset] += 1
        if classes_map[key]['availability'][offset][3][0] == class_sizes[key]:
            classes_map[key]['availability'][offset][1] = 'Fully Booked'
        elif classes_map[key]['availability'][offset][3][1] == class_sizes[key]:
            classes_map[key]['availability'][offset][1] = 'Closed'
        elif classes_map[key]['availability'][offset][3][0] > classes_map[key]['availability'][offset][3][1]:
            classes_map[key]['availability'][offset][1] = 'Partially Booked'
        else:
            classes_map[key]['availability'][offset][1] = 'Partially Closed'
        
        # tentatively flag campsite class as unavailable
        classes_map[key]['availability'][offset][0] = False
        classes_map[key]['price'] = False

    for k, v in classes_map.items():
        v['breakdown'] = [x for x in v['breakdown'].values()]

    # for each class, any campsites remaining in the class sites map have zero bookings!
    # pick one of those and return that as the target
    for k, v in class_sites_map.items():
        if v:
            rate = rates_map[k]
            classes_map[k].update({
                'id': v.pop(),
                'price': '{}'.format(rate*length),
                'availability': [[True, '${}'.format(rate), rate, [0, 0]] for i in range(length)],
                'breakdown': []
            })


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
