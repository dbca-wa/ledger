import traceback
import base64
from urlparse import urlparse
from django.db.models import Q
from django.core.files.base import ContentFile
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
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
                                CampsiteRate,
                                Rate,
                                CampgroundPriceHistory,
                                CampsiteClassPriceHistory,
                                ClosureReason,
                                OpenReason,
                                PriceReason,
                                MaximumStayReason
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
                                    CampsiteRateReadonlySerializer,
                                    CampsiteStayHistorySerializer,
                                    RateSerializer,
                                    RateDetailSerializer,
                                    CampgroundPriceHistorySerializer,
                                    CampsiteClassPriceHistorySerializer,
                                    CampgroundImageSerializer,
                                    ExistingCampgroundImageSerializer,
                                    ClosureReasonSerializer,
                                    OpenReasonSerializer,
                                    PriceReasonSerializer,
                                    MaximumStayReasonSerializer,
                                    BulkPricingSerializer
                                    )
from parkstay.helpers import is_officer, is_customer




# API Views
class CampsiteBookingViewSet(viewsets.ModelViewSet):
    queryset = CampsiteBooking.objects.all()
    serializer_class = CampsiteBookingSerialiser


class CampsiteViewSet(viewsets.ModelViewSet):
    queryset = Campsite.objects.all()
    serializer_class = CampsiteSerialiser
    

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

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance,data=request.data,partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            number = request.data.pop('number')
            serializer = self.get_serializer(data=request.data,method='post')
            serializer.is_valid(raise_exception=True)

            if number >  1:
                data = dict(serializer.validated_data)
                campsites = Campsite.bulk_create(number,data)
                res = self.get_serializer(campsites,many=True)
            else:
                if number == 1 and serializer.validated_data['name'] == 'default':
                    latest = 0
                    current_campsites = Campsite.objects.filter(campground=serializer.validated_data.get('campground'))
                    cs_numbers = [int(c.name) for c in current_campsites if c.name.isdigit()]
                    if cs_numbers:
                        latest = max(cs_numbers)
                    if len(str(latest+1)) == 1:
                        name = '0{}'.format(latest+1)
                    else:
                        name = str(latest+1)
                    serializer.validated_data['name'] = name
                instance = serializer.save()
                res = self.get_serializer(instance)

            return Response(res.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'])
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
            serializer = CampsiteStayHistorySerializer(self.get_object().stay_history,many=True,context={'request':request},method='get')
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def price_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            price_history = self.get_object().rates.all()
            serializer = CampsiteRateReadonlySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

class CampsiteStayHistoryViewSet(viewsets.ModelViewSet):
    queryset = CampsiteStayHistory.objects.all()
    serializer_class = CampsiteStayHistorySerializer

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

    def strip_b64_header(self, content):
        if ';base64,' in content:
            header, base64_data = content.split(';base64,')
            return base64_data
        return content

    def create(self, request, format=None):
        try:
            images_data = None
            http_status = status.HTTP_200_OK
            if "images" in request.data:
                images_data = request.data.pop("images")
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance =serializer.save()
            # Get and Validate campground images
            initial_image_serializers = [CampgroundImageSerializer(data=image) for image in images_data] if images_data else []
            image_serializers = []
            if initial_image_serializers:

                for image_serializer in initial_image_serializers:
                    result = urlparse(image_serializer.initial_data['image'])
                    if not (result.scheme =='http' or result.scheme == 'https') and not result.netloc:
                        image_serializers.append(image_serializer)

                if image_serializers:
                    for image_serializer in image_serializers:
                        image_serializer.initial_data["campground"] = instance.id
                        image_serializer.initial_data["image"] = ContentFile(base64.b64decode(self.strip_b64_header(image_serializer.initial_data["image"])))
                        image_serializer.initial_data["image"].name = 'uploaded'

                    for image_serializer in image_serializers:
                        image_serializer.is_valid(raise_exception=True)

                    for image_serializer in image_serializers:
                        image_serializer.save()

            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def update(self, request, *args, **kwargs):
        try:
            images_data = None
            http_status = status.HTTP_200_OK
            instance = self.get_object()
            if "images" in request.data:
                images_data = request.data.pop("images")
            serializer = self.get_serializer(instance,data=request.data,partial=True)
            serializer.is_valid(raise_exception=True)
            # Get and Validate campground images
            initial_image_serializers = [CampgroundImageSerializer(data=image) for image in images_data] if images_data else []
            image_serializers, existing_image_serializers = [],[]
            # Get campgrounds current images
            current_images = instance.images.all()
            if initial_image_serializers:

                for image_serializer in initial_image_serializers:
                    result = urlparse(image_serializer.initial_data['image'])
                    if not (result.scheme =='http' or result.scheme == 'https') and not result.netloc:
                        image_serializers.append(image_serializer)
                    else:
                        data = {
                            'id':image_serializer.initial_data['id'],
                            'image':image_serializer.initial_data['image'],
                            'campground':instance.id
                        }
                        existing_image_serializers.append(ExistingCampgroundImageSerializer(data=data))

                # Dealing with existing images
                images_id_list = []
                for image_serializer in existing_image_serializers:
                    image_serializer.is_valid(raise_exception=True)
                    images_id_list.append(image_serializer.validated_data['id'])

                #Get current object images and check if any has been removed
                for img in current_images:
                    if img.id not in images_id_list:
                        img.delete()

                # Creating new Images
                if image_serializers:
                    for image_serializer in image_serializers:
                        image_serializer.initial_data["campground"] = instance.id
                        image_serializer.initial_data["image"] = ContentFile(base64.b64decode(self.strip_b64_header(image_serializer.initial_data["image"])))
                        image_serializer.initial_data["image"].name = 'uploaded'

                    for image_serializer in image_serializers:
                        image_serializer.is_valid(raise_exception=True)

                    for image_serializer in image_serializers:
                        image_serializer.save()
            else:
                if current_images:
                    current_images.delete()

            self.perform_update(serializer)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'])
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

    @detail_route(methods=['post'],)
    def addPrice(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            rate = None
            serializer = RateDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rate_id = serializer.validated_data.get('rate',None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e :
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'])[0]
            if rate:
                serializer.validated_data['rate']= rate
                data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(serializer.validated_data['reason']),
                    'details': serializer.validated_data['details'],
                    'update_level': 0
                }
                self.get_object().createCampsitePriceHistory(data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'],)
    def updatePrice(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            original_data = request.data.pop('original')
            original_serializer = CampgroundPriceHistorySerializer(data=original_data,method='post')
            original_serializer.is_valid(raise_exception=True)

            serializer = RateDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rate_id = serializer.validated_data.get('rate',None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e :
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'])[0]
            if rate:
                serializer.validated_data['rate']= rate
                new_data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data['details'],
                    'update_level': 0
                }
                self.get_object().updatePriceHistory(dict(original_serializer.validated_data),new_data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'],)
    def deletePrice(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            serializer = CampgroundPriceHistorySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            self.get_object().deletePriceHistory(serializer.validated_data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
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
    def price_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history,many=True,context={'request':request})
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

    def list(self, request, *args, **kwargs):
        active_only = bool(request.GET.get('active_only',False))
        if active_only:
            queryset = CampsiteClass.objects.filter(deleted=False)
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True,method='get')
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,method='get')
        return Response(serializer.data) 
        

    @detail_route(methods=['get'])
    def price_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            price_history = CampsiteClassPriceHistory.objects.filter(id=self.get_object().id)
            # Format list
            open_ranges,formatted_list,fixed_list= [],[],[]
            for p in price_history:
                if p.date_end == None:
                    open_ranges.append(p)
                else:
                    formatted_list.append(p)

            for outer in open_ranges:
                for inner in open_ranges:
                    if inner.date_start > outer.date_start and inner.rate_id == outer.rate_id:
                        open_ranges.remove(inner)

            fixed_list = formatted_list + open_ranges
            fixed_list.sort(key=lambda x: x.date_start)
            serializer = CampsiteClassPriceHistorySerializer(fixed_list,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'],)
    def addPrice(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            rate = None
            serializer = RateDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rate_id = serializer.validated_data.get('rate',None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e :
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'])[0]
            if rate:
                serializer.validated_data['rate']= rate
                data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data['details'],
                    'update_level': 1
                }
                self.get_object().createCampsitePriceHistory(data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'],)
    def updatePrice(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            original_data = request.data.pop('original')

            original_serializer = CampgroundPriceHistorySerializer(data=original_data)
            original_serializer.is_valid(raise_exception=True)

            serializer = RateDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rate_id = serializer.validated_data.get('rate',None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e :
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'])[0]
            if rate:
                serializer.validated_data['rate']= rate
                new_data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data['details'],
                    'update_level': 1
                }
                self.get_object().updatePriceHistory(dict(original_serializer.validated_data),new_data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'],)
    def deletePrice(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            serializer = CampgroundPriceHistorySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            self.get_object().deletePriceHistory(serializer.validated_data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class CampsiteRateViewSet(viewsets.ModelViewSet):
    queryset = CampsiteRate.objects.all()
    serializer_class = CampsiteRateSerializer


    def create(self, request, format=None):
        try:
            http_status = status.HTTP_200_OK
            rate = None
            print(request.data)
            rate_serializer = RateDetailSerializer(data=request.data)
            rate_serializer.is_valid(raise_exception=True)
            rate_id = rate_serializer.validated_data.get('rate',None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e :
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'])[0]
            print(rate_serializer.validated_data)
            if rate:
                data = {
                    'rate': rate.id,
                    'date_start': rate_serializer.validated_data['period_start'],
                    'campsite': rate_serializer.validated_data['campsite'],
                    #'reason': serializer.validated_data['reason'],
                    'update_level': 2
                }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            res = serializer.save()

            serializer = CampsiteRateReadonlySerializer(res)
            return Response(serializer.data, status=http_status)

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def update(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            rate = None
            rate_serializer = RateDetailSerializer(data=request.data)
            rate_serializer.is_valid(raise_exception=True)
            rate_id = rate_serializer.validated_data.get('rate',None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e :
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'])[0]
            if rate:
                data = {
                    'rate': rate.id,
                    'date_start': rate_serializer.validated_data['period_start'],
                    'campsite': rate_serializer.validated_data['campsite'],
                    #'reason': serializer.validated_data['reason'],
                    'update_level': 2
                }
            instance = self.get_object()
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance,data=data,partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data, status=http_status)

        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

class BookingRangeViewset(viewsets.ModelViewSet):

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

class RateViewset(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

# Reasons
# =========================
class ClosureReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClosureReason.objects.all()
    serializer_class = ClosureReasonSerializer

class OpenReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OpenReason.objects.all()
    serializer_class = OpenReasonSerializer

class PriceReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceReason.objects.all()
    serializer_class = PriceReasonSerializer

class MaximumStayReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaximumStayReason.objects.all()
    serializer_class = MaximumStayReasonSerializer

# Bulk Pricing
# ===========================
class BulkPricingView(generics.CreateAPIView):
    serializer_class = BulkPricingSerializer
    renderer_classes = (JSONRenderer,)

    def create(self, request,*args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            print serializer.validated_data

            rate_id = serializer.data.get('rate',None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e :
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'])[0]
            if rate:
                data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.data['reason']),
                    'details': serializer.validated_data['details']
                }
            if serializer.data['type'] == 'Park':
                for c in serializer.data['campgrounds']:
                    data['update_level'] = 0
                    Campground.objects.get(pk=c).createCampsitePriceHistory(data)

            return Response(serializer.data, status=http_status)

        except serializers.ValidationError:
            print traceback.print_exc()
            raise
        except Exception as e:
            print traceback.print_exc()
            raise serializers.ValidationError(str(e))
