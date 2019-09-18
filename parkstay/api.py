import traceback
import base64
import geojson
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from django.db import connection, transaction
from django.db.models import Q, Min
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta, date
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from ledger.payments.models import Invoice
from parkstay import utils
from parkstay.helpers import can_view_campground
from parkstay.models import (Campground,
                             District,
                             Contact,
                             CampsiteBooking,
                             Campsite,
                             CampsiteClass,
                             CampsiteRate,
                             Booking,
                             CampgroundBookingRange,
                             CampsiteBookingRange,
                             CampsiteStayHistory,
                             CampgroundStayHistory,
                             PromoArea,
                             Park,
                             Feature,
                             Region,
                             Rate,
                             CampgroundPriceHistory,
                             CampsiteClassPriceHistory,
                             ClosureReason,
                             PriceReason,
                             MaximumStayReason,
                             DiscountReason,
                             ParkEntryRate,
                             )

from parkstay.serialisers import (CampsiteBookingSerialiser,
                                  CampsiteSerialiser,
                                  ContactSerializer,
                                  DistrictSerializer,
                                  CampgroundMapSerializer,
                                  CampgroundMapFilterSerializer,
                                  CampgroundSerializer,
                                  CampgroundDatatableSerializer,
                                  CampgroundCampsiteFilterSerializer,
                                  CampsiteBookingSerializer,
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
                                  CampgroundStayHistorySerializer,
                                  RateSerializer,
                                  RateDetailSerializer,
                                  CampgroundPriceHistorySerializer,
                                  CampsiteClassPriceHistorySerializer,
                                  CampgroundImageSerializer,
                                  ExistingCampgroundImageSerializer,
                                  ClosureReasonSerializer,
                                  PriceReasonSerializer,
                                  MaximumStayReasonSerializer,
                                  DiscountReasonSerializer,
                                  BulkPricingSerializer,
                                  UsersSerializer,
                                  ParkEntryRateSerializer,
                                  ReportSerializer,
                                  BookingSettlementReportSerializer,
                                  CountrySerializer,
                                  UserSerializer,
                                  UserAddressSerializer,
                                  ContactSerializer as UserContactSerializer,
                                  PersonalSerializer,
                                  PhoneSerializer,
                                  OracleSerializer,
                                  BookingHistorySerializer
                                  )
from parkstay.helpers import is_officer
from parkstay import reports
from parkstay import pdf
from parkstay.perms import PaymentCallbackPermission
from parkstay import emails


# API Views
class CampsiteBookingViewSet(viewsets.ModelViewSet):
    queryset = CampsiteBooking.objects.all()
    serializer_class = CampsiteBookingSerialiser


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


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
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            number = request.data.pop('number')
            serializer = self.get_serializer(data=request.data, method='post')
            serializer.is_valid(raise_exception=True)

            if number > 1:
                data = dict(serializer.validated_data)
                campsites = Campsite.bulk_create(number, data)
                res = self.get_serializer(campsites, many=True)
            else:
                if number == 1 and serializer.validated_data['name'] == 'default':
                    latest = 0
                    current_campsites = Campsite.objects.filter(campground=serializer.validated_data.get('campground'))
                    cs_numbers = [int(c.name) for c in current_campsites if c.name.isdigit()]
                    if cs_numbers:
                        latest = max(cs_numbers)
                    if len(str(latest + 1)) == 1:
                        name = '0{}'.format(latest + 1)
                    else:
                        name = str(latest + 1)
                    serializer.validated_data['name'] = name
                instance = serializer.save()
                res = self.get_serializer(instance)

            return Response(res.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def close_campsites(self, closure_data, campsites):
        for campsite in campsites:
            closure_data['campsite'] = campsite
            try:
                serializer = CampsiteBookingRangeSerializer(data=closure_data, method='post')
                serializer.is_valid(raise_exception=True)
                instance = Campsite.objects.get(pk=campsite)
                instance.close(dict(serializer.validated_data))
            except Exception as e:
                raise

    @list_route(methods=['post'])
    def bulk_close(self, request, format='json', pk=None):
        with transaction.atomic():
            try:
                http_status = status.HTTP_200_OK
                closure_data = request.data.copy()
                campsites = closure_data.pop('campsites[]')
                self.close_campsites(closure_data, campsites)
                return Response('All selected campsites closed')
            except serializers.ValidationError:
                print(traceback.print_exc())
                raise serializers.ValidationError(str(e[0]))
            except Exception as e:
                print(traceback.print_exc())
                raise serializers.ValidationError(str(e[0]))

    @detail_route(methods=['get'])
    def status_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            # Check what status is required
            closures = bool(request.GET.get("closures", False))
            if closures:
                serializer = CampsiteBookingRangeSerializer(self.get_object().booking_ranges.filter(~Q(status=0)).order_by('-range_start'), many=True)
            else:
                serializer = CampsiteBookingRangeSerializer(self.get_object().booking_ranges, many=True)
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def stay_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            serializer = CampsiteStayHistorySerializer(self.get_object().stay_history, many=True, context={'request': request}, method='get')
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def price_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            price_history = self.get_object().rates.all().order_by('-date_start')
            serializer = CampsiteRateReadonlySerializer(price_history, many=True, context={'request': request})
            res = serializer.data
            return Response(res, status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def current_price(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            start_date = request.GET.get('arrival', False)
            end_date = request.GET.get('departure', False)
            res = []
            if start_date and end_date:
                res = utils.get_campsite_current_rate(request, self.get_object().id, start_date, end_date)
            else:
                res.append({
                    "error": "Arrival and departure dates are required",
                    "success": False
                })

            return Response(res, status=http_status)
        except serializers.ValidationError:
            traceback.print_exc()
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @csrf_exempt
    @list_route(methods=['post'])
    def current_price_list(self, request, format='json', pk=None):
        with transaction.atomic():
            try:
                http_status = status.HTTP_200_OK
                rate_data = request.data.copy()
                campsites = rate_data.pop('campsites')
                start_date = rate_data.pop('arrival')
                end_date = rate_data.pop('departure')
                res = utils.get_campsites_current_rate(self.request, campsites, start_date, end_date)

                return Response(res, status=http_status)
            except serializers.ValidationError:
                print(traceback.print_exc())
                raise serializers.ValidationError(str(e[0]))
            except Exception as e:
                print(traceback.print_exc())
                raise serializers.ValidationError(str(e[0]))


class CampsiteStayHistoryViewSet(viewsets.ModelViewSet):
    queryset = CampsiteStayHistory.objects.all()
    serializer_class = CampsiteStayHistorySerializer

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            if instance.range_end and not serializer.validated_data.get('range_end'):
                instance.range_end = None
            self.perform_update(serializer)

            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))


class CampgroundStayHistoryViewSet(viewsets.ModelViewSet):
    queryset = CampgroundStayHistory.objects.all()
    serializer_class = CampgroundStayHistorySerializer

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            if instance.range_end and not serializer.validated_data.get('range_end'):
                instance.range_end = None
            self.perform_update(serializer)

            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))


class CampgroundMapViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Campground.objects.exclude(campground_type=3).annotate(Min('campsites__rates__rate__adult'))
    serializer_class = CampgroundMapSerializer
    permission_classes = []


class CampgroundMapFilterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Campground.objects.exclude(campground_type=3)
    serializer_class = CampgroundMapFilterSerializer
    permission_classes = []

    def list(self, request, *args, **kwargs):
        data = {
            "arrival": request.GET.get('arrival', None),
            "departure": request.GET.get('departure', None),
            "num_adult": request.GET.get('num_adult', 0),
            "num_concession": request.GET.get('num_concession', 0),
            "num_child": request.GET.get('num_child', 0),
            "num_infant": request.GET.get('num_infant', 0),
            "gear_type": request.GET.get('gear_type', 'all')
        }

        serializer = CampgroundCampsiteFilterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        scrubbed = serializer.validated_data
        context = {}
        # filter to the campsites by gear allowed (if specified), else show the lot
        if scrubbed['gear_type'] != 'all':
            context = {scrubbed['gear_type']: True}

        # if a date range is set, filter out campgrounds that are unavailable for the whole stretch
        if scrubbed['arrival'] and scrubbed['departure'] and (scrubbed['arrival'] < scrubbed['departure']):
            sites = Campsite.objects.filter(**context)
            ground_ids = utils.get_open_campgrounds(sites, scrubbed['arrival'], scrubbed['departure'])

        else:  # show all of the campgrounds with campsites
            ground_ids = set((x[0] for x in Campsite.objects.filter(**context).values_list('campground')))

            # we need to be tricky here. for the default search (all, no timestamps),
            # we want to include all of the "campgrounds" that don't have any campsites in the model! (e.g. third party)
            if scrubbed['gear_type'] == 'all':
                ground_ids.update((x[0] for x in Campground.objects.filter(campsites__isnull=True).values_list('id')))

        # Filter out for the max period
        today = date.today()
        if scrubbed['arrival']:
            start_date = scrubbed['arrival']
        else:
            start_date = today
        if scrubbed['departure']:
            end_date = scrubbed['departure']
        else:
            end_date = today + timedelta(days=1)

        temp_queryset = Campground.objects.filter(id__in=ground_ids).order_by('name')
        queryset = []
        for q in temp_queryset:
            # Get the current stay history
            stay_history = CampgroundStayHistory.objects.filter(
                Q(range_start__lte=start_date, range_end__gte=start_date) |  # filter start date is within period
                Q(range_start__lte=end_date, range_end__gte=end_date) |  # filter end date is within period
                Q(Q(range_start__gt=start_date, range_end__lt=end_date) & Q(range_end__gt=today)),  # filter start date is before and end date after period
                campground=q
            )
            if stay_history:
                max_days = min([x.max_days for x in stay_history])
            else:
                max_days = settings.PS_MAX_BOOKING_LENGTH
            if (end_date - start_date).days <= max_days:
                queryset.append(q)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@require_http_methods(['GET'])
def search_suggest(request, *args, **kwargs):
    entries = []
    for x in Campground.objects.filter(wkb_geometry__isnull=False).values_list('id', 'name', 'wkb_geometry'):
        entries.append(geojson.Point((x[2].x, x[2].y), properties={'type': 'Campground', 'id': x[0], 'name': x[1]}))
    for x in Park.objects.filter(wkb_geometry__isnull=False).values_list('id', 'name', 'wkb_geometry'):
        entries.append(geojson.Point((x[2].x, x[2].y), properties={'type': 'Park', 'id': x[0], 'name': x[1]}))
    for x in PromoArea.objects.filter(wkb_geometry__isnull=False).values_list('id', 'name', 'wkb_geometry'):
        entries.append(geojson.Point((x[2].x, x[2].y), properties={'type': 'PromoArea', 'id': x[0], 'name': x[1]}))

    return HttpResponse(geojson.dumps(geojson.FeatureCollection(entries)), content_type='application/json')


