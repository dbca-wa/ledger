
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateView
from django.conf import settings

from parkstay.serialisers import (  CampsiteBookingSerialiser,
                                    CampsiteSerialiser,
                                    CampgroundSerializer,
                                    CampgroundCampsiteFilterSerializer,
                                    PromoAreaSerializer,
                                    ParkSerializer,
                                    FeatureSerializer,
                                    RegionSerializer,
                                    CampsiteClassSerializer,
                                    BookingSerializer,
                                    CampsiteRateSerializer
                                    )
from parkstay.models import (Campground,
                                CampsiteBooking,
                                Campsite,
                                CampsiteRate,
                                Booking,
                                PromoArea,
                                Park,
                                Feature,
                                Region,
                                CampsiteClass,
                                Booking,
                                CampsiteRate
                                )
from django_ical.views import ICalFeed
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from datetime import datetime, timedelta
from collections import OrderedDict

class CampsiteBookingSelector(TemplateView):
    template_name = 'ps/campsite_booking_selector.html'

    def get(self, request, *args, **kwargs):
        return super(CampsiteBookingSelector, self).get(request, *args, **kwargs)

class CampgroundFeed(ICalFeed):
    timezone = 'UTC+8'

    def get_object(self, request, ground_id):
        # FIXME: add authentication parameter check
        return Campground.objects.get(pk=ground_id)

    def title(self, obj):
        return 'Bookings for {}'.format(obj.name)

    def items(self, obj):
#        return CampsiteBooking.objects.filter(campsite__campground__name='Yardie Creek').order_by('-date','campsite__name')
        now = datetime.utcnow()
        low_bound = now - timedelta(days=60)
        up_bound = now + timedelta(days=90)
        return Booking.objects.filter(campground=obj, arrival__gte=low_bound, departure__lt=up_bound).order_by('-arrival','campground__name')

    def item_link(self, item):
        return 'http://www.geocities.com/replacethiswithalinktotheadmin'

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

class CampgroundViewSet(viewsets.ModelViewSet):
    queryset = Campground.objects.all()
    serializer_class = CampgroundSerializer

    @detail_route(methods=['get']) 
    def campsite_bookings(self, request, pk=None, format=None):
        """Fetch campsite availability for a campground."""
        # convert GET parameters to objects
        ground = self.get_object()
        # Validate parameters
        data = {
            "arrival" : request.GET.get('arrival'),
            "departure" : request.GET.get('departure'),
            "num_adult" : request.GET.get('num_adult', 0),
            "num_concession" : request.GET.get('num_concession', 0),
            "num_child" : request.GET.get('num_child', 0),
            "num_infant" : request.GET.get('num_infant', 0)
        }
        serializer = CampgroundCampsiteFilterSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data['arrival']
        end_date = serializer.validated_data['departure']
        num_adult = serializer.validated_data['num_adult']
        num_concession = serializer.validated_data['num_concession']
        num_child = serializer.validated_data['num_child']
        num_infant = serializer.validated_data['num_infant']
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
        rates_qs = CampsiteRate.objects.filter(sites_qs)

        # make a map of campsite class to cost
        rates_map = {r.campsite_class_id: r.rate(num_adult, num_concession, num_child, num_infant) for r in rates_qs}

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

        return Response(result)

    @detail_route(methods=['get'])
    def campsite_class_bookings(self, request, pk=None, format=None):
        """Fetch campsite availability for a campground, grouped by campsite class."""
        # convert GET parameters to objects
        ground = self.get_object() 
        # Validate parameters
        data = {
            "arrival" : request.GET.get('arrival'),
            "departure" : request.GET.get('departure'),
            "num_adult" : request.GET.get('num_adult', 0),
            "num_concession" : request.GET.get('num_concession', 0),
            "num_child" : request.GET.get('num_child', 0),
            "num_infant" : request.GET.get('num_infant', 0)
        }
        serializer = CampgroundCampsiteFilterSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data['arrival']
        end_date = serializer.validated_data['departure']
        num_adult = serializer.validated_data['num_adult']
        num_concession = serializer.validated_data['num_concession']
        num_child = serializer.validated_data['num_child']
        num_infant = serializer.validated_data['num_infant']

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
        rates_map = {r.campsite_class_id: r.rate(num_adult, num_concession, num_child, num_infant) for r in rates_qs}
        
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
                'price': '${}'.format(rate*length),
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
            classes_map[s.campsite_class.pk]['breakdown'][s.name] = [[True, '${}'.format(rate), rate] for i in range(length)]

        # store number of campsites in each class
        class_sizes = {k: len(v) for k, v in class_sites_map.items()}

        

        # strike out existing bookings
        for b in bookings_qs:
            offset = (b.date-start_date).days
            key = b.campsite.campsite_class.pk

            # clear the campsite from the class sites map
            if b.campsite.pk in class_sites_map[key]:
                class_sites_map[key].remove(b.campsite.pk)

            # update the per-site availability
            classes_map[key]['breakdown'][b.campsite.name][offset][0] = False
            classes_map[key]['breakdown'][b.campsite.name][offset][1] = 'Closed' if (b.booking_type == 2) else 'Sold'

            # update the class availability status
            book_offset = 1 if (b.booking_type == 2) else 0
            classes_map[key]['availability'][offset][3][book_offset] += 1
            if classes_map[key]['availability'][offset][3][0] == class_sizes[key]:
                classes_map[key]['availability'][offset][1] = 'Fully Booked'
            elif classes_map[key]['availability'][offset][3][1] == class_sizes[key]:
                classes_map[key]['availability'][offset][1] = 'Closed'
            elif classes_map[key]['availability'][offset][3][0] >= classes_map[key]['availability'][offset][3][1]:
                classes_map[key]['availability'][offset][1] = 'Partially Booked'
            else:
                classes_map[key]['availability'][offset][1] = 'Partially Closed'
            
            # tentatively flag campsite class as unavailable
            classes_map[key]['availability'][offset][0] = False
            classes_map[key]['price'] = False

        # convert breakdowns to a flat list
        for klass in classes_map.values():
            klass['breakdown'] = [{'name': k, 'availability': v} for k, v in klass['breakdown'].items()]

        # any campsites remaining in the class sites map have zero bookings!
        # check if there's any left for each class, and if so return that as the target
        for k, v in class_sites_map.items():
            if v:
                rate = rates_map[k]
                classes_map[k].update({
                    'id': v.pop(),
                    'price': '${}'.format(rate*length),
                    'availability': [[True, '${}'.format(rate), rate, [0, 0]] for i in range(length)],
                    'breakdown': []
                })


        return Response(result)

class PromoAreaViewSet(viewsets.ModelViewSet):
    queryset = PromoArea.objects.all()
    serializer_class = PromoAreaSerializer

class ParkViewSet(viewsets.ModelViewSet):
    queryset = Park.objects.all()
    serializer_class = ParkSerializer

class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = CampgroundSerializer

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class CampsiteClassViewSet(viewsets.ModelViewSet):
    queryset = CampsiteClass.objects.all()
    serializer_class = CampsiteClassSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class CampsiteRateViewSet(viewsets.ModelViewSet):
    queryset = CampsiteRate.objects.all()
    serializer_class = CampsiteRateSerializer


class DashboardView(TemplateView):
    template_name = 'ps/dash/dash_tables_campgrounds.html'
