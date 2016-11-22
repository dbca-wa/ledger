import traceback
from django.db.models import Q
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from datetime import datetime, timedelta
from collections import OrderedDict

from parkstay.models import (Campground,
                                CampsiteBooking,
                                Campsite,
                                CampsiteRate,
                                Booking,
                                CampgroundBookingRange,
                                CampsiteBookingRange,
                                CampsiteStayHistory,
                                PromoArea,
                                Park,
                                Feature,
                                Region,
                                CampsiteClass,
                                Booking,
                                CampsiteRate
                                )

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
                                    CampgroundBookingRangeSerializer,
                                    CampsiteBookingRangeSerializer,
                                    CampsiteRateSerializer,
                                    CampsiteStayHistorySerializer
                                    )
from parkstay.helpers import is_officer, is_customer




# API Views
class CampsiteBookingViewSet(viewsets.ModelViewSet):
    queryset = CampsiteBooking.objects.all()
    serializer_class = CampsiteBookingSerialiser

class CampsiteViewSet(viewsets.ModelViewSet):
    queryset = Campsite.objects.all()
    serializer_class = CampsiteSerialiser

    @detail_route(methods=['post'],authentication_classes=[])
    def open_close(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            # parse and validate data
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['campsite'] = self.get_object().id
            request.POST._mutable = mutable
            serializer = CampsiteBookingRangeSerializer(data=request.data, method="post")
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data.get('status') == 0:
                self.get_object().open(dict(serializer.validated_data))
            else:
                self.get_object().close(dict(serializer.validated_data))

            # return object
            ground = self.get_object()
            res = CampsiteSerialiser(ground, context={'request':request})

            return Response(res.data)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def status_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            # Check what status is required
            closures = bool(request.GET.get("closures", False))
            if closures:
                serializer = CampsiteBookingRangeSerializer(self.get_object().booking_ranges.filter(~Q(status=0)),many=True)
            else:
                serializer = CampsiteBookingRangeSerializer(self.get_object().booking_ranges,many=True)
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def stay_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            serializer = CampsiteStayHistorySerializer(self.get_object().stay_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

class CampsiteStayHistoryViewSet(viewsets.ModelViewSet):
    queryset = CampsiteStayHistory.objects.all()
    serializer_class = CampsiteStayHistorySerializer
    authentication_classes=[]

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance,data=request.data,partial=partial)
            serializer.is_valid(raise_exception=True)
            if instance.range_end and not serializer.validated_data.get('range_end'):
                instance.range_end = None
            self.perform_update(serializer)

            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

class CampgroundViewSet(viewsets.ModelViewSet):
    queryset = Campground.objects.all()
    serializer_class = CampgroundSerializer
    authentication_classes=[]

    def list(self, request, format=None):
        queryset = self.get_queryset()
        formatted = bool(request.GET.get("formatted", False))
        serializer = self.get_serializer(queryset, formatted=formatted, many=True, method='get')
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        formatted = bool(request.GET.get("formatted", False))
        serializer = self.get_serializer(instance, formatted=formatted, method='get')
        return Response(serializer.data)

    @detail_route(methods=['post'],authentication_classes=[])
    def open_close(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            # parse and validate data
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['campground'] = self.get_object().id
            request.POST._mutable = mutable
            serializer = CampgroundBookingRangeSerializer(data=request.data, method="post")
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data.get('status') == 0:
                self.get_object().open(dict(serializer.validated_data))
            else:
                self.get_object().close(dict(serializer.validated_data))

            # return object
            ground = self.get_object()
            res = CampgroundSerializer(ground, context={'request':request})

            return Response(res.data)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def status_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            # Check what status is required
            closures = bool(request.GET.get("closures", False))
            if closures:
                serializer = CampgroundBookingRangeSerializer(self.get_object().booking_ranges.filter(~Q(status=0)),many=True)
            else:
                serializer = CampgroundBookingRangeSerializer(self.get_object().booking_ranges,many=True)
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def campsites(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            serializer = CampsiteSerialiser(self.get_object().campsites,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

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
        rates_qs = CampsiteRate.objects.filter(campsite__in=sites_qs)

        # make a map of campsite class to cost
        rates_map = {r.campsite.campsite_class_id: r.get_rate(num_adult, num_concession, num_child, num_infant) for r in rates_qs}

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
        rates_qs = CampsiteRate.objects.filter(campsite__in=sites_qs)

        # make a map of campsite class to cost
        rates_map = {r.campsite.campsite_class_id: r.get_rate(num_adult, num_concession, num_child, num_infant) for r in rates_qs}

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
    serializer_class = FeatureSerializer

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

class BookingRangeViewset(viewsets.ModelViewSet):
    authentication_classes=[]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        original = bool(request.GET.get("original", False))
        serializer = self.get_serializer(instance, original=original, method='get')
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance,data=request.data,partial=partial)
            serializer.is_valid(raise_exception=True)
            if instance.range_end and not serializer.validated_data.get('range_end'):
                instance.range_end = None
            self.perform_update(serializer)

            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

class CampgroundBookingRangeViewset(BookingRangeViewset):
    queryset = CampgroundBookingRange.objects.all()
    serializer_class = CampgroundBookingRangeSerializer

class CampsiteBookingRangeViewset(BookingRangeViewset):
    queryset = CampsiteBookingRange.objects.all()
    serializer_class = CampsiteBookingRangeSerializer