class CampgroundViewSet(viewsets.ModelViewSet):
    queryset = Campground.objects.all()
    serializer_class = CampgroundSerializer

    @list_route(methods=['GET', ])
    @renderer_classes((JSONRenderer,))
    def datatable_list(self, request, format=None):
        queryset = cache.get('campgrounds_dt')
        if queryset is None:
            queryset = self.get_queryset()
            cache.set('campgrounds_dt', queryset, 3600)
        qs = [c for c in queryset.all() if can_view_campground(request.user, c)]
        serializer = CampgroundDatatableSerializer(qs, many=True)
        data = serializer.data
        return Response(data)

    @renderer_classes((JSONRenderer,))
    def list(self, request, format=None):

        queryset = cache.get('campgrounds')
        formatted = bool(request.GET.get("formatted", False))
        if queryset is None:
            queryset = self.get_queryset()
            cache.set('campgrounds', queryset, 3600)
        qs = [c for c in queryset.all() if can_view_campground(request.user, c)]
        serializer = self.get_serializer(qs, formatted=formatted, many=True, method='get')
        data = serializer.data
        return Response(data)

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
            instance = serializer.save()
            # Get and Validate campground images
            initial_image_serializers = [CampgroundImageSerializer(data=image) for image in images_data] if images_data else []
            image_serializers = []
            if initial_image_serializers:

                for image_serializer in initial_image_serializers:
                    result = urlparse(image_serializer.initial_data['image'])
                    if not (result.scheme == 'http' or result.scheme == 'https') and not result.netloc:
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
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            # Get and Validate campground images
            initial_image_serializers = [CampgroundImageSerializer(data=image) for image in images_data] if images_data else []
            image_serializers, existing_image_serializers = [], []
            # Get campgrounds current images
            current_images = instance.images.all()
            if initial_image_serializers:

                for image_serializer in initial_image_serializers:
                    result = urlparse(image_serializer.initial_data['image'])
                    if not (result.scheme == 'http' or result.scheme == 'https') and not result.netloc:
                        image_serializers.append(image_serializer)
                    else:
                        data = {
                            'id': image_serializer.initial_data['id'],
                            'image': image_serializer.initial_data['image'],
                            'campground': instance.id
                        }
                        existing_image_serializers.append(ExistingCampgroundImageSerializer(data=data))

                # Dealing with existing images
                images_id_list = []
                for image_serializer in existing_image_serializers:
                    image_serializer.is_valid(raise_exception=True)
                    images_id_list.append(image_serializer.validated_data['id'])

                # Get current object images and check if any has been removed
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
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def close_campgrounds(self, closure_data, campgrounds):
        for campground in campgrounds:
            closure_data['campground'] = campground
            try:
                serializer = CampgroundBookingRangeSerializer(data=closure_data, method="post")
                serializer.is_valid(raise_exception=True)
                instance = Campground.objects.get(pk=campground)
                instance.close(dict(serializer.validated_data))
            except Exception as e:
                raise

    @list_route(methods=['post'])
    def bulk_close(self, request, format='json', pk=None):
        with transaction.atomic():
            try:
                http_status = status.HTTP_200_OK
                closure_data = request.data.copy()
                campgrounds = closure_data.pop('campgrounds[]')
                self.close_campgrounds(closure_data, campgrounds)
                cache.delete('campgrounds_dt')
                return Response('All Selected Campgrounds Closed')
            except serializers.ValidationError:
                print(traceback.print_exc())
                raise serializers.ValidationError(str(e[0]))
            except Exception as e:
                print(traceback.print_exc())
                raise serializers.ValidationError(str(e[0]))

    @detail_route(methods=['post'],)
    def addPrice(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            rate = None
            serializer = RateDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rate_id = serializer.validated_data.get('rate', None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e:
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'], concession=serializer.validated_data['concession'], child=serializer.validated_data['child'], infant=serializer.validated_data['infant'])[0]
            if rate:
                serializer.validated_data['rate'] = rate
                data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data.get('details', None),
                    'update_level': 0
                }
                self.get_object().createCampsitePriceHistory(data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history, many=True, context={'request': request})
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            print(traceback.format_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.format_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'],)
    def updatePrice(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            original_data = request.data.pop('original')
            original_serializer = CampgroundPriceHistorySerializer(data=original_data, method='post')
            original_serializer.is_valid(raise_exception=True)

            serializer = RateDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rate_id = serializer.validated_data.get('rate', None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e:
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'], concession=serializer.validated_data['concession'], child=serializer.validated_data['child'], infant=serializer.validated_data['infant'])[0]
            if rate:
                serializer.validated_data['rate'] = rate
                new_data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data.get('details', None),
                    'update_level': 0
                }
                self.get_object().updatePriceHistory(dict(original_serializer.validated_data), new_data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history, many=True, context={'request': request})
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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
            serializer = CampgroundPriceHistorySerializer(price_history, many=True, context={'request': request})
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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
                serializer = CampgroundBookingRangeSerializer(self.get_object().booking_ranges.filter(~Q(status=0)).order_by('-range_start'), many=True)
            else:
                serializer = CampgroundBookingRangeSerializer(self.get_object().booking_ranges, many=True)
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def campsites(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            serializer = CampsiteSerialiser(self.get_object().campsites, many=True, context={'request': request, 'status': None})
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def price_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id).order_by('-date_start')
            serializer = CampgroundPriceHistorySerializer(price_history, many=True, context={'request': request})
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def stay_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            start = request.GET.get("start", False)
            end = request.GET.get("end", False)
            serializer = None
            if (start) or (end):
                start = datetime.strptime(start, "%Y-%m-%d").date()
                end = datetime.strptime(end, "%Y-%m-%d").date()
                queryset = CampgroundStayHistory.objects.filter(range_end__range=(start, end), range_start__range=(start, end)).order_by("range_start")[:5]
                serializer = CampgroundStayHistorySerializer(queryset, many=True, context={'request': request}, method='get')
            else:
                serializer = CampgroundStayHistorySerializer(self.get_object().stay_history.all().order_by('-range_start'), many=True, context={'request': request}, method='get')
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def try_parsing_date(self, text):
        for fmt in ('%Y/%m/%d', '%d/%m/%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise serializers.ValidationError('no valid date format found')

    @detail_route(methods=['get'])
    def available_campsites(self, request, format='json', pk=None):
        try:
            start_date = self.try_parsing_date(request.GET.get('arrival')).date()
            end_date = self.try_parsing_date(request.GET.get('departure')).date()
            campsite_qs = Campsite.objects.filter(campground_id=self.get_object().id)
            http_status = status.HTTP_200_OK
            available = utils.get_available_campsites_list(campsite_qs, request, start_date, end_date)

            return Response(available, status=http_status)
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def available_campsites_booking(self, request, format='json', pk=None):
        try:
            start_date = self.try_parsing_date(request.GET.get('arrival')).date()
            end_date = self.try_parsing_date(request.GET.get('departure')).date()
            booking_id = request.GET.get('booking', None)
            if not booking_id:
                raise serializers.ValidationError('Booking has not been defined')
            try:
                booking = Booking.objects.get(id=booking_id)
            except BaseException:
                raise serializers.ValiadationError('The booking could not be retrieved')
            campsite_qs = Campsite.objects.filter(campground_id=self.get_object().id)
            http_status = status.HTTP_200_OK
            available = utils.get_available_campsites_list_booking(campsite_qs, request, start_date, end_date, booking)

            return Response(available, status=http_status)
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def available_campsite_classes(self, request, format='json', pk=None):
        try:
            start_date = datetime.strptime(request.GET.get('arrival'), '%Y/%m/%d').date()
            end_date = datetime.strptime(request.GET.get('departure'), '%Y/%m/%d').date()
            http_status = status.HTTP_200_OK
            available = utils.get_available_campsitetypes(self.get_object().id, start_date, end_date, _list=False)
            available_serializers = []
            for k, v in available.items():
                s = CampsiteClassSerializer(CampsiteClass.objects.get(id=k), context={'request': request}, method='get').data
                s['campsites'] = [c_id for c_id, stat in v.items() if stat != 'closed & booked' and stat != 'booked' and stat != 'closed']
                counts = {'open': 0, 'closed': 0, 'booked': 0, 'closed & booked': 0}
                for c_id, stat in v.items():
                    counts[stat] += 1
                s['status'] = ', '.join(['{} {}'.format(stat, type) for type, stat in counts.items() if stat])
                available_serializers.append(s)
            available_serializers.sort(key=lambda x: x['name'])
            data = available_serializers

            return Response(data, status=http_status)
        except serializers.ValidationError:
            traceback.print_exc()
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))


class BaseAvailabilityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Campground.objects.all()
    serializer_class = CampgroundSerializer

    def retrieve(self, request, pk=None, ratis_id=None, format=None, show_all=False):
        """Fetch full campsite availability for a campground."""
        # convert GET parameters to objects
        ground = self.get_object()
        # check if the user has an ongoing booking
        ongoing_booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
        # Validate parameters
        data = {
            "arrival": request.GET.get('arrival'),
            "departure": request.GET.get('departure'),
            "num_adult": request.GET.get('num_adult', 0),
            "num_concession": request.GET.get('num_concession', 0),
            "num_child": request.GET.get('num_child', 0),
            "num_infant": request.GET.get('num_infant', 0),
            "gear_type": request.GET.get('gear_type', 'all')
        }
        serializer = CampgroundCampsiteFilterSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data['arrival']
        end_date = serializer.validated_data['departure']
        num_adult = serializer.validated_data['num_adult']
        num_concession = serializer.validated_data['num_concession']
        num_child = serializer.validated_data['num_child']
        num_infant = serializer.validated_data['num_infant']
        gear_type = serializer.validated_data['gear_type']

        # if campground doesn't support online bookings, abort!
        if ground.campground_type != 0:
            return Response({'error': 'Campground doesn\'t support online bookings'}, status=400)

        # get a length of the stay (in days), capped if necessary to the request maximum
        length = max(0, (end_date - start_date).days)

        # fetch all the campsites and applicable rates for the campground
        context = {}
        if gear_type != 'all':
            context[gear_type] = True
        sites_qs = Campsite.objects.filter(campground=ground).filter(**context)

        # fetch rate map
        rates = {
            siteid: {
                date: num_adult * info['adult'] + num_concession * info['concession'] + num_child * info['child'] + num_infant * info['infant']
                for date, info in dates.items()
            } for siteid, dates in utils.get_visit_rates(sites_qs, start_date, end_date).items()
        }

        # fetch availability map
        availability = utils.get_campsite_availability(sites_qs, start_date, end_date)

        # create our result object, which will be returned as JSON
        result = {
            'id': ground.id,
            'name': ground.name,
            'long_description': ground.long_description,
            'map': ground.campground_map.url if ground.campground_map else None,
            'ongoing_booking': True if ongoing_booking else False,
            'ongoing_booking_id': ongoing_booking.id if ongoing_booking else None,
            'arrival': start_date.strftime('%Y/%m/%d'),
            'days': length,
            'adults': 1,
            'children': 0,
            'maxAdults': 30,
            'maxChildren': 30,
            'sites': [],
            'classes': {},
        }

        # group results by campsite class
        if ground.site_type in (1, 2):
            # from our campsite queryset, generate a distinct list of campsite classes
            classes = [x for x in sites_qs.distinct('campsite_class__name').order_by('campsite_class__name').values_list('pk', 'campsite_class', 'campsite_class__name', 'tent', 'campervan', 'caravan')]
            classes_map = {}
            bookings_map = {}

            # create a rough mapping of rates to campsite classes
            # (it doesn't matter if this isn't a perfect match, the correct
            # pricing will show up on the booking page)
            rates_map = {}

            class_sites_map = {}
            for s in sites_qs:
                if s.campsite_class.pk not in class_sites_map:
                    class_sites_map[s.campsite_class.pk] = set()
                    rates_map[s.campsite_class.pk] = rates[s.pk]

                class_sites_map[s.campsite_class.pk].add(s.pk)

            # make an entry under sites for each campsite class
            for c in classes:
                rate = rates_map[c[1]]
                site = {
                    'name': c[2],
                    'id': None,
                    'type': c[1],
                    'price': '${}'.format(sum(rate.values())) if not show_all else False,
                    'availability': [[True, '${}'.format(rate[start_date + timedelta(days=i)]), rate[start_date + timedelta(days=i)], None, [0, 0, 0]] for i in range(length)],
                    'breakdown': OrderedDict(),
                    'gearType': {
                        'tent': c[3],
                        'campervan': c[4],
                        'caravan': c[5]
                    }
                }
                result['sites'].append(site)
                classes_map[c[1]] = site

            # make a map of class IDs to site IDs
            for s in sites_qs:
                rate = rates_map[s.campsite_class.pk]
                classes_map[s.campsite_class.pk]['breakdown'][s.name] = [[True, '${}'.format(rate[start_date + timedelta(days=i)]), rate[start_date + timedelta(days=i)], None] for i in range(length)]
            # store number of campsites in each class
            class_sizes = {k: len(v) for k, v in class_sites_map.items()}

            # update results based on availability map
            for s in sites_qs:
                # get campsite class key
                key = s.campsite_class.pk
                # if there's not a free run of slots
                if (not all([v[0] == 'open' for k, v in availability[s.pk].items()])) or show_all:
                    # clear the campsite from the campsite class map
                    if s.pk in class_sites_map[key]:
                        class_sites_map[key].remove(s.pk)

                    # update the days that are non-open
                    for offset, stat, closure_reason in [((k - start_date).days, v[0], v[1]) for k, v in availability[s.pk].items() if v[0] != 'open']:
                        # update the per-site availability
                        classes_map[key]['breakdown'][s.name][offset][0] = False
                        classes_map[key]['breakdown'][s.name][offset][1] = stat if show_all else 'Unavailable'
                        classes_map[key]['breakdown'][s.name][offset][3] = closure_reason if show_all else None

                        # update the class availability status
                        if stat == 'booked':
                            book_offset = 0
                        elif stat == 'closed':
                            book_offset = 1
                        else:
                            book_offset = 2

                        classes_map[key]['availability'][offset][4][book_offset] += 1
                        # if the number of booked entries equals the size of the class, it's fully booked
                        if classes_map[key]['availability'][offset][4][0] == class_sizes[key]:
                            classes_map[key]['availability'][offset][1] = 'Booked'
                        # if the number of closed entries equals the size of the class, it's closed (admin) or unavailable (user)
                        elif classes_map[key]['availability'][offset][4][1] == class_sizes[key]:
                            classes_map[key]['availability'][offset][1] = 'Closed' if show_all else 'Unavailable'
                            classes_map[key]['availability'][offset][3] = closure_reason if show_all else None
                        elif classes_map[key]['availability'][offset][4][2] == class_sizes[key]:
                            classes_map[key]['availability'][offset][1] = 'Closures/Bookings' if show_all else 'Unavailable'
                            classes_map[key]['availability'][offset][3] = closure_reason if show_all else None
                        # if all of the entries are closed, it's unavailable (user)
                        elif not show_all and (classes_map[key]['availability'][offset][4][0] + classes_map[key]['availability'][offset][4][1] == class_sizes[key]):
                            classes_map[key]['availability'][offset][1] = 'Unavailable'
                        # for admin view, we show some text even if there are slots available.
                        elif show_all:
                            # check if there are any booked or closed entries and change the message accordingly
                            test_bk = classes_map[key]['availability'][offset][4][0] > 0
                            test_cl = classes_map[key]['availability'][offset][4][1] > 0
                            test_clbk = classes_map[key]['availability'][offset][4][2] > 0
                            if test_clbk or (test_bk and test_cl):
                                classes_map[key]['availability'][offset][1] = 'Closures/Bookings'
                                if classes_map[key]['availability'][offset][3] is None:
                                    classes_map[key]['availability'][offset][3] = closure_reason
                            elif test_bk:
                                classes_map[key]['availability'][offset][1] = 'Some Booked'
                            elif test_cl:
                                classes_map[key]['availability'][offset][1] = 'Some Closed'
                                if classes_map[key]['availability'][offset][3] is None:
                                    classes_map[key]['availability'][offset][3] = closure_reason
                            elif test_clbk:
                                classes_map[key]['availability'][offset][1] = 'Closures/Bookings'
                                if classes_map[key]['availability'][offset][3] is None:
                                    classes_map[key]['availability'][offset][3] = closure_reason

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
                    # if the number of sites is less than the warning limit, add a notification
                    if len(v) <= settings.PS_CAMPSITE_COUNT_WARNING:
                        classes_map[k].update({
                            'warning': 'Only {} left!'.format(len(v))
                        })

                    classes_map[k].update({
                        'id': v.pop(),
                        'price': '${}'.format(sum(rate.values())),
                        'availability': [[True, '${}'.format(rate[start_date + timedelta(days=i)]), rate[start_date + timedelta(days=i)], [0, 0]] for i in range(length)],
                        'breakdown': []
                    })

            return Response(result)

        # don't group by class, list individual sites
        else:
            sites_qs = sites_qs.order_by('name')

            # from our campsite queryset, generate a digest for each site
            sites_map = OrderedDict([(s.name, (s.pk, s.campsite_class, rates[s.pk], s.tent, s.campervan, s.caravan)) for s in sites_qs])
            bookings_map = {}

            # make an entry under sites for each site
            for k, v in sites_map.items():
                site = {
                    'name': k,
                    'id': v[0],
                    'type': ground.campground_type,
                    'class': v[1].pk,
                    'price': '${}'.format(sum(v[2].values())) if not show_all else False,
                    'availability': [[True, '${}'.format(v[2][start_date + timedelta(days=i)]), v[2][start_date + timedelta(days=i)], None] for i in range(length)],
                    'gearType': {
                        'tent': v[3],
                        'campervan': v[4],
                        'caravan': v[5]
                    }
                }
                result['sites'].append(site)
                bookings_map[k] = site
                if v[1].pk not in result['classes']:
                    result['classes'][v[1].pk] = v[1].name

            # update results based on availability map
            for s in sites_qs:
                # if there's not a free run of slots
                if (not all([v[0] == 'open' for k, v in availability[s.pk].items()])) or show_all:
                    # update the days that are non-open
                    for offset, stat, closure_reason in [((k - start_date).days, v[0], v[1]) for k, v in availability[s.pk].items() if v[0] != 'open']:
                        bookings_map[s.name]['availability'][offset][0] = False
                        if stat == 'closed':
                            bookings_map[s.name]['availability'][offset][1] = 'Closed' if show_all else 'Unavailable'
                            bookings_map[s.name]['availability'][offset][3] = closure_reason if show_all else None
                        elif stat == 'closed & booked':
                            bookings_map[s.name]['availability'][offset][1] = 'Closed & Booked' if show_all else 'Unavailable'
                            bookings_map[s.name]['availability'][offset][3] = closure_reason if show_all else None
                        elif stat == 'booked':
                            bookings_map[s.name]['availability'][offset][1] = 'Booked' if show_all else 'Unavailable'
                        else:
                            bookings_map[s.name]['availability'][offset][1] = 'Unavailable'

                        bookings_map[s.name]['price'] = False

            return Response(result)


class AvailabilityViewSet(BaseAvailabilityViewSet):
    permission_classes = []


class AvailabilityRatisViewSet(BaseAvailabilityViewSet):
    permission_classes = []
    lookup_field = 'ratis_id'


class AvailabilityAdminViewSet(BaseAvailabilityViewSet):
    def retrieve(self, request, *args, **kwargs):
        return super(AvailabilityAdminViewSet, self).retrieve(request, *args, show_all=True, **kwargs)


@csrf_exempt
@require_http_methods(['POST'])
def create_booking(request, *args, **kwargs):
    """Create a temporary booking and link it to the current session"""
    data = {
        'arrival': request.POST.get('arrival'),
        'departure': request.POST.get('departure'),
        'num_adult': request.POST.get('num_adult', 0),
        'num_concession': request.POST.get('num_concession', 0),
        'num_child': request.POST.get('num_child', 0),
        'num_infant': request.POST.get('num_infant', 0),
        'campground': request.POST.get('campground', 0),
        'campsite_class': request.POST.get('campsite_class', 0),
        'campsite': request.POST.get('campsite', 0)
    }

    serializer = CampsiteBookingSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    campground = serializer.validated_data['campground']
    campsite_class = serializer.validated_data['campsite_class']
    campsite = serializer.validated_data['campsite']
    start_date = serializer.validated_data['arrival']
    end_date = serializer.validated_data['departure']
    num_adult = serializer.validated_data['num_adult']
    num_concession = serializer.validated_data['num_concession']
    num_child = serializer.validated_data['num_child']
    num_infant = serializer.validated_data['num_infant']

    if 'ps_booking' in request.session:
        # if there's already a booking in the current session, send bounce signal
        messages.success(request, 'Booking already in progress, complete this first!')
        return HttpResponse(geojson.dumps({
            'status': 'success',
            'msg': 'Booking already in progress.',
            'pk': request.session['ps_booking']
        }), content_type='application/json')

    # for a manually-specified campsite, do a sanity check
    # ensure that the campground supports per-site bookings and bomb out if it doesn't
    if campsite:
        campsite_obj = Campsite.objects.prefetch_related('campground').get(pk=campsite)
        if campsite_obj.campground.site_type != 0:
            return HttpResponse(geojson.dumps({
                'status': 'error',
                'msg': 'Campground doesn\'t support per-site bookings.'
            }), status=400, content_type='application/json')
    # for the rest, check that both campsite_class and campground are provided
    elif (not campsite_class) or (not campground):
        return HttpResponse(geojson.dumps({
            'status': 'error',
            'msg': 'Must specify campsite_class and campground.'
        }), status=400, content_type='application/json')

    # try to create a temporary booking
    try:
        if campsite:
            booking = utils.create_booking_by_site(
                Campsite.objects.filter(id=campsite), start_date, end_date,
                num_adult, num_concession,
                num_child, num_infant
            )
        else:
            booking = utils.create_booking_by_class(
                campground, campsite_class,
                start_date, end_date,
                num_adult, num_concession,
                num_child, num_infant
            )
    except ValidationError as e:
        if hasattr(e, 'error_dict'):
            error = repr(e.error_dict)
        else:
            error = {'error': str(e)}
        return HttpResponse(geojson.dumps({
            'status': 'error',
            'msg': error,
        }), status=400, content_type='application/json')

    # add the booking to the current session
    request.session['ps_booking'] = booking.pk

    return HttpResponse(geojson.dumps({
        'status': 'success',
        'pk': booking.pk
    }), content_type='application/json')


@require_http_methods(['GET'])
def get_confirmation(request, *args, **kwargs):
    # fetch booking for ID
    booking_id = kwargs.get('booking_id', None)
    if (booking_id is None):
        return HttpResponse('Booking ID not specified', status=400)

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return HttpResponse('Booking unavailable', status=403)

    # check permissions
    if not ((request.user == booking.customer) or is_officer(request.user) or (booking.id == request.session.get('ps_last_booking', None))):
        return HttpResponse('Booking unavailable', status=403)

    # check payment status
    if (not is_officer(request.user)) and (not booking.paid):
        return HttpResponse('Booking unavailable', status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="confirmation-PS{}.pdf"'.format(booking_id)

    pdf.create_confirmation(response, booking)

    return response


class PromoAreaViewSet(viewsets.ModelViewSet):
    queryset = PromoArea.objects.all()
    serializer_class = PromoAreaSerializer


class ParkViewSet(viewsets.ModelViewSet):
    queryset = Park.objects.all()
    serializer_class = ParkSerializer

    def list(self, request, *args, **kwargs):
        data = cache.get('parks')
        if data is None:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set('parks', data, 3600)
        return Response(data)

    @list_route(methods=['get'])
    def price_history(self, request, format='json', pk=None):
        http_status = status.HTTP_200_OK
        try:
            price_history = ParkEntryRate.objects.all().order_by('-period_start')
            serializer = ParkEntryRateSerializer(price_history, many=True, context={'request': request}, method='get')
            res = serializer.data
        except Exception as e:
            res = {
                "Error": str(e)
            }

        return Response(res, status=http_status)

    @detail_route(methods=['get'])
    def current_price(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            start_date = request.GET.get('arrival', False)
            res = []
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                price_history = ParkEntryRate.objects.filter(period_start__lte=start_date).order_by('-period_start')
                if price_history:
                    serializer = ParkEntryRateSerializer(price_history, many=True, context={'request': request})
                    res = serializer.data[0]

        except Exception as e:
            res = {
                "Error": str(e)
            }
        return Response(res, status=http_status)

    @list_route(methods=['post'],)
    def add_price(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            serializer = ParkEntryRateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = serializer.data
            return Response(res, status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))


class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer


class ParkEntryRateViewSet(viewsets.ModelViewSet):
    queryset = ParkEntryRate.objects.all()
    serializer_class = ParkEntryRateSerializer


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class CampsiteClassViewSet(viewsets.ModelViewSet):
    queryset = CampsiteClass.objects.all()
    serializer_class = CampsiteClassSerializer

    def list(self, request, *args, **kwargs):
        active_only = bool(request.GET.get('active_only', False))
        if active_only:
            queryset = CampsiteClass.objects.filter(deleted=False)
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, method='get')
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, method='get')
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def price_history(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            price_history = CampsiteClassPriceHistory.objects.filter(id=self.get_object().id).order_by('-date_start')
            # Format list
            open_ranges, formatted_list, fixed_list = [], [], []
            for p in price_history:
                if p.date_end is None:
                    open_ranges.append(p)
                else:
                    formatted_list.append(p)

            for outer in open_ranges:
                for inner in open_ranges:
                    if inner.date_start > outer.date_start and inner.rate_id == outer.rate_id:
                        open_ranges.remove(inner)

            fixed_list = formatted_list + open_ranges
            fixed_list.sort(key=lambda x: x.date_start)
            serializer = CampsiteClassPriceHistorySerializer(fixed_list, many=True, context={'request': request})
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'],)
    def addPrice(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            rate = None
            serializer = RateDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rate_id = serializer.validated_data.get('rate', None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e:
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'], concession=serializer.validated_data['concession'], child=serializer.validated_data['child'], infant=serializer.validated_data['infant'])[0]
            if rate:
                serializer.validated_data['rate'] = rate
                data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data.get('details', None),
                    'update_level': 1
                }
                self.get_object().createCampsitePriceHistory(data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history, many=True, context={'request': request})
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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
            rate_id = serializer.validated_data.get('rate', None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e:
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'], concession=serializer.validated_data['concession'], child=serializer.validated_data['child'], infant=serializer.validated_data['infant'])[0]
            if rate:
                serializer.validated_data['rate'] = rate
                new_data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data.get('details', None),
                    'update_level': 1
                }
                self.get_object().updatePriceHistory(dict(original_serializer.validated_data), new_data)
            price_history = CampgroundPriceHistory.objects.filter(id=self.get_object().id)
            serializer = CampgroundPriceHistorySerializer(price_history, many=True, context={'request': request})
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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
            serializer = CampgroundPriceHistorySerializer(price_history, many=True, context={'request': request})
            res = serializer.data

            return Response(res, status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def list(self, request, *args, **kwargs):
        try:
            search = request.GET.get('search[value]')
            draw = request.GET.get('draw') if request.GET.get('draw') else 1
            start = request.GET.get('start') if request.GET.get('draw') else 0
            length = request.GET.get('length') if request.GET.get('draw') else 'all'
            arrival = str(datetime.strptime(request.GET.get('arrival'), '%d/%m/%Y')) if request.GET.get('arrival') else ''
            departure = str(datetime.strptime(request.GET.get('departure'), '%d/%m/%Y')) if request.GET.get('departure') else ''
            campground = request.GET.get('campground')
            region = request.GET.get('region')
            canceled = request.GET.get('canceled', None)
            refund_status = request.GET.get('refund_status', None)
            if canceled:
                canceled = True if canceled.lower() in ['yes', 'true', 't', '1'] else False

            canceled = 't' if canceled else 'f'

            sql = ''
            http_status = status.HTTP_200_OK
            sqlSelect = 'select distinct parkstay_booking.id as id,parkstay_booking.created,parkstay_booking.customer_id, parkstay_campground.name as campground_name,parkstay_region.name as campground_region,parkstay_booking.legacy_name,\
                parkstay_booking.legacy_id,parkstay_campground.site_type as campground_site_type,\
                parkstay_booking.arrival as arrival, parkstay_booking.departure as departure,parkstay_campground.id as campground_id,coalesce(accounts_emailuser.first_name || \' \' || accounts_emailuser.last_name) as full_name'
            sqlCount = 'select count(distinct parkstay_booking.id)'

            sqlFrom = ' from parkstay_booking\
                join parkstay_campground on parkstay_campground.id = parkstay_booking.campground_id\
                join parkstay_park on parkstay_campground.park_id = parkstay_park.id\
                join parkstay_district on parkstay_park.district_id = parkstay_district.id\
                full outer join accounts_emailuser on parkstay_booking.customer_id = accounts_emailuser.id\
                join parkstay_region on parkstay_district.region_id = parkstay_region.id\
                left outer join parkstay_campgroundgroup_campgrounds cg on cg.campground_id = parkstay_booking.campground_id\
                full outer join parkstay_campgroundgroup_members cm on cm.campgroundgroup_id = cg.campgroundgroup_id'

            sql = sqlSelect + sqlFrom + " where "
            sqlCount = sqlCount + sqlFrom + " where "
            sqlParams = {}

            # Filter the camgrounds that the current user is allowed to view
            sqlFilterUser = ' cm.emailuser_id = %(user)s'
            sql += sqlFilterUser
            sqlCount += sqlFilterUser
            sqlParams['user'] = request.user.id

            if campground:
                sqlCampground = ' parkstay_campground.id = %(campground)s'
                sql = sql + " and " + sqlCampground
                sqlCount = sqlCount + " and " + sqlCampground
                sqlParams['campground'] = campground
            if region:
                sqlRegion = " parkstay_region.id = %(region)s"
                sql = sql + " and " + sqlRegion
                sqlCount = sqlCount + " and " + sqlRegion
                sqlParams['region'] = region
            if arrival:
                sqlArrival = ' parkstay_booking.departure > %(arrival)s'
                sqlCount = sqlCount + " and " + sqlArrival
                sql = sql + " and " + sqlArrival
                sqlParams['arrival'] = arrival
            if departure:
                sqlDeparture = ' parkstay_booking.arrival <= %(departure)s'
                sqlCount = sqlCount + ' and ' + sqlDeparture
                sql = sql + ' and ' + sqlDeparture
                sqlParams['departure'] = departure
            # Search for cancelled bookings
            sql += ' and parkstay_booking.is_canceled = %(canceled)s'
            sqlCount += ' and parkstay_booking.is_canceled = %(canceled)s'
            sqlParams['canceled'] = canceled
            # Remove temporary bookings
            sql += ' and parkstay_booking.booking_type <> 3'
            sqlCount += ' and parkstay_booking.booking_type <> 3'
            if search:
                sqlsearch = ' lower(parkstay_campground.name) LIKE lower(%(wildSearch)s)\
                or lower(parkstay_region.name) LIKE lower(%(wildSearch)s)\
                or lower(parkstay_booking.details->>\'first_name\') LIKE lower(%(wildSearch)s)\
                or lower(parkstay_booking.details->>\'last_name\') LIKE lower(%(wildSearch)s)\
                or lower(parkstay_booking.legacy_name) LIKE lower(%(wildSearch)s)\
                or lower(parkstay_booking.legacy_name) LIKE lower(%(wildSearch)s)'
                sqlParams['wildSearch'] = '%{}%'.format(search)
                if search.isdigit:
                    sqlsearch += ' or CAST (parkstay_booking.id as TEXT) like %(upperSearch)s'
                    sqlParams['upperSearch'] = '{}%'.format(search)

                sql += " and ( " + sqlsearch + " )"
                sqlCount += " and  ( " + sqlsearch + " )"

            sql += ' ORDER BY parkstay_booking.arrival DESC'

            if length != 'all':
                sql = sql + ' limit %(length)s offset %(start)s'
                sqlParams['length'] = length
                sqlParams['start'] = start

            if length == 'all':
                sql = sql + ' limit %(length)s offset %(start)s'
                sqlParams['length'] = 2000
                sqlParams['start'] = start

            sql += ';'

            cursor = connection.cursor()
            cursor.execute("Select count(*) from parkstay_booking ")
            recordsTotal = cursor.fetchone()[0]
            cursor.execute(sqlCount, sqlParams)
            recordsFiltered = cursor.fetchone()[0]

            cursor.execute(sql, sqlParams)
            columns = [col[0] for col in cursor.description]
            data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
            bookings_qs = Booking.objects.filter(id__in=[b['id'] for b in data]).prefetch_related('campground', 'campsites', 'campsites__campsite', 'customer', 'regos', 'history', 'invoices', 'canceled_by')
            booking_map = {b.id: b for b in bookings_qs}
            clean_data = []
            for bk in data:
                cg = None
                booking = booking_map[bk['id']]
                cg = booking.campground
                bk['editable'] = booking.editable
                bk['status'] = booking.status
                bk['booking_type'] = booking.booking_type
                bk['has_history'] = booking.has_history
                bk['cost_total'] = booking.cost_total
                bk['amount_paid'] = booking.amount_paid
                bk['vehicle_payment_status'] = booking.vehicle_payment_status
                bk['refund_status'] = booking.refund_status
                bk['is_canceled'] = 'Yes' if booking.is_canceled else 'No'
                bk['cancelation_reason'] = booking.cancellation_reason
                bk['canceled_by'] = booking.canceled_by.get_full_name() if booking.canceled_by else ''
                bk['cancelation_time'] = booking.cancelation_time if booking.cancelation_time else ''
                bk['paid'] = booking.paid
                bk['invoices'] = [i.invoice_reference for i in booking.invoices.all()]
                bk['active_invoices'] = [i.invoice_reference for i in booking.invoices.all() if i.active]
                bk['guests'] = booking.guests
                bk['campsite_names'] = booking.campsite_name_list
                bk['regos'] = [{r.type: r.rego} for r in booking.regos.all()]
                bk['firstname'] = booking.details.get('first_name', '')
                bk['lastname'] = booking.details.get('last_name', '')
                if booking.override_reason:
                    bk['override_reason'] = booking.override_reason.text
                if booking.override_reason_info:
                    bk['override_reason_info'] = booking.override_reason_info
                if booking.send_invoice:
                    bk['send_invoice'] = booking.send_invoice
                if booking.override_price:
                    bk['discount'] = booking.discount
                if not booking.paid:
                    bk['payment_callback_url'] = '/api/booking/{}/payment_callback.json'.format(booking.id)
                if booking.customer:
                    bk['email'] = booking.customer.email if booking.customer and booking.customer.email else ""
                    if booking.customer.phone_number:
                        bk['phone'] = booking.customer.phone_number
                    elif booking.customer.mobile_number:
                        bk['phone'] = booking.customer.mobile_number
                    else:
                        bk['phone'] = ''
                    if booking.is_canceled:
                        bk['campground_site_type'] = ""
                    else:
                        first_campsite_list = booking.first_campsite_list
                        campground_site_type = []
                        for item in first_campsite_list:
                            campground_site_type.append({
                                "name": '{}'.format(item.name if item else ""),
                                "type": '{}'.format(item.type if item.type else ""),
                                "campground_type": item.campground.site_type,
                            })
                        bk['campground_site_type'] = campground_site_type
                else:
                    bk['campground_site_type'] = ""
                if refund_status and canceled == 't':
                    refund_statuses = ['All', 'Partially Refunded', 'Not Refunded', 'Refunded']
                    if refund_status in refund_statuses:
                        if refund_status == 'All':
                            clean_data.append(bk)
                        else:
                            if refund_status == booking.refund_status:
                                clean_data.append(bk)
                else:
                    clean_data.append(bk)

            return Response(OrderedDict([
                ('recordsTotal', recordsTotal),
                ('recordsFiltered', recordsFiltered),
                ('results', clean_data)
            ]), status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, format=None):
        userCreated = False
        try:
            if 'ps_booking' in request.session:
                del request.session['ps_booking']
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            start_date = serializer.validated_data['arrival']
            end_date = serializer.validated_data['departure']
            guests = request.data['guests']
            costs = request.data['costs']
            regos = request.data['regos']
            override_price = serializer.validated_data.get('override_price', None)
            override_reason = serializer.validated_data.get('override_reason', None)
            override_reason_info = serializer.validated_data.get('override_reason_info', None)
            send_invoice = serializer.validated_data.get('send_invoice', False)
            overridden_by = None if (override_price is None) else request.user
            try:
                emailUser = request.data['customer']
                customer = EmailUser.objects.get(email=emailUser['email'])
            except EmailUser.DoesNotExist:
                customer = EmailUser.objects.create(
                    email=emailUser['email'],
                    first_name=emailUser['first_name'],
                    last_name=emailUser['last_name'],
                    phone_number=emailUser['phone'],
                    mobile_number=emailUser['phone'],
                )
                userCreated = True
                try:
                    country = emailUser['country']
                    country = Country.objects.get(iso_3166_1_a2=country)
                    Address.objects.create(line1='address', user=customer, postcode=emailUser['postcode'], country=country.iso_3166_1_a2)
                except Country.DoesNotExist:
                    raise serializers.ValidationError("Country you have entered does not exist")

            booking_details = {
                'campsites': Campsite.objects.filter(id__in=request.data['campsites']),
                'start_date': start_date,
                'end_date': end_date,
                'num_adult': guests['adult'],
                'num_concession': guests['concession'],
                'num_child': guests['child'],
                'num_infant': guests['infant'],
                'cost_total': costs['total'],
                'override_price': override_price,
                'override_reason': override_reason,
                'override_reason_info': override_reason_info,
                'send_invoice': send_invoice,
                'overridden_by': overridden_by,
                'customer': customer,
                'first_name': emailUser['first_name'],
                'last_name': emailUser['last_name'],
                'country': emailUser['country'],
                'postcode': emailUser['postcode'],
                'phone': emailUser['phone'],
                'regos': regos
            }
            data = utils.internal_booking(request, booking_details)
            serializer = self.get_serializer(data)
            return Response(serializer.data)
        except serializers.ValidationError:
            utils.delete_session_booking(request.session)
            if userCreated:
                customer.delete()
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        except Exception as e:
            utils.delete_session_booking(request.session)
            if userCreated:
                customer.delete()
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def update(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK

            instance = self.get_object()
            start_date = datetime.strptime(request.data['arrival'], '%d/%m/%Y').date()
            end_date = datetime.strptime(request.data['departure'], '%d/%m/%Y').date()
            guests = request.data['guests']
            booking_details = {
                'campsites': request.data['campsites'],
                'start_date': start_date,
                'campground': request.data['campground'],
                'end_date': end_date,
                'num_adult': guests['adults'],
                'num_concession': guests['concession'],
                'num_child': guests['children'],
                'num_infant': guests['infants'],
                'regos': request.data['entryFees']['regos'],
            }
            data = utils.update_booking(request, instance, booking_details)
            serializer = BookingSerializer(data)
            return Response(serializer.data, status=http_status)

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def destroy(self, request, *args, **kwargs):

        http_status = status.HTTP_200_OK
        try:
            reason = request.GET.get('reason', None)
            if not reason:
                raise serializers.ValidationError('A reason is needed before canceling a booking')
            booking = self.get_object()
            booking.cancelBooking(reason, user=request.user)
            emails.send_booking_cancelation(booking, request)
            serializer = self.get_serializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(permission_classes=[PaymentCallbackPermission], methods=['GET', 'POST'])
    def payment_callback(self, request, *args, **kwargs):
        http_status = status.HTTP_200_OK
        try:
            response = {
                'status': 'rejected',
                'error': ''
            }
            if request.method == 'GET':
                response = {'status': 'accessible'}
            elif request.method == 'POST':
                instance = self.get_object()

                invoice_ref = request.data.get('invoice', None)
                if invoice_ref:
                    try:
                        invoice = Invoice.objects.get(reference=invoice_ref)
                        if invoice.payment_status in ['paid', 'over_paid']:
                            # Get the latest cash payment and see if it was paid in the last 1 minute
                            latest_cash = invoice.cash_transactions.last()
                            # Check if the transaction came in the last 10 seconds
                            if (timezone.now() - latest_cash.created).seconds < 10 and instance.paid:
                                # Send out the confirmation pdf
                                emails.send_booking_confirmation(instance, request)
                            else:
                                response['error'] = 'Booking is not fully paid or the transaction was not done in the last 10 secs'
                        else:
                            response['error'] = 'Invoice is not fully paid'

                    except Invoice.DoesNotExist:
                        response['error'] = 'Invoice was not found'
                else:
                    response['error'] = 'Invoice was not found'

                response['status'] = 'approved'
            return Response(response, status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(permission_classes=[], methods=['GET'])
    def booking_checkout_status(self, request, *args, **kwargs):
        from django.utils import timezone
        http_status = status.HTTP_200_OK
        try:
            instance = self.get_object()
            response = {
                'status': 'rejected',
                'error': ''
            }
            # Check the type of booking
            if instance.booking_type != 3:
                response['error'] = 'This booking has already been paid for'
                return Response(response, status=status.HTTP_200_OK)
            # Check if the time for the booking has elapsed
            if instance.expiry_time <= timezone.now():
                response['error'] = 'This booking has expired'
                return Response(response, status=status.HTTP_200_OK)
            # if all is well
            response['status'] = 'approved'
            return Response(response, status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET'])
    def history(self, request, *args, **kwargs):
        http_status = status.HTTP_200_OK
        try:
            history = self.get_object().history.all()
            data = BookingHistorySerializer(history, many=True).data
            return Response(data, status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class CampsiteRateViewSet(viewsets.ModelViewSet):
    queryset = CampsiteRate.objects.all()
    serializer_class = CampsiteRateSerializer

    def create(self, request, format=None):
        try:
            http_status = status.HTTP_200_OK
            rate = None
            rate_serializer = RateDetailSerializer(data=request.data)
            rate_serializer.is_valid(raise_exception=True)
            rate_id = rate_serializer.validated_data.get('rate', None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e:
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=rate_serializer.validated_data['adult'], concession=rate_serializer.validated_data['concession'], child=rate_serializer.validated_data['child'])[0]
            if rate:
                data = {
                    'rate': rate.id,
                    'date_start': rate_serializer.validated_data['period_start'],
                    'campsite': rate_serializer.validated_data['campsite'],
                    'reason': rate_serializer.validated_data['reason'],
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
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def update(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            rate = None
            rate_serializer = RateDetailSerializer(data=request.data)
            rate_serializer.is_valid(raise_exception=True)
            rate_id = rate_serializer.validated_data.get('rate', None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e:
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=rate_serializer.validated_data['adult'], concession=rate_serializer.validated_data['concession'], child=rate_serializer.validated_data['child'])[0]
                pass
            if rate:
                data = {
                    'rate': rate.id,
                    'date_start': rate_serializer.validated_data['period_start'],
                    'campsite': rate_serializer.validated_data['campsite'],
                    'reason': rate_serializer.validated_data['reason'],
                    'update_level': 2
                }
                instance = self.get_object()
                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                return Response(serializer.data, status=http_status)

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            if instance.range_end and not serializer.validated_data.get('range_end'):
                instance.range_end = None
            self.perform_update(serializer)

            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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


class PriceReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceReason.objects.all()
    serializer_class = PriceReasonSerializer


class MaximumStayReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaximumStayReason.objects.all()
    serializer_class = MaximumStayReasonSerializer


class DiscountReasonViewset(viewsets.ReadOnlyModelViewSet):
    queryset = DiscountReason.objects.all()
    serializer_class = DiscountReasonSerializer


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.order_by('-display_order', 'printable_name')
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]


class UsersViewSet(viewsets.ModelViewSet):
    queryset = EmailUser.objects.all()
    serializer_class = UsersSerializer

    def list(self, request, *args, **kwargs):
        start = request.GET.get('start') if request.GET.get('draw') else 1
        length = request.GET.get('length') if request.GET.get('draw') else 10
        q = request.GET.get('q')
        if q:
            queryset = EmailUser.objects.filter(email__icontains=q)[:10]
        else:
            queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['POST', ])
    def update_personal(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = PersonalSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def update_contact(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = UserContactSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    def update_address(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = UserAddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            address, created = Address.objects.get_or_create(
                line1=serializer.validated_data['line1'],
                locality=serializer.validated_data['locality'],
                state=serializer.validated_data['state'],
                country=serializer.validated_data['country'],
                postcode=serializer.validated_data['postcode'],
                user=instance
            )
            instance.residential_address = address
            instance.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
# Bulk Pricing
# ===========================


class BulkPricingView(generics.CreateAPIView):
    serializer_class = BulkPricingSerializer
    renderer_classes = (JSONRenderer,)

    def create(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            rate_id = serializer.data.get('rate', None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e:
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'], concession=serializer.validated_data['concession'], child=serializer.validated_data['child'])[0]
            if rate:
                data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.data['reason']),
                    'details': serializer.validated_data.get('details', None)
                }
            if serializer.data['type'] == 'Park':
                for c in serializer.data['campgrounds']:
                    data['update_level'] = 0
                    Campground.objects.get(pk=c).createCampsitePriceHistory(data)
            elif serializer.data['type'] == 'Campsite Type':
                data['update_level'] = 1
                CampsiteClass.objects.get(pk=serializer.data['campsiteType']).createCampsitePriceHistory(data)

            return Response(serializer.data, status=http_status)

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e[0]))


class BookingRefundsReportView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        try:
            http_status = status.HTTP_200_OK
            # parse and validate data
            report = None
            data = {
                "start": request.GET.get('start'),
                "end": request.GET.get('end'),
            }
            serializer = ReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'Booking Refunds Report-{}-{}'.format(str(serializer.validated_data['start']), str(serializer.validated_data['end']))
            # Generate Report
            report = reports.booking_refunds(serializer.validated_data['start'], serializer.validated_data['end'])
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()


class BookingSettlementReportView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        try:
            http_status = status.HTTP_200_OK
            # parse and validate data
            report = None
            data = {
                "date": request.GET.get('date'),
            }
            serializer = BookingSettlementReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'Booking Settlement Report-{}'.format(str(serializer.validated_data['date']))
            # Generate Report
            report = reports.booking_bpoint_settlement_report(serializer.validated_data['date'])
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()


class BookingReportView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        try:
            http_status = status.HTTP_200_OK
            # parse and validate data
            report = None
            data = {
                "date": request.GET.get('date'),
            }
            serializer = BookingSettlementReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'Booking Report-{}'.format(str(serializer.validated_data['date']))
            # Generate Report
            report = reports.bookings_report(serializer.validated_data['date'])
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()


class GetProfile(views.APIView):
    renderer_classes = [JSONRenderer, ]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Check if the user has any address and set to residential address
        user = request.user
        if not user.residential_address:
            user.residential_address = user.profile_addresses.first() if user.profile_addresses.all() else None
            user.save()
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UpdateProfilePersonal(views.APIView):
    renderer_classes = [JSONRenderer, ]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            instance = request.user
            serializer = PersonalSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class UpdateProfileContact(views.APIView):
    renderer_classes = [JSONRenderer, ]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            instance = request.user
            serializer = PhoneSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class UpdateProfileAddress(views.APIView):
    renderer_classes = [JSONRenderer, ]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            instance = request.user
            serializer = UserAddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            address, created = Address.objects.get_or_create(
                line1=serializer.validated_data.get('line1'),
                locality=serializer.validated_data.get('locality'),
                state=serializer.validated_data.get('state'),
                country=serializer.validated_data.get('country'),
                postcode=serializer.validated_data.get('postcode'),
                user=instance
            )
            instance.residential_address = address
            instance.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class OracleJob(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        try:
            data = {
                "date": request.GET.get("date"),
                "override": request.GET.get("override")
            }
            serializer = OracleSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            utils.oracle_integration(serializer.validated_data['date'].strftime('%Y-%m-%d'), serializer.validated_data['override'])
            data = {'successful': True}
            return Response(data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e[0]))
