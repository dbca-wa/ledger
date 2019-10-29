import traceback
import base64
import geojson
import decimal
import logging
import json
import calendar
import time
import math
import hashlib
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from django.db.models import Q, Min
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from pytz import timezone as pytimezone
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route,renderer_classes,authentication_classes,permission_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser,Address
from ledger.address.models import Country
from ledger.payments.models import Invoice, OracleAccountCode
from django.db.models import Count
from mooring import utils
from mooring.helpers import can_view_campground, is_inventory, is_admin, is_payment_officer
from datetime import datetime,timedelta, date
from decimal import Decimal
from ledger.payments.utils import systemid_check, update_payments
from mooring.context_processors import mooring_url, template_context
from mooring.models import (MooringArea,
                                District,
                                Contact,
                                MooringsiteBooking,
                                Mooringsite,
                                MooringsiteRate,
                                Booking,
                                MooringAreaBookingRange,
                                MooringsiteBookingRange,
                                MooringsiteStayHistory,
                                MooringAreaStayHistory,
                                PromoArea,
                                MarinePark,
                                Feature,
                                Region,
                                MooringsiteClass,
                                Booking,
                                MooringsiteRate,
                                Rate,
                                MooringAreaPriceHistory,
                                MooringsiteClassPriceHistory,
                                ClosureReason,
                                OpenReason,
                                PriceReason,
                                AdmissionsReason,
                                MaximumStayReason,
                                DiscountReason,
                                MarinaEntryRate,
                                BookingVehicleRego,
                                MooringAreaGroup,
                                AdmissionsBooking,
                                AdmissionsLine,
                                AdmissionsLocation,
                                AdmissionsRate,
                                AdmissionsBookingInvoice,
                                AdmissionsOracleCode,
                                BookingInvoice,
                                BookingPeriodOption,
                                BookingPeriod,
                                RegisteredVessels,
                                GlobalSettings
                                )

from mooring.serialisers import (  MooringsiteBookingSerialiser,
                                    MooringsiteSerialiser,
                                    ContactSerializer,
                                    DistrictSerializer,
                                    MooringAreaMapSerializer,
                                    MarineParkMapSerializer,
                                    MarineParkRegionMapSerializer,
                                    MooringAreaMapFilterSerializer,
                                    MooringAreaSerializer,
                                    MooringAreaDatatableSerializer,
                                    MooringAreaMooringsiteFilterSerializer,
                                    MooringsiteBookingSerializer,
                                    PromoAreaSerializer,
                                    MarinaSerializer,
                                    FeatureSerializer,
                                    RegionSerializer,
                                    MooringsiteClassSerializer,
                                    BookingSerializer,
                                    MooringAreaBookingRangeSerializer,
                                    MooringsiteBookingRangeSerializer,
                                    MooringsiteRateSerializer,
                                    MooringsiteRateReadonlySerializer,
                                    MooringsiteStayHistorySerializer,
                                    MooringAreaStayHistorySerializer,
                                    RateSerializer,
                                    RateDetailSerializer,
                                    MooringAreaPriceHistorySerializer,
                                    MooringsiteClassPriceHistorySerializer,
                                    MooringAreaImageSerializer,
                                    ExistingMooringAreaImageSerializer,
                                    ClosureReasonSerializer,
                                    OpenReasonSerializer,
                                    PriceReasonSerializer,
                                    AdmissionsReasonSerializer,
                                    MaximumStayReasonSerializer,
                                    DiscountReasonSerializer,
                                    BulkPricingSerializer,
                                    UsersSerializer,
                                    AccountsAddressSerializer,
                                    MarinaEntryRateSerializer,
                                    ReportSerializer,
                                    BookingSettlementReportSerializer,
                                    CountrySerializer,
                                    UserSerializer,
                                    UserAddressSerializer,
                                    ContactSerializer as UserContactSerializer,
                                    PersonalSerializer,
                                    PhoneSerializer,
                                    OracleSerializer,
                                    BookingHistorySerializer,
                                    MooringAreaGroupSerializer,
                                    AdmissionsBookingSerializer,
                                    AdmissionsLineSerializer,
                                    AdmissionsRateSerializer,
                                    BookingPeriodOptionsSerializer,
                                    BookingPeriodSerializer,
                                    RegisteredVesselsSerializer,
                                    GlobalSettingsSerializer,
                                    )
from mooring.helpers import is_officer, is_customer
from mooring import reports 
from mooring import pdf
from mooring.perms import PaymentCallbackPermission
from mooring import emails
from mooring import exceptions
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance  
from ledger.payments.bpoint.models import BpointTransaction, BpointToken

# API Views
class MooringsiteBookingViewSet(viewsets.ModelViewSet):
    queryset = MooringsiteBooking.objects.all()
    serializer_class = MooringsiteBookingSerialiser

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

    def list(self, request, *args, **kwargs):
        groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
        qs = self.get_queryset()
        mooring_groups = []
        for group in groups:
            mooring_groups.append(group.id)
        queryset = qs.filter(mooring_group__in=mooring_groups)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def list(self, request, *args, **kwargs):
        groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
        qs = self.get_queryset()
        mooring_groups = []
        for group in groups:
            mooring_groups.append(group.id)
        queryset = qs.filter(mooring_group__in=mooring_groups)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MooringsiteViewSet(viewsets.ModelViewSet):
    queryset = Mooringsite.objects.all()
    serializer_class = MooringsiteSerialiser


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
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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
                campsites = Mooringsite.bulk_create(number,data)
                res = self.get_serializer(campsites,many=True)
            else:
                if number == 1 and serializer.validated_data['name'] == 'default':
                    latest = 0
                    current_campsites = Mooringsite.objects.filter(campground=serializer.validated_data.get('campground'))
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
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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
            serializer = MooringsiteBookingRangeSerializer(data=request.data, method="post")
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data.get('status') == 0:
                self.get_object().open(dict(serializer.validated_data))
            else:
                self.get_object().close(dict(serializer.validated_data))

            # return object
            ground = self.get_object()
            res = MooringsiteSerialiser(ground, context={'request':request})

            return Response(res.data)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def close_campsites(self, closure_data, campsites):
        for campsite in campsites:
            closure_data['campsite'] = campsite
            try:
                serializer = MooringsiteBookingRangeSerializer(data=closure_data, method='post')
                serializer.is_valid(raise_exception=True)
                instance = Mooringsite.objects.get(pk=campsite)
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
                serializer = MooringsiteBookingRangeSerializer(self.get_object().booking_ranges.filter(~Q(status=0)).order_by('-range_start'),many=True)
            else:
                serializer = MooringsiteBookingRangeSerializer(self.get_object().booking_ranges,many=True)
            res = serializer.data

            return Response(res,status=http_status)
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
            serializer = MooringsiteStayHistorySerializer(self.get_object().stay_history,many=True,context={'request':request},method='get')
            res = serializer.data

            return Response(res,status=http_status)
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
            serializer = MooringsiteRateReadonlySerializer(price_history,many=True,context={'request':request})
            res = serializer.data
            return Response(res,status=http_status)
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
            start_date = request.GET.get('arrival',False)
            end_date = request.GET.get('departure',False)
            res = []
            if start_date and end_date:
                res = utils.get_campsite_current_rate(request,self.get_object().id,start_date,end_date)
            else:
                res.append({
                    "error":"Arrival and departure dates are required",
                    "success":False
                })

            return Response(res,status=http_status)
        except serializers.ValidationError:
            traceback.print_exc()
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))



class MooringsiteStayHistoryViewSet(viewsets.ModelViewSet):
    queryset = MooringsiteStayHistory.objects.all()
    serializer_class = MooringsiteStayHistorySerializer

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
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

class MooringAreaStayHistoryViewSet(viewsets.ModelViewSet):
    queryset = MooringAreaStayHistory.objects.all()
    serializer_class = MooringAreaStayHistorySerializer

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
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

class MooringAreaMapViewSet(viewsets.ReadOnlyModelViewSet):
#   queryset = MooringArea.objects.exclude(campground_type=3).annotate(Min('mooringsites__rates__rate__adult'))
    queryset = MooringArea.objects.exclude(mooring_type=3)
    serializer_class = MooringAreaMapSerializer
    permission_classes = []

class MarineParksRegionMapViewSet(viewsets.ReadOnlyModelViewSet):
#    queryset = MooringArea.objects.values('park_id__name','park_id__wkb_geometry').annotate(total=Count('park'))
    queryset = MooringArea.objects.values('park__district__region','park__district__region__name','park__district__region__wkb_geometry').annotate(total=Count('park__district__region'))
    serializer_class = MarineParkRegionMapSerializer
    permission_classes = []

class MarineParksMapViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = District.objects.all()
    queryset = MooringArea.objects.values('park_id__name','park_id__wkb_geometry').annotate(total=Count('park'))
    serializer_class = MarineParkMapSerializer 
    permission_classes = []

class MooringAreaMapFilterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MooringArea.objects.exclude(mooring_type=3)
    serializer_class = MooringAreaMapFilterSerializer
    permission_classes = []

    def list(self, request, *args, **kwargs):
        data = {
            "arrival" : request.GET.get('arrival', None),
            "departure" : request.GET.get('departure', None),
            "num_adult" : request.GET.get('num_adult', 0),
            "num_concession" : request.GET.get('num_concession', 0),
            "num_child" : request.GET.get('num_child', 0),
            "num_infant" : request.GET.get('num_infant', 0),
            "avail": request.GET.get('gear_type', 'all'),
            "pen_type": request.GET.get('pen_type', 'all')
        }
 
        serializer = MooringAreaMooringsiteFilterSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        scrubbed = serializer.validated_data
        context = {}
        ground_ids = []
        open_marinas = [] 
        #Removed from parkstay
        # filter to the campsites by gear allowed (if specified), else show the lot
        # if scrubbed['gear_type'] != 'all':
        #     context = {scrubbed['gear_type']: True}

        # if a date range is set, filter out campgrounds that are unavailable for the whole stretch
        if scrubbed['arrival'] and scrubbed['departure'] and (scrubbed['arrival'] < scrubbed['departure']):
            sites = Mooringsite.objects.filter(**context)
            #ground_ids = utils.get_open_marinas(sites, scrubbed['arrival'], scrubbed['departure'])

            open_marinas = utils.get_open_marinas(sites, scrubbed['arrival'], scrubbed['departure'])
            for i in open_marinas:
                 ground_ids.append(i) 

        else:
            # show all of the campgrounds with campsites
            ground_ids = set((x[0] for x in Mooringsite.objects.filter(**context).values_list('mooringarea')))
            # we need to be tricky here. for the default search (all, no timestamps),
            # we want to include all of the "campgrounds" that don't have any campsites in the model! (e.g. third party)
            if scrubbed['avail'] == 'all':
                ground_ids.update((x[0] for x in MooringArea.objects.filter(campsites__isnull=True).values_list('id')))

        # If the pen type has been included in filtering and is not 'all' then loop through the sites selected.
        if scrubbed['pen_type'] != 'all':
            sites = Mooringsite.objects.filter(pk__in=ground_ids)
            for s in sites:           
            # When looping through, if the pen type is not correct, remove it from the list.
                i = s.mooringarea
                if i.mooring_physical_type != scrubbed['pen_type']:
                    ground_ids.remove(s.id)

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
        
        temp_queryset = Mooringsite.objects.filter(id__in=ground_ids).order_by('name')

        queryset = []
        for q in temp_queryset:
            # Get the current stay history
            stay_history = MooringAreaStayHistory.objects.filter(
                            Q(range_start__lte=start_date,range_end__gte=start_date)|# filter start date is within period
                            Q(range_start__lte=end_date,range_end__gte=end_date)|# filter end date is within period
                            Q(Q(range_start__gt=start_date,range_end__lt=end_date)&Q(range_end__gt=today)) #filter start date is before and end date after period
                            ,mooringarea=q.mooringarea)


            if stay_history:
                max_days = min([x.max_days for x in stay_history])
            else:
                max_days = settings.PS_MAX_BOOKING_LENGTH
            if (end_date - start_date).days <= max_days:         
                row = {}
                row['id'] = q.mooringarea.id
                if q.id in open_marinas:
                    row['avail2'] = open_marinas[q.id]
                #row['avail'] = 'full'
                if q.mooringarea.mooring_type == 1:
                        row['avail'] = 'full'
                else:
                     if q.id in open_marinas:

                         if int(open_marinas[q.id]['closed_periods']) == 0 and int(open_marinas[q.id]['open_periods']) > 0:
                            row['avail'] = 'free'
                         elif int(open_marinas[q.id]['open_periods']) == 0:
                            row['avail'] = 'full'
                         elif int(open_marinas[q.id]['closed_periods']) > 0 and int(open_marinas[q.id]['open_periods']) > 0:
                            row['avail'] = 'partial'

                queryset.append(row)
        
        # Filter based on the availability
        query = []
        if scrubbed['avail'] != 'all':
            for q in queryset:
                mooring_type = MooringArea.objects.get(id=q['id']).mooring_type
                if scrubbed['avail'] == 'rental-available' and q['avail'] not in ['free', 'partial']:
                    pass
                elif scrubbed['avail'] == 'rental-notavailable' and (q['avail'] not in ['full'] or mooring_type == 2):
                        pass
                elif scrubbed['avail'] == 'public-notbookable':
                    if mooring_type != 2:
                        pass
                    else:
                        query.append(q)
                else:
                    query.append(q)
        else:
            query = queryset
                
#        serializer = self.get_serializer(queryset, many=True)
        return HttpResponse(json.dumps(query), content_type='application/json')
#        return Response(serializer.data)

def current_booking(request, *args, **kwargs):
    queryset = MooringArea.objects.exclude(mooring_type=3)
    response_data = {}
    response_data['result'] = 'success'
    response_data['message'] = ''
    ongoing_booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
    response_data['current_booking'] = get_current_booking(ongoing_booking, request)
    return HttpResponse(json.dumps(response_data), content_type='application/json')


@require_http_methods(['GET'])
def search_suggest(request, *args, **kwargs):
    entries = []
    for x in MooringArea.objects.filter(wkb_geometry__isnull=False).values_list('id', 'name', 'wkb_geometry','park__name','park__district__region__name'):
        entries.append(geojson.Point((x[2].x, x[2].y), properties={'type': 'MooringArea', 'id': x[0], 'name': x[1]+' - '+x[3]+' - '+x[4]}))
    for x in MarinePark.objects.filter(wkb_geometry__isnull=False).values_list('id', 'name', 'wkb_geometry','zoom_level','district__region__name'):
        entries.append(geojson.Point((x[2].x, x[2].y), properties={'type': 'Marina', 'id': x[0], 'name': x[1]+' - '+x[4], 'zoom_level': x[3]}))
    for x in PromoArea.objects.filter(wkb_geometry__isnull=False).values_list('id', 'name', 'wkb_geometry', 'zoom_level'):
        entries.append(geojson.Point((x[2].x, x[2].y), properties={'type': 'PromoArea', 'id': x[0], 'name': x[1], 'zoom_level': x[3]}))
    for x in Region.objects.filter(wkb_geometry__isnull=False).values_list('id', 'name', 'wkb_geometry','zoom_level'):
        entries.append(geojson.Point((x[2].x, x[2].y), properties={'type': 'Region', 'id': x[0], 'name': x[1], 'zoom_level': x[3]}))
    return HttpResponse(geojson.dumps(geojson.FeatureCollection(entries)), content_type='application/json')

@csrf_exempt
def delete_booking(request, *args, **kwargs):
    response_data = {}
    response_data['result'] = 'success'
    response_data['message'] = ''
    payments_officer_group = request.user.groups.filter(name__in=['Payments Officers']).exists()
    nowtime = datetime.strptime(str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')+timedelta(hours=8)
    booking = None
    booking_item = request.POST['booking_item']
    if 'ps_booking' in request.session:
        booking_id = request.session['ps_booking']
        if booking_id:
            booking = Booking.objects.get(id=booking_id)
            ms_booking = MooringsiteBooking.objects.get(id=booking_item,booking=booking)
            msb = datetime.strptime(str(ms_booking.from_dt.strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')+timedelta(hours=8)
            if msb > nowtime:
                  ms_booking.delete()
            elif payments_officer_group is True:
                  ms_booking.delete()
            else:
                 if msb.date() == nowtime.date():
                     if booking.old_booking is None:
                          ms_booking.delete() 
                     else:
                         response_data['result'] = 'error'
                         response_data['message'] = 'Unable to delete booking'

                 else:

                     response_data['result'] = 'error'
                     response_data['message'] = 'Unable to delete booking'
    return HttpResponse(json.dumps(response_data), content_type='application/json')

@csrf_exempt
#@require_http_methods(['GET'])
#@require_http_methods(['POST'])
def add_booking(request, *args, **kwargs):
    response_data = {}
    response_data['result'] = 'error'
    response_data['message'] = ''
    booking_date = request.POST['date']
#    booking_period_start = request.POST['booking_start']
#    booking_period_finish = request.POST['booking_finish']
    booking_period_start = datetime.strptime(request.POST['booking_start'], "%d/%m/%Y").date()
    booking_period_finish = datetime.strptime(request.POST['booking_finish'], "%d/%m/%Y").date()
    num_adults = request.POST.get('num_adult', 0)
    num_children = request.POST.get('num_children', 0)
    num_infants = request.POST.get('num_infant',0)
    vessel_size = request.POST.get('vessel_size', 0)
    vessel_draft = request.POST.get('vessel_draft', 0)
    vessel_beam = request.POST.get('vessel_beam', 0)
    vessel_weight = request.POST.get('vessel_weight', 0)
    vessel_rego = request.POST.get('vessel_rego', 0)

    start_booking_date = request.POST['date']
    finish_booking_date = request.POST['date']

    booking = None
    if 'ps_booking' in request.session:
        booking_id = request.session['ps_booking']
        if booking_id:
            booking = Booking.objects.get(id=booking_id)
            booking.arrival = booking_period_start
            booking.departure = booking_period_finish
            if not booking.details:
                booking.details = {}
            booking.details['num_adults'] = num_adults
            booking.details['num_children'] = num_children
            booking.details['num_infants'] = num_infants
            booking.details['vessel_size'] = vessel_size
            booking.details['vessel_draft'] = vessel_draft
            booking.details['vessel_beam'] = vessel_beam
            booking.details['vessel_weight'] = vessel_weight
            booking.details['vessel_rego'] = vessel_rego
            booking.save()
    else:
        details = {
           'num_adults' : num_adults,
           'num_children' : num_children,
           'num_infants' : num_infants,
           'vessel_size' : vessel_size,
           'vessel_draft': vessel_draft,
           'vessel_beam' : vessel_beam,
           'vessel_weight' : vessel_weight,
           'vessel_rego' : vessel_rego,
        }
        mooringarea = MooringArea.objects.get(id=request.POST['mooring_id'])
        booking = Booking.objects.create(mooringarea=mooringarea,booking_type=3,expiry_time=timezone.now()+timedelta(seconds=settings.BOOKING_TIMEOUT),details=details,arrival=booking_period_start,departure=booking_period_finish)
        request.session['ps_booking'] = booking.id
        request.session.modified = True

    #print BookingPeriodOption.objects.all()
    mooringsite = Mooringsite.objects.get(id=request.POST['site_id'])

    booking_period = BookingPeriodOption.objects.get(id=int(request.POST['bp_id'])) 

    if booking_period.start_time > booking_period.finish_time:
            finish_bd = datetime.strptime(finish_booking_date, "%Y-%m-%d").date()
            finish_booking_date = str(finish_bd+timedelta(days=1))
            #print finish_bd

    mooring_class = mooringsite.mooringarea.mooring_class
    amount = '0.00'

    if mooring_class == 'small':
        amount = booking_period.small_price
    elif mooring_class == 'medium':
        amount = booking_period.medium_price
    elif mooring_class == 'large':
        amount = booking_period.large_price
#    MooringsiteBooking
#    for i in range((end_date-start_date).days):

    from_dt_utc = datetime.strptime(str(start_booking_date)+' '+str(booking_period.start_time), '%Y-%m-%d %H:%M:%S') - timedelta(hours=8)
    to_dt_utc =  datetime.strptime(str(finish_booking_date)+' '+str(booking_period.finish_time), '%Y-%m-%d %H:%M:%S') - timedelta(hours=8)
    from_dt_utc = from_dt_utc.replace(tzinfo=timezone.utc).isoformat()
    to_dt_utc =  to_dt_utc.replace(tzinfo=timezone.utc).isoformat()
    #to_dt__lte=to_dt_utc
    existing_booking_check = utils.check_mooring_available_by_time(mooringsite.id,from_dt_utc,to_dt_utc)
    if existing_booking_check is True:
        response_data['result'] = 'error'
        response_data['message'] = 'Sorry booking has already been taken by another booking.' 

    
    else:
        cb =    MooringsiteBooking.objects.create(
                  campsite=mooringsite,
                  booking_type=3,
                  date=booking_date,
                  from_dt=start_booking_date+' '+str(booking_period.start_time),
                  to_dt=finish_booking_date+' '+str(booking_period.finish_time),
                  booking=booking,
                  amount=amount,
                  booking_period_option=booking_period 
                  )

        response_data['result'] = 'success'
        response_data['message'] = ''

#    with transaction.atomic():
#            set_session_booking(request.session,booking)


    #booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
#    if request.user.is_anonymous():
#        form = AnonymousMakeBookingsForm(request.POST)

    return HttpResponse(json.dumps(response_data), content_type='application/json')

class MooringAreaViewSet(viewsets.ModelViewSet):
    from django.db.models import Value, ManyToManyField
    queryset = MooringArea.objects.all().annotate(mooring_group=Value(None,output_field=ManyToManyField(MooringAreaGroup,blank=True)))
    serializer_class = MooringAreaSerializer

    @list_route(methods=['GET',])
    @renderer_classes((JSONRenderer,))
    def datatable_list(self,request,format=None):
        queryset = cache.get('moorings_dt')
        if queryset is None:
            queryset = self.get_queryset()
            cache.set('moorings_dt',queryset,3600)
        qs = [c for c in queryset.all() if can_view_campground(request.user,c)]
        serializer = MooringAreaDatatableSerializer(qs,many=True)
        data = serializer.data
        return Response(data)

    @renderer_classes((JSONRenderer,))
    def list(self, request, format=None):
        queryset = cache.get('mooringareas')
        formatted = bool(request.GET.get("formatted", False))
        if queryset is None:
            queryset = self.get_queryset()
            cache.set('mooringareas',queryset,3600)
        queryset = self.get_queryset()
        qs = [c for c in queryset.all() if can_view_campground(request.user,c)]
        serializer = self.get_serializer(qs, formatted=formatted, many=True, method='get')
        data = serializer.data
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        formatted = bool(request.GET.get("formatted", False))
        groups =  MooringAreaGroup.objects.filter(members__in=[request.user.id,],moorings__in=[instance.id,])
        if groups.count() > 0:
            instance.mooring_group = groups[0].id
        if Mooringsite.objects.filter(mooringarea__id=instance.id).exists():
           pass
        else:
           mooringsite_class = MooringsiteClass.objects.all().first()    
           Mooringsite.objects.create(mooringarea=instance, 
                                      name=instance.name, 
                                      mooringsite_class=mooringsite_class,
                                      description=None)
       
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
            instance.mooring_group = None

            cache.set('moorings_dt', self.get_queryset(), 3600)
        
            # Get and Validate campground images
            initial_image_serializers = [MooringAreaImageSerializer(data=image) for image in images_data] if images_data else []
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

            if "oracle_code" in request.data:
                  oracle_code = request.data.pop("oracle_code")
                  if OracleAccountCode.objects.filter(active_receivables_activities=oracle_code).count() == 0:
                      raise serializers.ValidationError("Oracle Code does not exist")

            if "mooring_group" in request.data:
                mooring_group = request.data.pop("mooring_group")
                mg = MooringAreaGroup.objects.all()
                for i in mg:
                    # i.campgrounds.clear()
                    if i.id == int(mooring_group[0]):
                        m_all = i.moorings.all()
                        if instance.id in m_all:
                            pass
                        else:
                            i.moorings.add(instance)
                    else:
                        m_all = i.moorings.all()
                        for b in m_all:
                           if instance.id == b.id:
                              i.moorings.remove(b)

            if Mooringsite.objects.filter(mooringarea__id=instance.id).exists():
                pass
            else:
                mooringsite_class = MooringsiteClass.objects.all().first()
                Mooringsite.objects.create(mooringarea=instance,
                                      name=instance.name,
                                      mooringsite_class=mooringsite_class,
                                      description=None)

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
        #= MooringAreaSerializer
        try:
            images_data = None
            http_status = status.HTTP_200_OK
            instance = self.get_object()
            post = request.data
            instance.mooring_group = None
            if "mooring_group" in request.data:
                mooring_group = request.data.pop("mooring_group")
                
                # mg = MooringAreaGroup.objects.filter(id__in=mooring_group)

                mg = MooringAreaGroup.objects.all()
                for i in mg:
                    # i.campgrounds.clear()
                    if i.pk == mooring_group: 
                        m_all = i.moorings.all()
                        if instance.id in m_all:
                            pass
                        else:
                            i.moorings.add(instance)
                    else:
                        m_all = i.moorings.all()
                        for b in m_all:
                           if instance.id == b.id:
                              i.moorings.remove(b)

                
            if "oracle_code" in request.data:
                  oracle_code = request.data.pop("oracle_code")
                  if OracleAccountCode.objects.filter(active_receivables_activities=oracle_code).count() == 0:
                      raise serializers.ValidationError("Oracle Code does not exist") 
            if "images" in request.data:
                images_data = request.data.pop("images")
            serializer = self.get_serializer(instance,data=request.data,partial=True)
            serializer.is_valid(raise_exception=True)
            # Get and Validate campground images
            initial_image_serializers = [MooringAreaImageSerializer(data=image) for image in images_data] if images_data else []
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
                        existing_image_serializers.append(ExistingMooringAreaImageSerializer(data=data))
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
            instance.mooring_group = MooringAreaGroup.objects.filter(moorings__in=[instance.id])[0].id
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
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
            date_start = request.POST['range_start']
            time_start = request.POST.get('range_start_time', "00:00")
            request.POST['range_start'] = date_start +" "+ time_start
            date_end = request.POST.get('range_end', None)
            time_end = request.POST.get('range_end_time', "23:59")
            if date_end is not None and date_end != "" and date_end != " ":
                request.POST['range_end'] = date_end +" "+ time_end
            request.POST._mutable = mutable
            serializer = MooringAreaBookingRangeSerializer(data=request.data, method="post")
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data.get('status') == 0:
                self.get_object().open(dict(serializer.validated_data))
            else:
                self.get_object().close(dict(serializer.validated_data))

            # return object
            ground = self.get_object()
            res = MooringAreaSerializer(ground, context={'request':request})
            cache.delete('campgrounds_dt')
            return Response(res.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e[0]))

    def close_campgrounds(self,closure_data,campgrounds):
        for campground in campgrounds:
            closure_data['campground'] = campground
            try:
                serializer = MooringAreaBookingRangeSerializer(data=closure_data, method="post")
                serializer.is_valid(raise_exception=True)
                instance = MooringArea.objects.get(pk = campground)
                instance.close(dict(serializer.validated_data))
            except Exception as e:
                raise

    @list_route(methods=['post'])
    def bulk_close(self, request, format='json', pk=None):
        with transaction.atomic():
            try:
                http_status = status.HTTP_200_OK
                closure_data = request.data.copy();
                campgrounds = closure_data.pop('campgrounds[]')
                '''Thread for performance / no error messages though'''
                #import thread
                #thread.start_new_thread( self.close_campgrounds, (closure_data,campgrounds,) )
                start = closure_data['range_start'] + " " + closure_data['range_start_time']
                end = closure_data['range_end'] + " " + closure_data['range_end_time']

                data = {
                    'range_start': start,
                    'range_end': end,
                    'reason': closure_data['reason'],
                    'status': closure_data['status'],
                }
                self.close_campgrounds(data,campgrounds)
                cache.delete('campgrounds_dt')
                return Response('All Selected MooringAreas Closed')
            except serializers.ValidationError as e:
                print(traceback.print_exc())
                raise serializers.ValidationError(str(e[0]))
            except Exception as e:
                print(traceback.print_exc())
                raise serializers.ValidationError(str(e[0]))

    def set_periods(self, request, period_data, moorings):
        http_status = status.HTTP_200_OK
        overlap_moorings = []
        for mooring in moorings:
            period_data['mooring'] = mooring
            moor = MooringArea.objects.get(pk=mooring)
            try:
                rate = None
                serializer = RateDetailSerializer(data=period_data)
                serializer.is_valid(raise_exception=True)
                rate_id = serializer.validated_data.get('rate',None)
                if rate_id:
                    try:
                        rate = Rate.objects.get(id=rate_id)
                    except Rate.DoesNotExist as e :
                        raise serializers.ValidationError('The selected rate does not exist')
                else:
                    rate = Rate.objects.get_or_create(mooring=serializer.validated_data['mooring'])[0]

                if rate:
                    try:
                        booking = BookingPeriod.objects.get(pk=serializer.validated_data.get('booking_period_id', None))
                    except BookingPeriod.DoesNotExist as e:
                        raise serializers.ValidationError('The selected booking period does not exist')
                    overlapcheck = self.checkOverrlapDates(moor.id,serializer.validated_data['period_start'], serializer.validated_data['period_end'],None)
                    if overlapcheck is True:
                        overlap_moorings.append(moor.name)
                        continue
                        # raise serializers.ValidationError('Dates overlap existing periods for: ' + moor.name)
                    #MooringAreaPriceHistory.objects.filter() 
                    if booking:
                        period = booking
                    else:
                        period = None
                    serializer.validated_data['rate']=rate
                    data = {
                        'rate': rate,
                        'date_start': serializer.validated_data['period_start'],
                        'date_end': serializer.validated_data['period_end'],
                        'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                        'details': serializer.validated_data.get('details',None),
                        'booking_period': period,
                        'update_level': 0
                    }
                    # This line creates the end date of previous price.

                    moor.createMooringsitePriceHistory(data)

                price_history = MooringAreaPriceHistory.objects.filter(id=moor.id)
                serializer = MooringAreaPriceHistorySerializer(price_history,many=True,context={'request':request})
                res = serializer.data
            except Exception as e:
                raise
        if overlap_moorings == []:
            return Response(res, status=http_status)
        else:
            errorstr = "Dates overlap existing periods for: "
            for i, m in enumerate(overlap_moorings):
                if i != 0:
                    errorstr += ", "
                errorstr += m
            raise ValueError(errorstr)

    @list_route(methods=['post'])
    def bulk_period(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            period_data = request.data.copy();
            moorings = period_data.pop('moorings[]')

            start = period_data['period_start']
            end = period_data['period_end'] if period_data['period_end'] != "" or period_data['period_end'] != " " else None

            data = {
                'period_start': start,
                'booking_period_id': period_data['booking_period'],
                'reason': period_data['reason'],
            }
            if end:
                data['period_end'] = end
            if 'details' in period_data:
                data['details'] = period_data['details']
            else:
                data['details'] = ''

            self.set_periods(request, data, moorings)
            return Response('All Selected MooringAreas Period Updated')
        except Exception as e:
            raise

    def checkOverrlapDates(self,mooring_id,date_start,date_end,exclude_id):

         start_period_count =None
         end_period_count=None
         start_end_within_period=None

         if exclude_id:  
             start_period_count =  MooringAreaPriceHistory.objects.filter(id=mooring_id,date_start__lte=date_start,date_end__gte=date_start).exclude(price_id=exclude_id).count()
             end_period_count = MooringAreaPriceHistory.objects.filter(id=mooring_id,date_start__lte=date_end,date_end__gte=date_end).exclude(price_id=exclude_id).count()
             start_end_within_period = MooringAreaPriceHistory.objects.filter(id=mooring_id,date_start__gte=date_start,date_end__lte=date_end).exclude(price_id=exclude_id).count()
         else:
             start_period_count =  MooringAreaPriceHistory.objects.filter(id=mooring_id,date_start__lte=date_start,date_end__gte=date_start).count()
             end_period_count = MooringAreaPriceHistory.objects.filter(id=mooring_id,date_start__lte=date_end,date_end__gte=date_end).count()
             start_end_within_period = MooringAreaPriceHistory.objects.filter(id=mooring_id,date_start__gte=date_start,date_end__lte=date_end).count()

         if start_period_count > 0 or end_period_count > 0 or start_end_within_period > 0:
            return True
         else:
              return False



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
#                rate = Rate.objects.get_or_create(mooring=serializer.validated_data['mooring'],adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'],infant=serializer.validated_data['infant'])[0]
#                rate = Rate.objects.get_or_create(mooring=serializer.validated_data['mooring'],adult='0.00',concession='0.00',child='0.00',infant='0.00')[0]
                rate = Rate.objects.get_or_create(mooring=serializer.validated_data['mooring'])[0]

            if rate:
                try:
                    booking = BookingPeriod.objects.get(pk=serializer.validated_data.get('booking_period_id', None))
                except BookingPeriod.DoesNotExist as e:
                    raise serializers.ValidationError('The selected booking period does not exist')
                overlapcheck = self.checkOverrlapDates(self.get_object().id,serializer.validated_data['period_start'], serializer.validated_data['period_end'],None)
                if overlapcheck is True:
                     raise serializers.ValidationError('Dates overlap existing periods')
                #MooringAreaPriceHistory.objects.filter() 
                if booking:
                    period = booking
                else:
                    period = None
                serializer.validated_data['rate']=rate
                data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'date_end': serializer.validated_data['period_end'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data.get('details',None),
                    'booking_period': period,
                    'update_level': 0
                }
                # This line creates the end date of previous price.
                self.get_object().createMooringsitePriceHistory(data)

            price_history = MooringAreaPriceHistory.objects.filter(id=self.get_object().id)
            serializer = MooringAreaPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
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
            price_id = request.data.pop('price_id')
            original_serializer = MooringAreaPriceHistorySerializer(data=original_data,method='post')
            original_serializer.is_valid(raise_exception=True)

            serializer = RateDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rate_id = serializer.validated_data.get('rate',None)
            overlapcheck = self.checkOverrlapDates(self.get_object().id,serializer.validated_data['period_start'], serializer.validated_data['period_end'], price_id)
            if overlapcheck is True:
                raise serializers.ValidationError('Dates overlap existing periods')

            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e :
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                #rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'],infant=serializer.validated_data['infant'])[0]
                rate = Rate.objects.get_or_create(mooring=serializer.validated_data['mooring'])[0]
            if rate:
                try:
                    booking = BookingPeriod.objects.get(pk=serializer.validated_data.get('booking_period_id', None))
                except BookingPeriod.DoesNotExist as e:
                    raise serializers.ValidationError('The selected booking period does not exist')
                if booking:
                    period = booking
                else:
                    period = None
                serializer.validated_data['rate']= rate
                new_data = {
                    'rate': rate,
#                    'date_start': serializer.validated_data['period_start'],
                    'date_end': serializer.validated_data['period_end'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data.get('details',None),
                    'booking_period': period,
                    'update_level': 0
                }
                self.get_object().updatePriceHistory(dict(original_serializer.validated_data),new_data)

            price_history = MooringAreaPriceHistory.objects.filter(id=self.get_object().id)
            serializer = MooringAreaPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
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
            serializer = MooringAreaPriceHistorySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            self.get_object().deletePriceHistory(serializer.validated_data)
            price_history = MooringAreaPriceHistory.objects.filter(id=self.get_object().id)
            serializer = MooringAreaPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
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
                serializer = MooringAreaBookingRangeSerializer(self.get_object().booking_ranges.filter(~Q(status=0)).order_by('-range_start'),many=True)
            else:
                serializer = MooringAreaBookingRangeSerializer(self.get_object().booking_ranges,many=True)
            res = serializer.data

            return Response(res,status=http_status)
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
            serializer = MooringsiteSerialiser(self.get_object().campsites,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
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
            price_history = MooringAreaPriceHistory.objects.filter(id=self.get_object().id).order_by('-date_start')
            
            serializer = MooringAreaPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data
            for line in res:
                for k, v in line.items():
                    if k == "booking_period_id":
                        period = BookingPeriod.objects.get(pk=v)
                        line['period_name'] = period.name
            return Response(res,status=http_status)
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
            start = request.GET.get("start",False)
            end = request.GET.get("end",False)
            serializer = None
            if (start) or (end):
                start = datetime.strptime(start,"%Y-%m-%d").date()
                end = datetime.strptime(end,"%Y-%m-%d").date()
                queryset = MooringAreaStayHistory.objects.filter(range_end__range = (start,end), range_start__range=(start,end) ).order_by("range_start")[:5]
                serializer = MooringAreaStayHistorySerializer(queryset,many=True,context={'request':request},method='get')
            else:
                serializer = MooringAreaStayHistorySerializer(self.get_object().stay_history.all().order_by('-range_start'),many=True,context={'request':request},method='get')
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))


    def try_parsing_date(self,text):
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
            campsite_qs = Mooringsite.objects.filter(mooringarea_id=self.get_object().id)
            http_status = status.HTTP_200_OK
            available = utils.get_available_campsites_list(campsite_qs,request, start_date, end_date)

            return Response(available,status=http_status)
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def available_campsites_booking(self, request, format='json', pk=None):
        start_date = self.try_parsing_date(request.GET.get('arrival')).date()
        end_date = self.try_parsing_date(request.GET.get('departure')).date()
        booking_id = request.GET.get('booking',None)

        booking = Booking.objects.get(id=booking_id)
        campsite_qs = Mooringsite.objects.filter(mooringarea_id=self.get_object().id)
#       campsite_qs = Mooringsite.objects.filter(mooringarea_id=4)
        
        http_status = status.HTTP_200_OK
       
        available = utils.get_available_campsites_list_booking(campsite_qs,request, start_date, end_date,booking)
        return Response(available,status=http_status)


        try:
            start_date = self.try_parsing_date(request.GET.get('arrival')).date()
            end_date = self.try_parsing_date(request.GET.get('departure')).date()
            booking_id = request.GET.get('booking',None) 
            if not booking_id:
                raise serializers.ValidationError('Booking has not been defined')
            try:
                booking = Booking.objects.get(id=booking_id)
            except:
                raise serializers.ValiadationError('The booking could not be retrieved')
            campsite_qs = Mooringsite.objects.filter(mooringarea_id=self.get_object().id)
            http_status = status.HTTP_200_OK
            available = utils.get_available_campsites_list_booking(campsite_qs,request, start_date, end_date,booking)
            return Response(available,status=http_status)
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    def available_campsite_classes(self, request, format='json', pk=None):
        try:
            start_date = datetime.strptime(request.GET.get('arrival'),'%Y/%m/%d').date()
            end_date = datetime.strptime(request.GET.get('departure'),'%Y/%m/%d').date()
            http_status = status.HTTP_200_OK
            available = utils.get_available_campsitetypes(self.get_object().id,start_date, end_date,_list=False)
            available_serializers = []
            #for k,v in available.items():
                #s = MooringsiteClassSerializer(MooringsiteClass.objects.get(id=k),context={'request':request},method='get').data
                #s['campsites'] = [c.id for c in v]
                #available_serializers.append(s)
            data = available_serializers

            return Response(data,status=http_status)
        except serializers.ValidationError:
            traceback.print_exc()
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))


class BaseAvailabilityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MooringArea.objects.all()
    serializer_class = MooringAreaSerializer

    def retrieve(self, request, pk=None, ratis_id=None, format=None, show_all=False):
        """Fetch mooring availability."""
        # convert GET parameters to objects
        ground = self.get_object()
        # check if the user has an ongoing booking
        ongoing_booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
        # Validate parameters
        data = {
            "arrival" : request.GET.get('arrival'),
            "departure" : request.GET.get('departure'),
            "num_adult" : request.GET.get('num_adult', 0),
            "num_concession" : request.GET.get('num_concession', 0),
            "num_child" : request.GET.get('num_child', 0),
            "num_infant" : request.GET.get('num_infant', 0),
            "num_mooring" : request.GET.get('num_mooring', 0),
            "gear_type" : request.GET.get('gear_type', 'all'),
            "vessel_size" : request.GET.get('vessel_size', 0),
            "vessel_draft": request.GET.get('vessel_draft', 0)
        }

        serializer = MooringAreaMooringsiteFilterSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data['arrival']
        end_date = serializer.validated_data['departure']
        num_adult = serializer.validated_data['num_adult']
        num_concession = serializer.validated_data['num_concession']
        num_child = serializer.validated_data['num_child']
        num_infant = serializer.validated_data['num_infant']
        num_mooring = serializer.validated_data['num_mooring']
        gear_type = serializer.validated_data['gear_type']
        vessel_size = serializer.validated_data['vessel_size']

        # if campground doesn't support online bookings, abort!
        if ground.mooring_type != 0:
            return Response({'error': 'Mooring doesn\'t support online bookings'}, status=400)
   
        if ground.vessel_size_limit < vessel_size:
             return Response({'name':'   ', 'error': 'Vessel size is too large for mooring', 'error_type': 'vessel_error', 'vessel_size': ground.vessel_size_limit}, status=200)


        #if not ground._is_open(start_date):
        #    return Response({'closed': 'MooringArea is closed for your selected dates'}, status=status.HTTP_400_BAD_REQUEST)

        # get a length of the stay (in days), capped if necessary to the request maximum
        today = date.today()
        length = max(0, (end_date-start_date).days)
        max_advance_booking_days = max(0, (start_date-today).days) 
        #if length > settings.PS_MAX_BOOKING_LENGTH:
        #    length = settings.PS_MAX_BOOKING_LENGTH
        #    end_date = start_date+timedelta(days=settings.PS_MAX_BOOKING_LENGTH)
        
        # Have moved this into Availablity Calander utils.py
        #if max_advance_booking_days > ground.max_advance_booking:
        #   return Response({'name':'   ', 'error': 'Max advanced booking limit is '+str(ground.max_advance_booking)+' day/s. You can not book longer than this period.', 'error_type': 'stay_error', 'max_advance_booking': ground.max_advance_booking, 'days': length, 'max_advance_booking_days': max_advance_booking_days }, status=200 )


        # fetch all the campsites and applicable rates for the campground
        context = {}
        if gear_type != 'all':
            context[gear_type] = True
        sites_qs = Mooringsite.objects.filter(mooringarea=ground).filter(**context)

        # fetch rate map
        rates = {
            siteid: {
                #date: num_adult*info['adult']+num_concession*info['concession']+num_child*info['child']+num_infant*info['infant']
                 date: info['mooring']
                for date, info in dates.items()
            } for siteid, dates in utils.get_visit_rates(sites_qs, start_date, end_date).items()
        }
        # fetch availability map
        availability = utils.get_campsite_availability(sites_qs, start_date, end_date, None, None)
        # create our result object, which will be returned as JSON
        result = {
            'id': ground.id,
            'name': ground.name,
            'long_description': ground.long_description,
            'map': ground.mooring_map.url if ground.mooring_map else None,
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
            'vessel_size' : ground.vessel_size_limit,
            'vessel_draft' : ground.vessel_draft_limit,
            'max_advance_booking': ground.max_advance_booking 
        }

        # group results by campsite class
        if ground.site_type in (1, 2):
            # from our campsite queryset, generate a distinct list of campsite classes
#            classes = [x for x in sites_qs.distinct('campsite_class__name').order_by('campsite_class__name').values_list('pk', 'campsite_class', 'campsite_class__name', 'tent', 'campervan', 'caravan')]
            classes = [x for x in sites_qs.distinct('mooringsite_class__name').order_by('mooringsite_class__name').values_list('pk', 'mooringsite_class', 'mooringsite_class__name', 'tent', 'campervan', 'caravan')]

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
                    'availability': [[True, '${}'.format(rate[start_date+timedelta(days=i)]), rate[start_date+timedelta(days=i)], [0, 0]] for i in range(length)],
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
                classes_map[s.campsite_class.pk]['breakdown'][s.name] = [[True, '${}'.format(rate[start_date+timedelta(days=i)]), rate[start_date+timedelta(days=i)]] for i in range(length)]

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
                    for offset, stat in [((k-start_date).days, v[0]) for k, v in availability[s.pk].items() if v[0] != 'open']:
                        # update the per-site availability
                        classes_map[key]['breakdown'][s.name][offset][0] = False
                        classes_map[key]['breakdown'][s.name][offset][1] = 'Booked' if (stat == 'booked') else 'Unavailable'

                        # update the class availability status
                        book_offset = 0 if (stat == 'booked') else 1
                        classes_map[key]['availability'][offset][3][book_offset] += 1
                        if classes_map[key]['availability'][offset][3][0] == class_sizes[key]:
                            classes_map[key]['availability'][offset][1] = 'Fully Booked'
                        elif classes_map[key]['availability'][offset][3][1] == class_sizes[key]:
                            classes_map[key]['availability'][offset][1] = 'Unavailable'
                        elif classes_map[key]['availability'][offset][3][0] >= classes_map[key]['availability'][offset][3][1]:
                            classes_map[key]['availability'][offset][1] = 'Partially Booked'
                        else:
                            classes_map[key]['availability'][offset][1] = 'Partially Unavailable'

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
                        'availability': [[True, '${}'.format(rate[start_date+timedelta(days=i)]), rate[start_date+timedelta(days=i)], [0, 0]] for i in range(length)],
                        'breakdown': []
                    })


            return Response(result)


        # don't group by class, list individual sites
        else:
            sites_qs = sites_qs.order_by('name')
            # from our campsite queryset, generate a digest for each site
            sites_map = OrderedDict([(s.mooringarea.name, (s.pk, s.mooringsite_class, rates[s.pk], s.tent, s.campervan, s.caravan)) for s in sites_qs])
            bookings_map = {}
            # make an entry under sites for each site
            for k, v in sites_map.items():
                site = {
                    'name': k,
                    'id': v[0],
                    'type': ground.mooring_type,
                    'class': v[1].pk,
                    'price': '${}'.format(sum(v[2].values())) if not show_all else False,
                    'availability': [[True, '${}'.format(v[2][start_date+timedelta(days=i)]), v[2][start_date+timedelta(days=i)]] for i in range(length)],
                    'gearType': {
                        'tent': v[3],
                        'campervan': v[4],
                        'caravan': v[5]
                    }
                }
                result['sites'].append(site)
#                bookings_map[k] = site
                bookings_map[v[0]] = site
                if v[1].pk not in result['classes']:
                    result['classes'][v[1].pk] = v[1].name
            # update results based on availability map
            for s in sites_qs:
               # if there's not a free run of slots
                if (not all([v[0] == 'open' for k, v in availability[s.pk].items()])) or show_all:
                    # update the days that are non-open
                    for offset, stat in [((k-start_date).days, v[0]) for k, v in availability[s.pk].items() if v[0] != 'open']:
                        bookings_map[s.id]['availability'][offset][0] = False
                        if stat == 'closed':
                            bookings_map[s.id]['availability'][offset][1] = 'Unavailable'
                        elif stat == 'booked':
                            bookings_map[s.id]['availability'][offset][1] = 'Unavailable'
                        else:
                            bookings_map[s.id]['availability'][offset][1] = 'Unavailable'

                        bookings_map[s.id]['price'] = False
            return Response(result)



class BaseAvailabilityViewSet2(viewsets.ReadOnlyModelViewSet):
    queryset = MooringArea.objects.all()
    serializer_class = MooringAreaSerializer

    def distance(self,origin, destination):
         lat1, lon1 = origin
         lat2, lon2 = destination
         radius = 6371 # km

         dlon = lon2 - lon1
         dlat = lat2 - lat1
         a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2
         c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
         distance = radius * c / 100 * 1.60934

         return distance

    def distance_meters(self,origin, destination):
         lat1, lon1 = origin
         lat2, lon2 = destination
         radius = 6372800 # meters 

         dlon = lon2 - lon1
         dlat = lat2 - lat1
         a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2
         c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
         distance = radius * c / 100 * 1.60934

         return distance

    def retrieve(self, request, pk=None, ratis_id=None, format=None, show_all=False):
        """Fetch full mooring availability."""

        # convert GET parameters to objects
        ground = self.get_object()
        # check if the user has an ongoing booking
        ongoing_booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
        timer = None
        expiry = None
        if ongoing_booking:
            #expiry_time = ongoing_booking.expiry_time
            timer = (ongoing_booking.expiry_time-timezone.now()).seconds if ongoing_booking else -1
            expiry = ongoing_booking.expiry_time.isoformat() if ongoing_booking else ''
        distance_radius = request.GET.get('distance_radius', 0)
        # Validate parameters
        data = {
            "arrival" : request.GET.get('arrival'),
            "departure" : request.GET.get('departure'),
            "num_adult" : request.GET.get('num_adult', 0),
            "num_concession" : request.GET.get('num_concession', 0),
            "num_child" : request.GET.get('num_child', 0),
            "num_infant" : request.GET.get('num_infant', 0),
            # "gear_type" : request.GET.get('gear_type', 'all'),
            "vessel_size" : request.GET.get('vessel_size', 0),
            "vessel_draft" : request.GET.get('vessel_draft', 0),
            "vessel_beam" : request.GET.get('vessel_beam', 0),
            "vessel_weight" : request.GET.get('vessel_weight', 0),
            "vessel_rego" : request.GET.get('vessel_rego', 0)
#            "distance_radius" : request.GET.get('distance_radius', 0)
        }
        serializer = MooringAreaMooringsiteFilterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        start_date = serializer.validated_data['arrival']
        end_date = serializer.validated_data['departure']
        num_adult = serializer.validated_data['num_adult']
        num_concession = serializer.validated_data['num_concession']
        num_child = serializer.validated_data['num_child']
        num_infant = serializer.validated_data['num_infant']
        # gear_type = serializer.validated_data['gear_type']
        vessel_size = serializer.validated_data['vessel_size']
        vessel_draft = serializer.validated_data['vessel_draft']
        vessel_beam = serializer.validated_data['vessel_beam']
        vessel_weight = serializer.validated_data['vessel_weight']
        vessel_rego = serializer.validated_data['vessel_rego']
        # distance_radius = serializer.validated_data['distance_radius']

        if ongoing_booking:
            if not ongoing_booking.details:
                ongoing_booking.details={}
            ongoing_booking.details['num_adult'] = num_adult
            ongoing_booking.details['num_child'] = num_child
            ongoing_booking.details['num_infant'] = num_infant
            ongoing_booking.details['num_concession'] = num_concession
            ongoing_booking.details['vessel_size'] = vessel_size
            ongoing_booking.details['vessel_draft'] = vessel_draft
            ongoing_booking.details['vessel_beam'] = vessel_beam
            ongoing_booking.details['vessel_weight'] = vessel_weight
            ongoing_booking.details['vessel_rego'] = vessel_rego
            ongoing_booking.save()
        

        # if campground doesn't support online bookings, abort!
        if ground.mooring_type != 0:
            return Response({'error': 'Mooring doesn\'t support online bookings'}, status=400)

        #if ground.vessel_size_limit < vessel_size:
        #     return Response({'name':'   ', 'error': 'Vessel size is too large for mooring', 'error_type': 'vessel_error', 'vessel_size': ground.vessel_size_limit}, status=200 )


        #if not ground._is_open(start_date):
        #    return Response({'closed': 'MooringArea is closed for your selected dates'}, status=status.HTTP_400_BAD_REQUEST)

        # get a length of the stay (in days), capped if necessary to the request maximum
        today = date.today()
        #end_date =end_date  + timedelta(days=1)
        length = max(0, (end_date-start_date).days)
        max_advance_booking_days = max(0, (start_date-today).days)

        #if length > settings.PS_MAX_BOOKING_LENGTH:
        #    length = settings.PS_MAX_BOOKING_LENGTH
        #    end_date = start_date+timedelta(days=settings.PS_MAX_BOOKING_LENGTH)
        #### # Have moved this into Availablity Calander utils.py
        #if max_advance_booking_days > ground.max_advance_booking:
        #   return Response({'name':'   ', 'error': 'Max advanced booking limit is '+str(ground.max_advance_booking)+' day/s. You can not book longer than this period.', 'error_type': 'stay_error', 'max_advance_booking': ground.max_advance_booking, 'days': length, 'max_advance_booking_days': max_advance_booking_days }, status=200 )


        # fetch all the campsites and applicable rates for the campground
        context = {}
        #gear type is for parkstay, remvoed for now.
        # if gear_type != 'all':
        #     context[gear_type] = True
#        sites_qs = Mooringsite.objects.filter(mooringarea=ground).filter(**context)
#        radius = int(distance_radius)

        radius = int(1)
        if float(distance_radius) > 0:
            radius = float(distance_radius)
#       sites_qs = Mooringsite.objects.all().filter(**context)
        sites_qs = []
  #      if request.session['ps_booking_old']:
#            sites_qs = Mooringsite.objects.filter(mooringarea__wkb_geometry__distance_lt=(ground.wkb_geometry, Distance(km=radius))).filter(**context).exclude()
 #       else:
#        sites_qs = Mooringsite.objects.filter(mooringarea__vessel_size_limit__gte=vessel_size, 
#                                              mooringarea__vessel_draft_limit__gte=vessel_draft,
#                                              mooringarea__vessel_beam_limit__gte=vessel_beam,
#                                              mooringarea__vessel_weight_limit__gte=vessel_weight,
#                                              mooringarea__wkb_geometry__distance_lt=(ground.wkb_geometry, Distance(km=radius)))
#
        sites_qs = Mooringsite.objects.filter(mooringarea__vessel_size_limit__gte=vessel_size,
                                              mooringarea__vessel_draft_limit__gte=vessel_draft,
                                              mooringarea__wkb_geometry__distance_lt=(ground.wkb_geometry, Distance(km=radius)))

        #.filter(**context)

        # # If the pen type has been included in filtering and is not 'all' then loop through the sites selected.
        # if pen_type != 'all':
        #     sites = Mooringsite.objects.filter(pk__in=sites_qs)
        #     for s in sites:           
        #     # When looping through, if the pen type is not correct, remove it from the list.
        #         i = s.mooringarea
        #         if i.mooring_physical_type != pen_type:
        #             sites_qs = sites_qs.exclude(pk=s.id)


        # fetch rate map
        rates = {
            siteid: {
                #date: num_adult*info['adult']+num_concession*info['concession']+num_child*info['child']+num_infant*info['infant']
#                 date: info['mooring']
                 date: info
                 #booking_period: info['booking_period'],
                for date, info in dates.items()
            } for siteid, dates in utils.get_visit_rates(sites_qs, start_date, end_date).items()
        }

  

        #for siteid, dates in utils.get_visit_rates(sites_qs, start_date, end_date).items():
        # fetch availability map

        cb = get_current_booking(ongoing_booking, request)
        current_booking = cb['current_booking']
        total_price = cb['total_price']


#        ms_booking = MooringsiteBooking.objects.filter(booking=ongoing_booking)
#        current_booking = []
#        total_price = Decimal('0.00')
#        for ms in ms_booking:
#           row = {}
#           row['id'] = ms.id
#           #print ms.from_dt.astimezone(pytimezone('Australia/Perth'))
#           row['item'] = ms.campsite.name + ' from '+ms.from_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%y %H:%M %p')+' to '+ms.to_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%y %H:%M %p')
#           row['amount'] = str(ms.amount)
##           row['item'] = ms.campsite.name
#           total_price = total_price +ms.amount
#           current_booking.append(row)
        booking_changed = True

        if ongoing_booking:
             # When changing a book this check for changes
             if ongoing_booking.old_booking is not None:
             
                 current_booking_obj = MooringsiteBooking.objects.filter(booking=ongoing_booking).values('campsite','from_dt','to_dt','booking_period_option')
                 old_booking_obj = MooringsiteBooking.objects.filter(booking=ongoing_booking.old_booking).values('campsite','from_dt','to_dt','booking_period_option')
                 # compare old and new booking for changes
                 if hashlib.md5(str(current_booking_obj)).hexdigest() == hashlib.md5(str(old_booking_obj)).hexdigest():
                       booking_changed = False
                 if utils.check_mooring_admin_access(request) is True:
                       booking_changed = True
                      
        availability = utils.get_campsite_availability(sites_qs, start_date, end_date, ongoing_booking, request)

        # create our result object, which will be returned as JSON
        result = {
            'id': ground.id,
            'name': ground.name,
            'long_description': ground.long_description,
            'map': ground.mooring_map.url if ground.mooring_map else None,
            'ongoing_booking': True if ongoing_booking else False,
            'ongoing_booking_id': ongoing_booking.id if ongoing_booking else None,
            'booking_changed': booking_changed,
            'expiry': expiry,
            'timer': timer,
            'current_booking': current_booking,
            'total_booking': str(total_price),
            'arrival': start_date.strftime('%Y/%m/%d'),
            'days': length,
            'adults': num_adult,
            'children': num_child,
            'infants' : num_infant,
            'maxAdults': 30,
            'maxChildren': 30,
            'sites': [],
            'classes': {},
            'vessel_size' : ground.vessel_size_limit,
            'max_advance_booking': ground.max_advance_booking
        }
        
        # group results by campsite class
        if ground.site_type in (1, 2):
            # from our campsite queryset, generate a distinct list of campsite classes
#            classes = [x for x in sites_qs.distinct('campsite_class__name').order_by('campsite_class__name').values_list('pk', 'campsite_class', 'campsite_class__name', 'tent', 'campervan', 'caravan')]
            classes = [x for x in sites_qs.distinct('mooringsite_class__name').order_by('mooringsite_class__name').values_list('pk', 'mooringsite_class', 'mooringsite_class__name', 'tent', 'campervan', 'caravan')]

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
                    'availability': [[True, '${}'.format(rate[start_date+timedelta(days=i)]), rate[start_date+timedelta(days=i)], [0, 0]] for i in range(length)],
                    'availability2' : [],
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
                classes_map[s.campsite_class.pk]['breakdown'][s.name] = [[True, '${}'.format(rate[start_date+timedelta(days=i)]), rate[start_date+timedelta(days=i)]] for i in range(length)]

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
                    for offset, stat in [((k-start_date).days, v[0]) for k, v in availability[s.pk].items() if v[0] != 'open']:
                        # update the per-site availability
                        classes_map[key]['breakdown'][s.name][offset][0] = False
                        classes_map[key]['breakdown'][s.name][offset][1] = 'Booked' if (stat == 'booked') else 'Unavailable'

                        # update the class availability status
                        book_offset = 0 if (stat == 'booked') else 1
                        classes_map[key]['availability'][offset][3][book_offset] += 1
                        if classes_map[key]['availability'][offset][3][0] == class_sizes[key]:
                            classes_map[key]['availability'][offset][1] = 'Fully Booked'
                        elif classes_map[key]['availability'][offset][3][1] == class_sizes[key]:
                            classes_map[key]['availability'][offset][1] = 'Unavailable'
                        elif classes_map[key]['availability'][offset][3][0] >= classes_map[key]['availability'][offset][3][1]:
                            classes_map[key]['availability'][offset][1] = 'Partially Booked'
                        else:
                            classes_map[key]['availability'][offset][1] = 'Partially Unavailable'

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
                        'availability': [[True, '${}'.format(rate[start_date+timedelta(days=i)]), rate[start_date+timedelta(days=i)], [0, 0]] for i in range(length)],
                        'breakdown': []
                    })


            return Response(result)


        # don't group by class, list individual sites
        else:
            sites_qs = sites_qs.order_by('name')
            
            # from our campsite queryset, generate a digest for each site
            sites_map = OrderedDict([(s, (s.pk, s.mooringsite_class, rates[s.pk], s.tent, s.campervan, s.caravan)) for s in sites_qs])
            #for s in sites_map:
            #     print s
            bookings_map = {}
            # make an entry under sites for each site
            for k, v in sites_map.items():
                distance_from_selection = round(self.distance(ground.wkb_geometry,k.mooringarea.wkb_geometry),2)
                distance_from_selection_meters = round(self.distance_meters(ground.wkb_geometry,k.mooringarea.wkb_geometry),0)
                availability_map = []
                date_rotate = start_date
                for i in range(length):
                     bp_new = []
                     date_rotate = start_date+timedelta(days=i)
                     avbp_map = None
                     if date_rotate in availability[v[0]]:
                         avbp_map = availability[v[0]][date_rotate][1]
                         avbp_map2 = availability[v[0]][date_rotate][2]
                     #[start_date+timedelta(days=i)]
                     for bp in v[2][date_rotate]['booking_period']:
                         bp['status'] = 'open'
                         bp['date'] = str(date_rotate)
                            
                         if avbp_map:
                            if bp['id'] in avbp_map:
                               bp['status'] = avbp_map[bp['id']]
                               bp['booking_row_id'] = avbp_map2[bp['id']]
                               bp['past_booking'] = False
                        
                               #if date_rotate <= datetime.now().date():
                               #   bp['past_booking'] = True
                               bp_dt = datetime.strptime(str(bp['date'])+' '+str(bp['start_time']), '%Y-%m-%d %H:%M:%S')
                               if bp_dt <= datetime.now():
                                  if bp_dt.date() == datetime.now().date():
                                      if ongoing_booking:
                                           if ongoing_booking.old_booking is None:
                                               pass
                                           else:
                                               bp['past_booking'] = True
                                      else:
                                          pass
                                  else:
                                     bp['past_booking'] = True

 
                         bp_new.append(bp)
                         # Close everything thats in the past 
                         # if datetime.strptime(str(date_rotate), '%Y-%m-%d') <= datetime.now():
                         #      bp['status'] = 'closed'
                         
                     v[2][date_rotate]['booking_period'] = bp_new
 
                     availability_map.append([True, v[2][date_rotate], v[2][date_rotate]])
                     #date_rotate = start_date+timedelta(days=i)
#                print availability_map
                
                #print [v[2][start_date+timedelta(days=i)]['mooring'] for i in range(length)]
#                k.mooringarea.vessel_beam_limit = 10000000
                if k.mooringarea.mooring_physical_type == 0:
                    vessel_beam_limit = 1000000
                else:
                    vessel_beam_limit = k.mooringarea.vessel_beam_limit

                if k.mooringarea.mooring_physical_type == 1 or k.mooringarea.mooring_physical_type == 2:
                    vessel_weight_limit = 1000000
                else:
                    vessel_weight_limit = k.mooringarea.vessel_weight_limit

                site = {
                    'name': k.mooringarea.name,
                    'mooring_class' : k.mooringarea.mooring_class,
                    'mooring_park': k.mooringarea.park.name,
                    'id': v[0],
                    'mooring_id': k.mooringarea.id,
                    'type': ground.mooring_type,
                    'class': v[1].pk,
                    'price' : '0.00',
                    'distance_from_selection': distance_from_selection,
                    'distance_from_selection_meters': distance_from_selection_meters,
                    'availability': availability_map,
                    'gearType': {
                        'tent': v[3],
                        'campervan': v[4],
                        'caravan': v[5]
                    },
                    'vessel_size_limit': k.mooringarea.vessel_size_limit,
                    'vessel_draft_limit': k.mooringarea.vessel_draft_limit,
                    'vessel_beam_limit': vessel_beam_limit,
                    'vessel_weight_limit': vessel_weight_limit
                }

                showmooring = True
                if vessel_size > 0: 
                    if k.mooringarea.vessel_size_limit >= vessel_size:
                          pass
                    else:
                       showmooring = False

                if vessel_draft > 0:
                    if k.mooringarea.vessel_draft_limit >= vessel_draft:
                          pass
                    else:
                       showmooring = False

                if vessel_beam > 0:
                    if vessel_beam_limit >= vessel_beam:
                          pass
                    else:
                       showmooring = False
                if vessel_weight > 0:
                    if vessel_weight_limit >= vessel_weight:
                          pass
                    else:
                       showmooring = False

                if showmooring == True:
                   result['sites'].append(site)
                   bookings_map[k.id] = site

                if v[1].pk not in result['classes']:
                    result['classes'][v[1].pk] = v[1].name
            # update results based on availability map
            result['sites'] =  sorted(result['sites'], key = lambda i: i['distance_from_selection']) 
            return Response(result)





class AvailabilityViewSet(BaseAvailabilityViewSet):
    permission_classes = []

class AvailabilityViewSet2(BaseAvailabilityViewSet2):
    permission_classes = []

class AvailabilityRatisViewSet(BaseAvailabilityViewSet):
    permission_classes = []
    lookup_field = 'ratis_id'

class AvailabilityAdminViewSet(BaseAvailabilityViewSet):
    def retrieve(self, request, *args, **kwargs):
        return super(AvailabilityAdminViewSet, self).retrieve(request, *args, show_all=True, **kwargs)

@csrf_exempt
@require_http_methods(['POST'])
def create_admissions_booking(request, *args, **kwargs):

    location_text = request.POST.get('location')
    location = AdmissionsLocation.objects.filter(key=location_text)[0]

    data = {
        'vesselRegNo': request.POST.get('vesselReg'),
        'noOfAdults': request.POST.get('noOfAdults', 0),
        'noOfConcessions': request.POST.get('noOfConcessions', 0),
        'noOfChildren': request.POST.get('noOfChildren', 0),
        'noOfInfants': request.POST.get('noOfInfants', 0),
        'warningReferenceNo': request.POST.get('warningRefNo'),
        'location' : location.pk
    }

    if len(request.POST.get('vesselReg', '')) > 0: 
        pass
    else:
        return HttpResponse(geojson.dumps({
            'status': 'failure',
            'error': (None,"Please enter a vessel registration")
        }), content_type='application/json')


    serializer = AdmissionsBookingSerializer(data=data)
    serializer.is_valid(raise_exception=True)

 

    admissionsBooking = AdmissionsBooking.objects.create(
        vesselRegNo = serializer.validated_data['vesselRegNo'],
        noOfAdults = serializer.validated_data['noOfAdults'],
        noOfConcessions = serializer.validated_data['noOfConcessions'],
        noOfChildren = serializer.validated_data['noOfChildren'],
        noOfInfants = serializer.validated_data['noOfInfants'],
        warningReferenceNo = serializer.validated_data['warningReferenceNo'],
        booking_type = 3,
        location = serializer.validated_data['location']
    )

    data2 = {
        'arrivalDate' : request.POST.get('arrival'),
        'admissionsBooking' : admissionsBooking.pk,
        'location' : location.pk
    }
    
    if(request.POST.get('overnightStay') == 'yes'):
        data2['overnightStay'] = 'True'
    else:
        data2['overnightStay'] = 'False'
    dateAsString = data2['arrivalDate']
    data2['arrivalDate'] = datetime.strptime(dateAsString, "%Y/%m/%d").date()
    
    serializer2 = AdmissionsLineSerializer(data=data2)
    serializer2.is_valid(raise_exception=True)

    admissionsLine = AdmissionsLine.objects.create(
        arrivalDate = serializer2.validated_data['arrivalDate'],
        overnightStay = serializer2.validated_data['overnightStay'],
        admissionsBooking = admissionsBooking,
        location=serializer2.validated_data['location']
    )

    #Lookup price and set lines.
    lines = []
    try:
        lines = utils.admissions_price_or_lineitems(request, admissionsBooking)
    except Exception as e:
        error = (None, '{} Please contact Marine Park and Visitors services with this error message and the time of the request.'.format(str(e)))
        return HttpResponse(geojson.dumps({
            'status': 'failure',
            'error': error
        }), content_type='application/json')
        #handle
    total = sum([decimal.Decimal(p['price_incl_tax'])*p['quantity'] for p in lines])

    
    #Lookup customer
    if request.user.is_anonymous() or request.user.is_staff:
        try:
            customer = EmailUser.objects.get(email=request.POST.get('email'))
        except EmailUser.DoesNotExist:
            customer = EmailUser.objects.create(
                    email=request.POST.get('email'),
                    first_name=request.POST.get('givenName'),
                    last_name=request.POST.get('lastName')
            )
    else:
        customer = request.user 
    

    admissionsBooking.customer = customer
    admissionsBooking.totalCost = total
    admissionsBooking.created_by = None
    if request.user.__class__.__name__ == 'EmailUser':
        admissionsBooking.created_by = request.user
        
    admissionsBooking.save()
    admissionsLine.cost = total
    admissionsLine.save()

    request.session['ad_booking'] = admissionsBooking.pk
    logger = logging.getLogger('booking_checkout')
    logger.info('{} built admissions booking {} and handing over to payment gateway'.format('User {} with id {}'.format(admissionsBooking.customer.get_full_name(),admissionsBooking.customer.id) if admissionsBooking.customer else 'An anonymous user',admissionsBooking.id))

    # generate invoice
    invoice = u"Invoice for {} on {}".format(
            u'{} {}'.format(admissionsBooking.customer.first_name, admissionsBooking.customer.last_name),
            admissionsLine.arrivalDate.strftime('%d-%m-%Y')
    )
    #Not strictly needed.
    #logger.info('{} built booking {} and handing over to payment gateway'.format('User {} with id {}'.format(admissionsBooking.customer.get_full_name(),admissionsBooking.customer.id) if admissionsBooking.customer else 'An anonymous user',admissionsBooking.id))
    # if request.user.is_staff:
    #     result = utils.admissionsCheckout(request, admissionsBooking, lines, invoice_text=invoice, internal=True)
    # else:
    try:
        result = utils.admissionsCheckout(request, admissionsBooking, lines, invoice_text=invoice)
    except Exception as e:
        return HttpResponse(geojson.dumps({
           'status': 'failure',
           'error':  ['',str(e)]
        }), content_type='application/json')
    if(result):
        return result
    else:
        return HttpResponse(geojson.dumps({
            'status': 'failure',
        }), content_type='application/json')

@csrf_exempt
@require_http_methods(['POST'])
def create_booking(request, *args, **kwargs):
    """Create a temporary booking and link it to the current session"""
    data = {
        'arrival': request.POST.get('arrival'),
        'departure': request.POST.get('departure'),
        'num_adult': int(request.POST.get('num_adult', 0)),
        'num_concession': int(request.POST.get('num_concession', 0)),
        'num_child': int(request.POST.get('num_child', 0)),
        'num_infant': int(request.POST.get('num_infant', 0)),
        'num_mooring' : int(request.POST.get('num_mooring', 0)),
        'campground': int(request.POST.get('campground', 0)),
        'campsite_class': int(request.POST.get('campsite_class', 0)),
        'campsite': int(request.POST.get('campsite', 0)),
        'vessel_size' : int(request.POST.get('vessel_size', 0))
    }
    serializer = MooringsiteBookingSerializer(data=data)
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
    num_mooring = serializer.validated_data['num_mooring']
    vessel_size = serializer.validated_data['vessel_size']

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
        campsite_obj = Mooringsite.objects.prefetch_related('mooringarea').get(pk=campsite)
        if campsite_obj.mooringarea.site_type != 0:
            return HttpResponse(geojson.dumps({
                'status': 'error',
                'msg': 'MooringArea doesn\'t support per-site bookings.'
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
                Mooringsite.objects.filter(id=campsite), start_date, end_date,
                num_adult, num_concession,
                num_child, num_infant,
                num_mooring, vessel_size
            )
        else:
            booking = utils.create_booking_by_class(
                campground, campsite_class,
                start_date, end_date,
                num_adult, num_concession,
                num_child, num_infant,
                num_mooring, vessel_size
            )
    except ValidationError as e:
        if hasattr(e,'error_dict'):
            error = repr(e.error_dict)
        else:
            error = {'error':str(e)}
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
def get_admissions_confirmation(request, *args, **kwargs):

    context_processor = template_context(request)
    # fetch booking for ID
    booking_id = kwargs.get('booking_id', None)
    if (booking_id is None):
        return HttpResponse('Booking ID not specified', status=400)
    
    try:
        booking = AdmissionsBooking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return HttpResponse('Booking unavailable', status=403)

    # check permissions
    if not ((request.user == booking.customer) or is_officer(request.user) or (booking.id == request.session.get('ad_last_booking', None))):
        return HttpResponse('Booking unavailable', status=403)

    # check payment status
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="confirmation-AD{}.pdf"'.format(booking_id)

    pdf.create_admissions_confirmation(response, booking,context_processor)
    return response

@require_http_methods(['GET'])
def get_confirmation(request, *args, **kwargs):

    # Get branding configuration
    context_processor = template_context(request)
    # fetch booking for ID
    booking_id = kwargs.get('booking_id', None)
    if (booking_id is None):
        return HttpResponse('Booking ID not specified', status=400)
    
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return HttpResponse('Booking unavailable', status=403)

    try:
        mooring_bookings = MooringsiteBooking.objects.filter(booking=booking).order_by('from_dt')
    except MooringsiteBooking.DoesNotExist:
        return HttpResponse('Mooringsite Booking unavailable', status=403)

    # check permissions
    if not ((request.user == booking.customer) or is_officer(request.user) or (booking.id == request.session.get('ps_last_booking', None))):
        return HttpResponse('Booking unavailable', status=403)

    # check payment status
    if (not is_officer(request.user)) and (not booking.paid):
        return HttpResponse('Booking unavailable', status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="confirmation-PS{}.pdf"'.format(booking_id)

    response.write(pdf.create_confirmation(response, booking, mooring_bookings, context_processor))
    return response


class PromoAreaViewSet(viewsets.ModelViewSet):
    queryset = PromoArea.objects.all()
    serializer_class = PromoAreaSerializer

class MarinaViewSet(viewsets.ModelViewSet):
    queryset = MarinePark.objects.all()
    serializer_class = MarinaSerializer

    def list(self, request, *args, **kwargs):
        data = cache.get('parks')
        data = None
        if data is None:
            groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
            qs = self.get_queryset()
            mooring_groups = []
            for group in groups:
                mooring_groups.append(group.id)
            queryset = qs.filter(mooring_group__in =mooring_groups)
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set('parks',data,3600)
        return Response(data)

    @list_route(methods=['get'])
    def price_history(self, request, format='json', pk=None):
        http_status = status.HTTP_200_OK
        try:
            price_history = MarinaEntryRate.objects.all().order_by('-period_start')
            serializer = MarinaEntryRateSerializer(price_history,many=True,context={'request':request},method='get')
            res = serializer.data
        except Exception as e:
            res ={
                "Error": str(e)
            }

        return Response(res,status=http_status)

    @detail_route(methods=['get'])
    def current_price(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            start_date = request.GET.get('arrival',False)
            res = []
            if start_date:
                start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
                price_history = MarinaEntryRate.objects.filter(period_start__lte = start_date).order_by('-period_start')
                if price_history:
                    serializer = MarinaEntryRateSerializer(price_history,many=True,context={'request':request})
                    res = serializer.data[0]

        except Exception as e:
            res ={
                "Error": str(e)
            }
        return Response(res,status=http_status)

    @list_route(methods=['post'],)
    def add_price(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            serializer =  MarinaEntryRateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = serializer.data
            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer

class MarinaEntryRateViewSet(viewsets.ModelViewSet):
    queryset = MarinaEntryRate.objects.all()
    serializer_class = MarinaEntryRateSerializer

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class MooringGroup(viewsets.ModelViewSet):
    queryset = MooringAreaGroup.objects.all()
    serializer_class = MooringAreaGroupSerializer

    def list(self, request, *args, **kwargs):
        groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)

class MooringsiteClassViewSet(viewsets.ModelViewSet):
    queryset = MooringsiteClass.objects.all()
    serializer_class = MooringsiteClassSerializer

    def list(self, request, *args, **kwargs):
        active_only = bool(request.GET.get('active_only',False))
        if active_only:
            queryset = MooringsiteClass.objects.filter(deleted=False)
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
            price_history = MooringsiteClassPriceHistory.objects.filter(id=self.get_object().id).order_by('-date_start')
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
            serializer = MooringsiteClassPriceHistorySerializer(fixed_list,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
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
            rate_id = serializer.validated_data.get('rate',None)
            if rate_id:
                try:
                    rate = Rate.objects.get(id=rate_id)
                except Rate.DoesNotExist as e :
                    raise serializers.ValidationError('The selected rate does not exist')
            else:
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'],infant=serializer.validated_data['infant'])[0]
            if rate:
                serializer.validated_data['rate']= rate
                data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data.get('details',None),
                    'update_level': 1
                }
                self.get_object().createMooringsitePriceHistory(data)
            price_history = MooringAreaPriceHistory.objects.filter(id=self.get_object().id)
            serializer = MooringAreaPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
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

            original_serializer = MooringAreaPriceHistorySerializer(data=original_data)
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
                rate = Rate.objects.get_or_create(adult=serializer.validated_data['adult'],concession=serializer.validated_data['concession'],child=serializer.validated_data['child'],infant=serializer.validated_data['infant'])[0]
            if rate:
                serializer.validated_data['rate']= rate
                new_data = {
                    'rate': rate,
                    'date_start': serializer.validated_data['period_start'],
                    'date_end' : serializer.validated_data['period_end'],
                    'reason': PriceReason.objects.get(pk=serializer.validated_data['reason']),
                    'details': serializer.validated_data.get('details',None),
                    'update_level': 1
                }
                self.get_object().updatePriceHistory(dict(original_serializer.validated_data),new_data)
            price_history = MooringAreaPriceHistory.objects.filter(id=self.get_object().id)
            serializer = MooringAreaPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
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
            serializer = MooringAreaPriceHistorySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            self.get_object().deletePriceHistory(serializer.validated_data)
            price_history = MooringAreaPriceHistory.objects.filter(id=self.get_object().id)
            serializer = MooringAreaPriceHistorySerializer(price_history,many=True,context={'request':request})
            res = serializer.data

            return Response(res,status=http_status)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

class AdmissionsBookingViewSet(viewsets.ModelViewSet):
    queryset = AdmissionsBooking.objects.all()
    serializer_class = AdmissionsBookingSerializer

    def list(self, request, *args, **kwargs):
        http_status = status.HTTP_200_OK
        recordsTotal = None
        recordsFiltered = None
        res = None
        canceled = request.GET.get('canceled','False')
        #bt = [0,1]
        #if canceled == str('True'):
        #   bt = [0,1,4]
        bt = [0,1,4]
        recordsTotal = 0
        data = []
        data_temp = None
        try:
            data_temp = AdmissionsBooking.objects.filter(booking_type__in=bt).order_by('-pk')
            groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
            # If groups then we need to filter data by groups.
            if groups.count() > 0:
                filtered_ids = []
                for rec in data_temp:
                    bookings = Booking.objects.filter(admission_payment=rec)
                    if bookings.count() > 0:
                        booking = bookings[0]
                        msbs = MooringsiteBooking.objects.filter(booking=booking)
                        in_group = False
                        moorings = []
                        for group in groups:
                            for mooring in group.moorings.all():
                                moorings.append(mooring)
                        for msb in msbs:
                            if msb.campsite.mooringarea in moorings:
                                in_group = True
                                break
                        if in_group:
                            #filtered_ids.append(rec.id)
                            pass
                            if canceled == str('True'):
                               if rec.booking_type == 4:
                                  data.append(rec)
                            else:
                                if rec.booking_type == 0 or rec.booking_type == 1:
                                  data.append(rec)
                            recordsTotal = recordsTotal  + 1
                    else:
                        ad_line = AdmissionsLine.objects.filter(admissionsBooking=rec).first()
                        if ad_line:
                            if ad_line.location.mooring_group in groups:
                                if canceled == str('True'):
                                   if rec.booking_type == 4:
                                      data.append(rec)
                                else:
                                   if rec.booking_type == 0 or rec.booking_type == 1:
                                      data.append(rec)
 
                                recordsTotal = recordsTotal  + 1
                                #data.append(rec)
                                pass
                                #filtered_ids.append(rec.id)

                #data = AdmissionsBooking.objects.filter(pk__in=filtered_ids).order_by('-pk')
            else:
                return Response("Error no group")

            
#            recordsTotal = len(data)
#            recordsTotal = AdmissionsBooking.objects.filter(booking_type__in=[0,1,4],`
            #search = request.GET.get('search[value]') if request.GET.get('search[value]') else None
            search = request.GET.get('search_keyword') if request.GET.get('search_keyword') else None
            start = request.GET.get('start') if request.GET.get('start') else 0
            length = request.GET.get('length') if request.GET.get('length') else len(data)
            date_from = datetime.strptime(request.GET.get('arrival'),'%d/%m/%Y').date() if request.GET.get('arrival') else None
            date_to = datetime.strptime(request.GET.get('departure'),'%d/%m/%Y').date() if request.GET.get('departure') else None
            data2 = []
            data_temp = []
            if search:
                #if(search.upper().startswith('AD')):
                #    try:
                #        int(search[2:])
                #        search = search[2:]
                #    except:
                #        pass
                for row in data:
                     if row.warningReferenceNo.lower().find(search.lower()) >= 0 or row.customer.first_name.lower().find(search.lower()) >= 0 or row.customer.first_name.lower().find(search.lower()) >= 0 or row.vesselRegNo.lower().find(search.lower()) >= 0 or str(row.id) == search or str(row.customer.first_name.lower()+' '+row.customer.last_name.lower()).find(search.lower()) >= 0 or 'AD'+str(row.id) == search:
                          data_temp.append(row)
                     data = data_temp
                #data = data.filter(Q(warningReferenceNo__icontains=search) | Q(vesselRegNo__icontains=search) | Q(customer__first_name__icontains=search) | Q(customer__last_name__icontains=search) | Q(id__icontains=search))
            if date_from and date_to:
                data_temp = []
                for row in data:
                      date_match = False
                      for row_line in row.admissions_line:
                          if row_line.arrivalDate >= date_from and row_line.arrivalDate <= date_to:
                               date_match = True

                      if date_match is True:
                           data_temp.append(row)
                data = data_temp
#                data = data.distinct().filter(admissionsline__arrivalDate__gte=date_from, admissionsline__arrivalDate__lte=date_to)
            elif(date_from):
                data_temp = []
                for row in data:
                      date_match = False
                      for row_line in row.admissions_line:
                          if row_line.arrivalDate >= date_from:
                               date_match = True

                      if date_match is True:
                           data_temp.append(row)
                data = data_temp

            #    data = data.distinct().filter(admissionsline__arrivalDate__gte=date_from)
            elif(date_to):
                data_temp = []
                for row in data:
                      date_match = False
                      for row_line in row.admissions_line:
                          if row_line.arrivalDate <= date_to:
                               date_match = True

                      if date_match is True:
                           data_temp.append(row)
                data = data_temp

            #    data = data.distinct().filter(admissionsline__arrivalDate__lte=date_to)
            recordsFiltered = int(len(data))
            data = data[int(start):int(length)+int(start)]
            serializer = AdmissionsBookingSerializer(data,many=True)
            res = serializer.data
            for r in res:
                ad = AdmissionsBooking.objects.get(pk=r['id'])
                adLines = AdmissionsLine.objects.filter(admissionsBooking=ad)
                lines = []
                for line in adLines:
                    lines.append({'date' : line.arrivalDate, 'overnight': line.overnightStay})
                if adLines and lines != []:
                    r.update({'lines' : lines})
                if Booking.objects.filter(admission_payment=ad).count() > 0:
                    booking = Booking.objects.filter(admission_payment=ad)[0]
                    r.update({'booking': booking.id})
                    bi = BookingInvoice.objects.filter(booking=booking)
                    inv = []
                    for b in bi:
                        inv.append(b.invoice_reference)
                else:
                    adi = AdmissionsBookingInvoice.objects.filter(admissions_booking=ad)
                    inv = []
                    for i in adi:
                       inv.append(i.invoice_reference)
#                    inv = AdmissionsBookingInvoice.objects.filter(admissions_booking=ad)
#                    inv = [adi.invoice_reference,]

                future_or_admin = False
                if request.user.groups.filter(name__in=['Mooring Admin']).exists():
                    future_or_admin = True
                else:
                    future_or_admin = ad.in_future
                
                r.update({'invoice_ref': inv, 'in_future': future_or_admin, 'part_booking': ad.part_booking})
                if(r['customer']):
                    name = ad.customer.first_name + " " + ad.customer.last_name
                    email = ad.customer.email
                    r.update({'customerName': name, 'email': email})
                else:
                    r.update({'customerName': 'No customer', 'email': "No customer"})
            
        except Exception as e:
            res ={
                "Error": str(e)
            }

        return Response(OrderedDict([
                ('recordsTotal', recordsTotal),
                ('recordsFiltered',recordsFiltered),
                ('results',res)
            ]),status=status.HTTP_200_OK)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def list(self, request, *args, **kwargs):
        from django.db import connection, transaction
        try:

            #search = request.GET.get('search[value]')
            search = request.GET.get('search_keyword')
            draw = request.GET.get('draw') if request.GET.get('draw') else None
            start = request.GET.get('start') if request.GET.get('draw') else 1
            length = request.GET.get('length') if request.GET.get('draw') else 'all'
            arrival = datetime.strptime(request.GET.get('arrival'),'%d/%m/%Y') if request.GET.get('arrival') else None 
            departure = datetime.strptime(request.GET.get('departure'),'%d/%m/%Y') if request.GET.get('departure') else None 
            campground = request.GET.get('campground')
            region = request.GET.get('region') if request.GET.get('region') else None
            canceled = request.GET.get('canceled',None)
            refund_status = request.GET.get('refund_status',None)
            if canceled:
                canceled = True if canceled.lower() in ['yes','true','t','1'] else False
            canceled = 't' if canceled else 'f'


            moorings_user_groups = MooringAreaGroup.objects.filter(members__in=[request.user]).values('id','moorings')
            filter_query = Q()
            if canceled == 't':
                filter_query &= Q(booking_type=4)
            else:
                filter_query &= Q(booking_type=1) 
            if departure:
                 filter_query &= Q(arrival__lte=departure)
            if arrival:
                 filter_query &= Q(departure__gt=arrival)

            booking_query = Booking.objects.filter(filter_query).order_by('-id')
            recordsTotal = Booking.objects.filter(Q(Q(booking_type=1) | Q(booking_type=4))).count()
            recordsFiltered = booking_query.count()
            # build predata
            booking_items = {}
            booking_item_query = Q()
            mooring_name_list = {}
            for booking in booking_query: 
                  booking_item_query |= Q(booking_id=booking.id)
                  booking_items[booking.id] = []


            if len(booking_items) > 0:
                booking_items_object = MooringsiteBooking.objects.filter(booking_item_query).values('campsite__mooringarea__name','campsite__mooringarea__id','campsite_id','id','to_dt','from_dt','amount','booking_type','booking_period_option','booking_id','booking','date','campsite__mooringarea__park__district__region__name','campsite__mooringarea__park__district__region__id','campsite__name')
                
                for bi in booking_items_object: 
                      booking_items[bi['booking_id']].append({'id':bi['id'], 'campsite_id': bi['campsite_id'] , 'date' : bi['date'], 'from_dt': bi['from_dt'], 'to_dt': bi['to_dt'], 'amount': bi['amount'], 'booking_type' : bi['booking_type'], 'booking_period_option' :bi['booking_period_option'], 'campsite_name': bi['campsite__name'], 'region_name': bi['campsite__mooringarea__park__district__region__name'],'mooring_name': bi['campsite__mooringarea__name'], 'region_id': bi['campsite__mooringarea__park__district__region__id'], 'mooringarea_id': bi['campsite__mooringarea__id'] })
                       
            clean_data = []
            booking_data = []
            recordFilteredCount = 0
            rowcount = 0
            rowcountend = 0
            if length != 'all': 
                rowcountend = int(start) + int(length)
            for booking in booking_query:
                msb_list = []
                in_mg = False
                skip_row = False
                if region or campground:
                    skip_row = True
                else:
                    skip_row = False

                for bitem in booking_items[booking.id]:

                   msb_list.append([bitem['mooring_name'], bitem['region_name'], bitem['from_dt'], bitem['to_dt']])
                   if region:
                       if int(region) == int(bitem['region_id']):
                          skip_row = False
                   if campground:
                       if region:
                          if skip_row is False:
                            if int(campground) == int(bitem['mooringarea_id']):
                                skip_row = False
                            else:
                                skip_row = True
                       else:
                            if int(campground) == int(bitem['mooringarea_id']):
                                skip_row = False 
                            pass

                   # If user not in mooring group than skip
                   for mug in moorings_user_groups:
                        if mug['moorings'] == None:
                            pass
                        else:
                            if int(mug['moorings']) == int(bitem['mooringarea_id']):
                                in_mg = True 


                # If user not in mooring group than skip
                if in_mg is False:
                   continue

                # Search Keyword in data results
                if search:
                     if skip_row is False:
                          string_found = False
                          if search == str(booking.id):
                               string_found = True
                          if search == 'PS'+str(booking.id):
                               string_found = True
                          if booking.customer:
                                customer_email = booking.customer.email if booking.customer and booking.customer.email else ""
                                if search.lower() in customer_email.lower():
                                     string_found = True
 
                          customer_name = booking.details.get('first_name','')+' '+booking.details.get('last_name','')
                          if search.lower() in customer_name.lower():
                                string_found = True
                          phone_number = booking.details.get('phone','')
                          if search.lower() in phone_number.lower():
                                 string_found = True

                          for r in booking.regos.all():
                             if r.type == 'vessel':
                                 if search.lower() in r.rego.lower():
                                     string_found = True
 
                          for m_items in msb_list:
                              if search.lower() in m_items[0].lower():
                                      string_found = True
                              if search.lower() in m_items[1].lower():
                                      string_found = True

                          if string_found is True:
                               pass
                          else:
                               skip_row = True

                
                if skip_row is True:
                    continue
                recordFilteredCount = recordFilteredCount + 1

                show_row = False
                if length == 'all':
                    show_row = True
                else:
                    if rowcount >= int(start):
                        show_row = True
                    if rowcount > rowcountend:
                        show_row = False
 
                if show_row is True:
                    bk_list={}

                    booking_editable = False
                    if request.user.is_staff is True:
                        booking_editable = True
                    if request.user.is_superuser is True:
                        booking_editable = True


                    bk_list['editable'] = booking_editable
                    bk_list['id'] = booking.id

                    if booking.booking_type == 4:
                        bk_list['status'] = 'Cancelled'
                    else:
                        bk_list['status'] = booking.status
                    booking_invoices= booking.invoices.all()
                    bk_list['booking_type'] = booking.booking_type
                    bk_list['has_history'] = 0 #booking.has_history
                    bk_list['cost_total'] = booking.cost_total
                    bk_list['amount_paid'] = booking.amount_paid
                    bk_list['invoice_status'] = booking.invoice_status
                    bk_list['vehicle_payment_status'] = booking.vehicle_payment_status
                    bk_list['refund_status'] = booking.refund_status
                    bk_list['is_canceled'] = 'Yes' if booking.is_canceled else 'No'
                    bk_list['cancelation_reason'] = booking.cancellation_reason
                    bk_list['canceled_by'] = booking.canceled_by.get_full_name() if booking.canceled_by else ''
                    bk_list['cancelation_time'] = booking.cancelation_time if booking.cancelation_time else ''
                    bk_list['paid'] = booking.paid
                    bk_list['invoices'] = [i.invoice_reference for i in booking_invoices]
                    bk_list['active_invoices'] = [ i.invoice_reference for i in booking_invoices if i.active]
                    bk_list['guests'] = booking.guests
                    bk_list['admissions'] = { 'id' :booking.admission_payment.id, 'amount': booking.admission_payment.totalCost } if booking.admission_payment else None

                    vessel_beam = 0
                    vessel_weight = 0
                    vessel_size = 0
                    vessel_draft = 0

                    if 'vessel_beam' in booking.details:
                         vessel_beam = booking.details['vessel_beam']
                    if 'vessel_weight' in booking.details:
                         vessel_weight = booking.details['vessel_weight']
                    if 'vessel_size' in booking.details:
                         vessel_size = booking.details['vessel_size']
                    if 'vessel_draft' in booking.details:
                         vessel_draft = booking.details['vessel_draft']



 
                    bk_list['vessel_details'] = { 'vessel_beam': vessel_beam, 'vessel_weight': vessel_weight, 'vessel_size': vessel_size, 'vessel_draft': vessel_draft, } 

                    #bk_list['campsite_names'] = booking.campsite_name_list
                    bk_list['regos'] = [{'vessel':''}] 
                    for r in booking.regos.all():
                          if r.type == 'vessel':
                             bk_list['regos']=  [{r.type: r.rego}]
                    bk_list['booking_phone_number'] = ''
                    if booking.details: 
                         bk_list['firstname'] = booking.details.get('first_name','')
                         bk_list['lastname'] = booking.details.get('last_name','')
                         if "phone" in booking.details:
                             bk_list['booking_phone_number'] = booking.details['phone']

                    if booking.customer:
                        bk_list['email'] = booking.customer.email if booking.customer and booking.customer.email else ""
                        if booking.customer.phone_number:
                           bk_list['phone'] = booking.customer.phone_number
                        elif booking.customer.mobile_number:
                            bk_list['phone'] = booking.customer.mobile_number
                        else:
                            bk_list['phone'] = ''
                        if booking.is_canceled:
                            bk_list['campground_site_type'] = ""
                        else:
                            first_campsite = booking.first_campsite
                            bk_list['campground_site_type'] = first_campsite.type if first_campsite else ""
                            if booking.mooringarea.site_type != 2:
                                bk_list['campground_site_type'] = '{}{}'.format('{} - '.format(first_campsite.name if first_campsite else ""),'({})'.format(bk_list['campground_site_type'] if bk_list['campground_site_type'] else ""))
                    else:
                        bk['campground_site_type'] = ""


                    #msb_list.sort(key=lambda item: item[2])
                    bk_list['mooringsite_bookings'] = msb_list

                    booking_data.append(bk_list)
                rowcount = rowcount + 1
            recordsFiltered = recordFilteredCount 

            return Response(OrderedDict([
                ('recordsTotal', recordsTotal),
                ('recordsFiltered',recordsFiltered),
                ('results',booking_data)
            ]),status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, format=None):
        from datetime import datetime
        userCreated = False
        try:
            if 'ps_booking' in request.session:
                del request.session['ps_booking']
#            start_date = datetime.strptime(request.data['arrival'],'%Y/%m/%d').date()
#            end_date = datetime.strptime(request.data['departure'],'%Y/%m/%d').date()
#            guests = request.data['guests']
#            costs = request.data['costs']

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            start_date = serializer.validated_data['arrival']
            end_date = serializer.validated_data['departure']
            guests = request.data['guests']
            costs = request.data['costs']
            #regos = request.data['regos']
            override_price = serializer.validated_data.get('override_price', None)
            override_reason = serializer.validated_data.get('override_reason', None)
            override_reason_info = serializer.validated_data.get('override_reason_info', None)
            overridden_by = None if (override_price is None) else request.user

            try:
                emailUser = request.data['customer']
                customer = EmailUser.objects.get(email = emailUser['email'])
            except EmailUser.DoesNotExist:
                customer = EmailUser.objects.create(
                    email = emailUser['email'],
                    first_name = emailUser['first_name'],
                    last_name = emailUser['last_name'],
                    phone_number = emailUser['phone'],
                    mobile_number  = emailUser['phone'],
                )

                userCreated = True
                try:
                    country = emailUser['country']
                    country = Country.objects.get(iso_3166_1_a2=country)
                    Address.objects.create(line1='address',user = customer,postcode = emailUser['postcode'],country = country.iso_3166_1_a2)
                except Country.DoesNotExist:
                    raise serializers.ValidationError("Country you have entered does not exist")


            booking_details = {
                'campsites': Mooringsite.objects.filter(id__in=request.data['campsites']),
                'start_date' : start_date,
                'end_date' : end_date,
                'num_adult' : guests['adult'],
                'num_concession' : guests['concession'],
                'num_child' : guests['child'],
                'num_infant' : guests['infant'],
                'num_mooring' : guests['mooring'],
                'cost_total' : costs['total'],
                'override_price' : override_price,
                'override_reason' : override_reason,
                'override_reason_info' : override_reason_info,
                'overridden_by': overridden_by,
                'customer' : customer,
                'first_name': emailUser['first_name'],
                'last_name': emailUser['last_name'],
                'country': emailUser['country'],
                'postcode': emailUser['postcode'],
                'phone': emailUser['phone'],
                # 'regos': regos
            }

            #booking_details = {
            #    'campsites':request.data['campsite'],
            #    'start_date' : start_date,
            #    'end_date' : end_date,
            #    'num_mooring' : guests['mooring'],
            #    'num_adult' : guests['adult'],
            #    'num_concession' : guests['concession'],
            #    'num_child' : guests['child'],
            #    'num_infant' : guests['infant'],
            #    'num_mooring' : guests['mooring'],
            #    'cost_total' : costs['total'],
            #    'customer' : customer,
            #    'first_name': emailUser['first_name'],
            #    'last_name': emailUser['last_name'],
            #    'country': emailUser['country'],
            #    'postcode': emailUser['postcode'],
            #    'phone': emailUser['phone'],
            #}
            data = utils.internal_booking(request,booking_details)
            serializer = BookingSerializer(data)
            return Response(serializer.data)
        except serializers.ValidationError:
            utils.delete_session_booking(request.session)
            if userCreated:
                customer.delete()
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print (e)
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            utils.delete_session_booking(request.session)
            if userCreated:
                customer.delete()
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e[0]))

    def update(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK

            instance = self.get_object()
            start_date = datetime.strptime(request.data['arrival'],'%d/%m/%Y').date()
            end_date = datetime.strptime(request.data['departure'],'%d/%m/%Y').date()
            guests = request.data['guests']
            booking_details = {
                'campsites':request.data['campsites'],
                'start_date' : start_date,
                'mooringarea' : request.data['mooringarea'],
                'end_date' : end_date,
                'num_adult' : guests['adults'],
                'num_concession' : guests['concession'],
                'num_child' : guests['children'],
                'num_infant' : guests['infants'],
                'num_mooring' : guests['mooring'],
            }

            data = utils.update_booking(request,instance,booking_details)
            serializer = BookingSerializer(data)

            return Response(serializer.data, status=http_status)

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def partial_update(self, request, pk):
        booking = self.get_object()
        if 'details' in request.data:
            request.POST._mutable = True
            detail = {}
            b = '{}"'
            for char in b:
                request.POST['details'] = request.POST['details'].replace(char, "")
            items = request.POST['details'].split(",")
            for item in items:
                itm = item.split(':')
                key = itm[0]
                value = itm[1]
                detail[key] = value
            request.POST['details'] = detail
 
        serializer = self.get_serializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201, data=serializer.data)
        return Reponse(status=400, data="wrong params")

    def destroy(self, request, *args, **kwargs):
        http_status = status.HTTP_200_OK
        try:
            reason = request.GET.get('reason',None)
            if not reason:
                raise serializers.ValidationError('A reason is needed before canceling a booking');
            booking  = self.get_object()
            booking.cancelBooking(reason,user=request.user)
            emails.send_booking_cancelation(booking,request)
            serializer = self.get_serializer(booking)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @csrf_exempt
    @detail_route(permission_classes=[PaymentCallbackPermission],methods=['GET','POST'])
    def payment_callback(self, request, *args, **kwargs):
        from django.utils import timezone
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
                
                invoice_ref = request.data.get('invoice',None)
                if invoice_ref:
                    try:
                        invoice = Invoice.objects.get(reference=invoice_ref)
                        if invoice.payment_status in ['paid','over_paid']:
                            # Get the latest cash payment and see if it was paid in the last 1 minute
                            latest_cash = invoice.cash_transactions.last()
                            # Check if the transaction came in the last 10 seconds
                            if (timezone.now() - latest_cash.created).seconds < 10 and instance.paid:
                                # Send out the confirmation pdf
                                emails.send_booking_confirmation(instance,request)
                            else:
                                reponse['error'] = 'Booking is not fully paid or the transaction was not done in the last 10 secs'
                        else:
                            reponse['error'] = 'Invoice is not fully paid'
                    
                    except Invoice.DoesNotExist:
                        response['error'] = 'Invoice was not found'
                else:
                    response['error'] = 'Invoice was not found'
                    
            
                response['status'] = 'approved'
            return Response(response,status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(permission_classes=[],methods=['GET'])
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
               return Response(response,status=status.HTTP_200_OK)
            # Check if the time for the booking has elapsed
            if instance.expiry_time <= timezone.now():
                response['error'] = 'This booking has expired'
                return Response(response,status=status.HTTP_200_OK)
            #if all is well    
            response['status'] = 'approved'
            return Response(response,status=status.HTTP_200_OK)
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
            data = BookingHistorySerializer(history,many=True).data
            return Response(data,status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    


class MooringsiteRateViewSet(viewsets.ModelViewSet):
    queryset = MooringsiteRate.objects.all()
    serializer_class = MooringsiteRateSerializer

    def create(self, request, format=None):
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
                rate = Rate.objects.get_or_create(adult=rate_serializer.validated_data['adult'],concession=rate_serializer.validated_data['concession'],child=rate_serializer.validated_data['child'])[0]
            print(rate_serializer.validated_data)
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

                serializer = MooringsiteRateReadonlySerializer(res)
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
            #print(request.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

        # Below is no longer used as we have switched to booking periods.
        # Leaving this in for now but will be cleared up in the future.
        # try:
        #     http_status = status.HTTP_200_OK
        #     rate = None
        #     rate_serializer = RateDetailSerializer(data=request.data)
        #     rate_serializer.is_valid(raise_exception=True)
        #     rate_id = rate_serializer.validated_data.get('rate',None)
        #     if rate_id:
        #         try:
        #             rate = Rate.objects.get(id=rate_id)
        #         except Rate.DoesNotExist as e :
        #             raise serializers.ValidationError('The selected rate does not exist')
        #     else:
        #         rate = Rate.objects.get_or_create(adult=rate_serializer.validated_data['adult'],concession=rate_serializer.validated_data['concession'],child=rate_serializer.validated_data['child'])[0]
        #         pass
        #     if rate:
        #         data = {
        #             'rate': rate.id,
        #             'date_start': rate_serializer.validated_data['period_start'],
        #             'campsite': rate_serializer.validated_data['campsite'],
        #             'reason': rate_serializer.validated_data['reason'],
        #             'update_level': 2
        #         }
        #         instance = self.get_object()
        #         partial = kwargs.pop('partial', False)
        #         serializer = self.get_serializer(instance,data=data,partial=partial)
        #         serializer.is_valid(raise_exception=True)
        #         self.perform_update(serializer)

        #         return Response(serializer.data, status=http_status)

        # except serializers.ValidationError:
        #     print(traceback.print_exc())
        #     raise
        # except ValidationError as e:
        #     raise serializers.ValidationError(repr(e.error_dict))
        # except Exception as e:
        #     raise serializers.ValidationError(str(e))

class BookingRangeViewset(viewsets.ModelViewSet):

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        original = bool(request.GET.get("original", False))
        serializer = self.get_serializer(instance, original=original, method='get')
        data = serializer.data

        start = datetime.strptime(serializer.data['range_start'], '%d/%m/%Y %H:%M')
        timestamp = calendar.timegm(start.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        start = local_dt.replace(microsecond=start.microsecond)
        data['range_start'] = start.strftime('%d/%m/%Y %H:%M')

        if serializer.data['range_end']:
                end = datetime.strptime(serializer.data['range_end'], '%d/%m/%Y %H:%M') if serializer.data['range_end'] else ""
                timestamp = calendar.timegm(end.timetuple())
                local_dt = datetime.fromtimestamp(timestamp)
                end = local_dt.replace(microsecond=end.microsecond)
                data['range_end'] = end.strftime('%d/%m/%Y %H:%M')
        return Response(data)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            partial = kwargs.pop('partial', False)

            mutable = request.POST._mutable
            request.POST._mutable = True
            date_start = request.POST['range_start']
            time_start = request.POST.get('range_start_time', "00:00")
            request.POST['range_start'] = date_start +" "+ time_start
            date_end = request.POST.get('range_end', None)
            time_end = request.POST.get('range_end_time', "23:59")
            if date_end is not None and date_end != "" and date_end != " ":
                request.POST['range_end'] = date_end +" "+ time_end
            request.POST._mutable = mutable

            
            serializer = self.get_serializer(instance,data=request.data,partial=partial)
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

class MooringAreaBookingRangeViewset(BookingRangeViewset):
    queryset = MooringAreaBookingRange.objects.all()
    serializer_class = MooringAreaBookingRangeSerializer

class MooringsiteBookingRangeViewset(BookingRangeViewset):
    queryset = MooringsiteBookingRange.objects.all()
    serializer_class = MooringsiteBookingRangeSerializer

class RateViewset(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

class BookingPeriodOptionsViewSet(viewsets.ModelViewSet):
    queryset = BookingPeriodOption.objects.all().order_by('id')
    serializer_class = BookingPeriodOptionsSerializer

    def list(self, request, *args, **kwargs):
        q = request.GET.get('q') if request.GET.get('q') else None
        qs = BookingPeriodOption.objects.all().order_by('pk')
        if q:
            qs = qs.filter(period_name__icontains=q)
        serializer = BookingPeriodOptionsSerializer(qs, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if(BookingPeriod.objects.filter(booking_period=instance.id)):
            # Needs ignoring
            return Response('Error in use.', status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            self.perform_destroy(instance)
            return Response(status.HTTP_200_OK)

class BookingPeriodViewSet(viewsets.ModelViewSet):
    queryset = BookingPeriod.objects.all()
    serializer_class = BookingPeriodSerializer

    def list(self, request, *args, **kwargs):
        qs = BookingPeriod.objects.all().order_by('pk')
        serializer = BookingPeriodSerializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            serializer = BookingPeriodSerializer(data={'name':request.data['name']})
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            for val in request.data['booking_period']:
                option = BookingPeriodOption.objects.get(pk=val)
                if option:
                    instance.booking_period.add(option)
            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = BookingPeriodSerializer(instance,data={'name':request.data['name']},partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            instance.booking_period.clear()
            for val in request.data['booking_period']:
                option = BookingPeriodOption.objects.get(pk=val)
                if option:
                    instance.booking_period.add(option)
            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            raise serializers.ValidationError(str(e))

class RegisteredVesselsViewSet(viewsets.ModelViewSet):
    queryset = RegisteredVessels.objects.all()
    serializer_class = RegisteredVesselsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        rego = request.GET.get('rego') if request.GET.get('rego') else None
        queryset = self.get_queryset()
        if rego is not None:
            if len(rego) > 2:
               queryset = queryset.filter(rego_no=rego.upper())
               serializer = self.get_serializer(queryset, many=True)
               return Response(serializer.data)
            else:
                raise serializers.ValidationError("Please enter more characters")
 
        else:
           raise serializers.ValidationError("Please provide Rego")

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance,method='get')
        return Response(serializer.data)


# Reasons
# =========================
class ClosureReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClosureReason.objects.all()
    serializer_class = ClosureReasonSerializer

    def list(self, request, *args, **kwargs):
        groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
        qs = self.get_queryset()
        mooring_groups = []
        for group in groups:
            mooring_groups.append(group.id)
        queryset = qs.filter(mooring_group__in=mooring_groups)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class OpenReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OpenReason.objects.all()
    serializer_class = OpenReasonSerializer

    def list(self, request, *args, **kwargs):
        groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
        qs = self.get_queryset()
        mooring_groups = []
        for group in groups:
            mooring_groups.append(group.id)
        queryset = qs.filter(mooring_group__in=mooring_groups)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class PriceReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceReason.objects.all()
    serializer_class = PriceReasonSerializer

    def list(self, request, *args, **kwargs):
        groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
        qs = self.get_queryset()
        mooring_groups = []
        for group in groups:
            mooring_groups.append(group.id)
        queryset = qs.filter(mooring_group__in=mooring_groups)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AdmissionsReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdmissionsReason.objects.all()
    serializer_class = AdmissionsReasonSerializer

    def list(self, request, *args, **kwargs):
        groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
        qs = self.get_queryset()
        mooring_groups = []
        for group in groups:
            mooring_groups.append(group.id)
        queryset = qs.filter(mooring_group__in=mooring_groups)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MaximumStayReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaximumStayReason.objects.all()
    serializer_class = MaximumStayReasonSerializer

    def list(self, request, *args, **kwargs):
        groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
        qs = self.get_queryset()
        mooring_groups = []
        for group in groups:
            mooring_groups.append(group.id)
        queryset = qs.filter(mooring_group__in=mooring_groups)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class DiscountReasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DiscountReason.objects.all()
    serializer_class = DiscountReasonSerializer

    def list(self, request, *args, **kwargs):
        groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
        qs = self.get_queryset()
        mooring_groups = []
        for group in groups:
            mooring_groups.append(group.id)
        queryset = qs.filter(mooring_group__in=mooring_groups)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
        if q :
            queryset = EmailUser.objects.filter(email__icontains=q)[:10]
        else:
            queryset = self.get_queryset()

        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)

    @detail_route(methods=['POST',])
    def update_personal(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = PersonalSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def update_contact(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = UserContactSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def update_address(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = UserAddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            address, created = Address.objects.get_or_create(
                line1 = serializer.validated_data['line1'],
                locality = serializer.validated_data['locality'],
                state = serializer.validated_data['state'],
                country = serializer.validated_data['country'],
                postcode = serializer.validated_data['postcode'],
                user = instance 
            )
            instance.residential_address = address
            instance.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data);
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

    def create(self, request,*args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

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
                    'details': serializer.validated_data.get('details',None)
                }
            if serializer.data['type'] == 'Marina':
                for c in serializer.data['campgrounds']:
                    data['update_level'] = 0
                    MooringArea.objects.get(pk=c).createMooringsitePriceHistory(data)
            elif serializer.data['type'] == 'Mooringsite Type':
                data['update_level'] = 1
                MooringsiteClass.objects.get(pk=serializer.data['campsiteType']).createMooringsitePriceHistory(data)

            return Response(serializer.data, status=http_status)

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e[0]))

class AdmissionsRatesViewSet(viewsets.ModelViewSet):
    queryset = AdmissionsRate.objects.all()
    renderer_classes = (JSONRenderer,)
    serializer_class = AdmissionsRateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @detail_route(methods=['GET'])
    def get_price(self, request, format='json', pk=None):
        http_status = status.HTTP_200_OK
        try:
            date = request.GET.get('date')
            if date:
                if request.user.is_staff:
                    group = MooringAreaGroup.objects.filter(members__in=[request.user,])
                else:
                    key = request.GET.get('location') if request.GET.get('location') else None
                    group = AdmissionsLocation.objects.filter(key=key)[0].mooring_group
                if group:
                    price = AdmissionsRate.objects.filter(Q(mooring_group__in=group), Q(period_start__lte=date), Q(period_end=None) | Q(period_end__gte=date))
                    res = {
                        'price' : price
                    }
        except Exception as e:
            res = {
                'Error': str(e)
            }
        return Response(res, status=http_status)

    @list_route(methods=['get'])
    def get_price_by_location(self, request, format='json', pk=None):
        http_status = status.HTTP_200_OK
        res = ""
        try:
            date = request.GET.get('date')
            key = request.GET.get('location') if request.GET.get('location') else None
            if date:
                if request.user.is_staff:
                    groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
                    if groups.count() > 1:
                        group = AdmissionsLocation.objects.filter(key=key)[0].mooring_group
                    else:
                        group = groups[0]
                else:
                    group = AdmissionsLocation.objects.filter(key=key)[0].mooring_group
                if group:
                    price = AdmissionsRate.objects.filter(Q(mooring_group__in=[group]), Q(period_start__lte=date), Q(period_end=None) | Q(period_end__gte=date))[0]
                    serializer = AdmissionsRateSerializer(price)
                    res = {
                        'price' : serializer.data
                    }
        except Exception as e:
            res = {
                'Error': str(e)
            }
        return Response(res, status=http_status)


    @list_route(methods=['get'])
    def price_history(self, request, format='json', pk=None):
        http_status = status.HTTP_200_OK
        try:
            group = MooringAreaGroup.objects.filter(members__in=[request.user,])
            price_history = AdmissionsRate.objects.filter(mooring_group__in=group).order_by('-period_start')
            serializer = AdmissionsRateSerializer(price_history,many=True)
            res = serializer.data
            for row in res:
                row_group = MooringAreaGroup.objects.get(pk=row['mooring_group'])
                row['mooring_group'] = row_group.name
        except Exception as e:
            res ={
                "Error": str(e)
            }

        return Response(res,status=http_status)

    @list_route(methods=['post'],)
    def add_price(self, request, format='json', pk=None):
        try:
            http_status = status.HTTP_200_OK
            start = datetime.strptime(request.data['period_start'], '%Y-%m-%d').date() + timedelta(days=-1)

#             mooring_group =  MooringAreaGroup.objects.get(id=request.data['period']
#            group = MooringAreaGroup.objects.filter(members__in=[request.user,])
            request.POST._mutable = True
#            if group.count() == 1:
#                request.data['mooring_group'] = group[0].id
#            else:
#                raise ValueError('Must belong to exactly 1 mooring group when adding admissions fees.');
            request.data['period_start'] = start
            request.POST._mutable = False
            serializer = AdmissionsRateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = serializer.data
            return Response(res,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))


class BookingRefundsReportView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            report = None
            data = {
                "start":request.GET.get('start'),
                "end":request.GET.get('end'),
            }
            serializer = ReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'Booking Refunds Report-{}-{}'.format(str(serializer.validated_data['start']),str(serializer.validated_data['end']))
            # Generate Report
            report = reports.booking_refunds(serializer.validated_data['start'],serializer.validated_data['end'])


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

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            report = None
            data = {
                "date":request.GET.get('date'),
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

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            report = None
            data = {
                "date":request.GET.get('date'),
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
    renderer_classes = [JSONRenderer,]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        # Check if the user has any address and set to residential address
        user = request.user
        # if not user.residential_address:
        #     user.residential_address = user.profile_addresses.first() if user.profile_addresses.all() else None
        #     user.save()
        serializer  = UserSerializer(request.user)
        data = serializer.data
        groups = MooringAreaGroup.objects.filter(members__in=[user,])
        groups_text = []
        for group in groups:
            groups_text.append(group.name)
        data['is_inventory'] = is_inventory(user)
        data['is_admin'] = is_admin(user)
        data['is_payment_officer'] = is_payment_officer(user)
        data['groups'] = groups_text
        return JsonResponse(data)


class GetProfileAdmin(views.APIView):
    renderer_classes = [JSONRenderer,]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Check if the user has any address and set to residential address
        if request.user.is_staff:
            user = EmailUser.objects.get(email=request.GET.get('email_address'))
            serializer  = UserSerializer(user)
            data = serializer.data
            groups = MooringAreaGroup.objects.filter(members__in=[user,])
            groups_text = []
            for group in groups:
                groups_text.append(group.name)
            data['is_inventory'] = is_inventory(user)
            data['is_admin'] = is_admin(user)
            data['is_payment_officer'] = is_payment_officer(user)
            data['groups'] = groups_text
            return JsonResponse(data)
        else:
            data['status'] = 'permission denied'
            return JsonResponse(data)


class UpdateProfilePersonal(views.APIView):
    renderer_classes = [JSONRenderer,]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            instance = request.user
            serializer = PersonalSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data);
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
    renderer_classes = [JSONRenderer,]
    permission_classes = [IsAuthenticated] 
    
    def post(self, request, *args, **kwargs):
        try:
            instance = request.user
            serializer = PhoneSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data);
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
    renderer_classes = [JSONRenderer,]
    permission_classes = [IsAuthenticated] 
    
    def post(self, request, *args, **kwargs):
        try:
            instance = request.user
            serializer = UserAddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            address, created = Address.objects.get_or_create(
                line1 = serializer.validated_data.get('line1'),
                locality = serializer.validated_data.get('locality'),
                state = serializer.validated_data.get('state'),
                country = serializer.validated_data.get('country'),
                postcode = serializer.validated_data.get('postcode'),
                user = instance
            )
            instance.residential_address = address
            instance.save()
            serializer = UserSerializer(instance)
            return Response(serializer.data);
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
    renderer_classes = [JSONRenderer,]
    def get(self, request, format=None):
        try:
            data = {
                "date":request.GET.get("date"),
                "override": request.GET.get("override")
            }
            serializer = OracleSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            utils.oracle_integration(serializer.validated_data['date'].strftime('%Y-%m-%d'),serializer.validated_data['override'])
            data = {'successful':True}
            return Response(data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e[0]))


class GlobalSettingsView(views.APIView):
    renderer_classes = [JSONRenderer,]
    permission_classes = [IsAdminUser,]
    def get(self, request):
        try:
            groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
            key = request.GET.get('key') if request.GET.get('key') else None
            if key:
                if groups.count() == 1:
                    qs = GlobalSettings.objects.filter(mooring_group__in=groups, key=key)
                else:
                    if groups.count() == 0:
                        return Response("Error more than 1 group")
                    if groups.count() > 1 and key == 0:
                        return Response("Error more than 1 group")
                    qs = GlobalSettings.objects.filter(key=key)
                    highest_val = 0
                    highest_i = 0
                    for i, q in enumerate(qs):
                        if float(q.value) > highest_val:
                            highest_val = float(q.value)
                            highest_i = i
                    qsid = qs[highest_i].id
                    qs = GlobalSettings.objects.filter(id=qsid)
                    
                serializer = GlobalSettingsSerializer(qs, many=True)
                return Response(serializer.data)
            else:
                mooring = request.GET.get('mooring') if request.GET.get('mooring') else None
                if mooring:
                    groups = MooringAreaGroup.objects.filter(moorings__in=[mooring,])
                if groups.count() == 1:
                    qs = GlobalSettings.objects.filter(mooring_group__in=groups, key__gte=3, key__lte=14).order_by('key')
                else:
                    return Response("Error more than 1 group")
                serializer = GlobalSettingsSerializer(qs, many=True)
                return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise

class AdmissionsKeyFromURLView(views.APIView):
    renderer_classes = [JSONRenderer,]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            url = request.GET.get('url') if request.GET.get('url') else None
            if not url:
                return Response("Error, no url passed")
            else:
                url_split = url.split('/')
                url = url_split[2]
                global_set_url = GlobalSettings.objects.filter(key__in=[15,16], value=url)
                if global_set_url.count() > 0:
                    mooring_group = global_set_url[0].mooring_group
                    locs = AdmissionsLocation.objects.filter(mooring_group=mooring_group)
                    if locs.count() > 0:
                        loc = locs[0]
                        today = datetime.now().date()
                        rates = AdmissionsRate.objects.filter(Q(period_start__lte=today), (Q(period_end=None) | Q(period_end__gte=today)), mooring_group=mooring_group)
                        oracle_codes = AdmissionsOracleCode.objects.filter(mooring_group=mooring_group)
                        key = loc.key
                        if key and rates.count() > 0 and oracle_codes.count() > 0:
                            return Response(key)
                    else:
                        return Response("Error, no location found")
                else:
                    return Response("Error, no global setting found")
        except Exception as e:
            print(traceback.print_exc())
            raise



def get_current_booking(ongoing_booking, request): 
     #ongoing_booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
     timer = None
     expiry = None
     if ongoing_booking:
         #expiry_time = ongoing_booking.expiry_time
         timer = (ongoing_booking.expiry_time-timezone.now()).seconds if ongoing_booking else -1
         expiry = ongoing_booking.expiry_time.isoformat() if ongoing_booking else ''
     payments_officer_group = request.user.groups.filter(name__in=['Payments Officers']).exists()

     ms_booking = MooringsiteBooking.objects.filter(booking=ongoing_booking).order_by('from_dt')
     cb = {'current_booking':[], 'total_price': '0.00'}
     current_booking = []
#     total_price = Decimal('0.00')
     total_price = Decimal('0.00')
     for ms in ms_booking:
         row = {}
         row['id'] = ms.id
           #print ms.from_dt.astimezone(pytimezone('Australia/Perth'))
         row['item'] = ms.campsite.name + ' from '+ms.from_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%y %H:%M %p')+' to '+ms.to_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%y %H:%M %p')
         row['amount'] = str(ms.amount)
         
         row['past_booking'] = False
#         if ms.from_dt.date() <= datetime.now().date():
         ms_from_ft = datetime.strptime(ms.from_dt.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
         #+timedelta(hours=8)
#         print datetime.utcnow()+timedelta(hours=8)
         nowtime = datetime.strptime(str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
         #+timedelta(hours=8)
         if ms_from_ft <= nowtime:
              
              if ms_from_ft.date() == nowtime.date():
                 if ongoing_booking.old_booking is None:
                     pass 
                 else:
                     row['past_booking'] = True              
              else:
                  row['past_booking'] = True
              if payments_officer_group is True: 
                  row['past_booking'] = False
#           row['item'] = ms.campsite.name
         total_price = str(Decimal(total_price) +Decimal(ms.amount))
         current_booking.append(row)
     cb['current_booking'] = current_booking
     cb['total_price'] = str(total_price)
     cb['ongoing_booking'] = True if ongoing_booking else False,
     cb['ongoing_booking_id'] = ongoing_booking.id if ongoing_booking else None,
     cb['details'] = ongoing_booking.details if ongoing_booking else [],
     cb['expiry'] = expiry
     cb['timer'] = timer

     return cb


class CheckOracleCodeView(views.APIView):
    renderer_classes = [JSONRenderer,]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format='json'):
        try:
           oracle_code = request.GET.get('oracle_code','')
           if OracleAccountCode.objects.filter(active_receivables_activities=oracle_code).count() > 0:
                 json_obj = {'found': True, 'code': oracle_code}
           else:
                 json_obj = {'found': False, 'code': oracle_code}
           return Response(json_obj)
        except Exception as e:
            print(traceback.print_exc())
            raise

#from rest_framework.decorators import api_view
class RefundOracleView(views.APIView):
    renderer_classes = [JSONRenderer,]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):

    #def get(self, request, format='json'):
        
        try:
           if request.user.is_superuser or request.user.groups.filter(name__in=['Payments Officers']).exists():
 
                money_from = request.POST.get('money_from',[])
                money_to = request.POST.get('money_to',[])
                bpoint_trans_split= request.POST.get('bpoint_trans_split',[])
                refund_method = request.POST.get('refund_method', None)
                booking_id = request.POST.get('booking_id',None)
                newest_booking_id = request.POST.get('newest_booking_id',None)
                booking = Booking.objects.get(pk=newest_booking_id)
                money_from_json = json.loads(money_from)
                money_to_json = json.loads(money_to)
                bpoint_trans_split_json = json.loads(bpoint_trans_split)
                failed_refund = False
     
                json_obj = {'found': False, 'code': money_from, 'money_to': money_to, 'failed_refund': failed_refund}
    
                lines = []
                if int(refund_method) == 1:
                    lines = []
                    for mf in money_from_json:
                        if Decimal(mf['line-amount']) > 0: 
                            money_from_total = (Decimal(mf['line-amount']) - Decimal(mf['line-amount']) - Decimal(mf['line-amount']))
                            lines.append({'ledger_description':str(mf['line-text']),"quantity":1,"price_incl_tax":money_from_total,"oracle_code":str(mf['oracle-code']), 'line_status': 3})

                    for bp_txn in bpoint_trans_split_json:
                        bpoint_id = BpointTransaction.objects.get(txn_number=bp_txn['txn_number'])
                        info = {'amount': Decimal('{:.2f}'.format(float(bp_txn['line-amount']))), 'details' : 'Refund via system'}
                        if info['amount'] > 0:
                             lines.append({'ledger_description':str("Temp fund transfer "+bp_txn['txn_number']),"quantity":1,"price_incl_tax":Decimal('{:.2f}'.format(float(bp_txn['line-amount']))),"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 1})


                    order = utils.allocate_refund_to_invoice(request, booking, lines, invoice_text=None, internal=False, order_total='0.00',user=booking.customer)
                    new_invoice = Invoice.objects.get(order_number=order.number)
                    update_payments(new_invoice.reference) 
                    #order = utils.allocate_refund_to_invoice(request, booking, lines, invoice_text=None, internal=False, order_total='0.00',user=booking.customer)
                    #new_order = Order.objects.get(basket=basket)
                    #new_invoice = Invoice.objects.get(order_number=order.number)
                
                    for bp_txn in bpoint_trans_split_json:
                        bpoint_id = None
                        try:
                             bpoint_id = BpointTransaction.objects.get(txn_number=bp_txn['txn_number'])
                             info = {'amount': Decimal('{:.2f}'.format(float(bp_txn['line-amount']))), 'details' : 'Refund via system'}
                        except Exception as e:
                             print (e)
                             info = {'amount': Decimal('{:.2f}'.format('0.00')), 'details' : 'Refund via system'}

                        refund = None
                        lines = []
                        if info['amount'] > 0:
                            lines = []
                            #lines.append({'ledger_description':str("Temp fund transfer "+bp_txn['txn_number']),"quantity":1,"price_incl_tax":Decimal('{:.2f}'.format(float(bp_txn['line-amount']))),"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 1}) 


                            try:

                                bpoint_money_to = (Decimal('{:.2f}'.format(float(bp_txn['line-amount']))) - Decimal('{:.2f}'.format(float(bp_txn['line-amount']))) - Decimal('{:.2f}'.format(float(bp_txn['line-amount']))))
                                lines.append({'ledger_description':str("Payment Gateway Refund to "+bp_txn['txn_number']),"quantity":1,"price_incl_tax": bpoint_money_to,"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 3})
                                bpoint = BpointTransaction.objects.get(txn_number=bp_txn['txn_number'])
                                refund = bpoint.refund(info,request.user)
                            except Exception as e:
                                print (e)
                                failed_refund = True
                                bpoint_failed_amount = Decimal(bp_txn['line-amount'])
                                lines = []
                                lines.append({'ledger_description':str("Refund failed for txn "+bp_txn['txn_number']),"quantity":1,"price_incl_tax":bpoint_failed_amount,"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 1})
                            order = utils.allocate_refund_to_invoice(request, booking, lines, invoice_text=None, internal=False, order_total='0.00',user=booking.customer)
                            new_invoice = Invoice.objects.get(order_number=order.number)

                            if refund:
                               bpoint_refund = BpointTransaction.objects.get(txn_number=refund.txn_number)
                               bpoint_refund.crn1 = new_invoice.reference
                               bpoint_refund.save()
                               new_invoice.settlement_date = None
                               new_invoice.save()
                               update_payments(new_invoice.reference)
     
                else:
                    lines = []
                    for mf in money_from_json:
                        if Decimal(mf['line-amount']) > 0:
                            money_from_total = (Decimal(mf['line-amount']) - Decimal(mf['line-amount']) - Decimal(mf['line-amount']))
                            lines.append({'ledger_description':str(mf['line-text']),"quantity":1,"price_incl_tax":money_from_total,"oracle_code":str(mf['oracle-code']), 'line_status': 3})
    

                    for mt in money_to_json:
                        lines.append({'ledger_description':mt['line-text'],"quantity":1,"price_incl_tax":mt['line-amount'],"oracle_code":mt['oracle-code'], 'line_status': 1})
                    order = utils.allocate_refund_to_invoice(request, booking, lines, invoice_text=None, internal=False, order_total='0.00',user=booking.customer)
                    new_invoice = Invoice.objects.get(order_number=order.number)
                    update_payments(new_invoice.reference)

                json_obj['failed_refund'] = failed_refund
            
                return Response(json_obj)
           else:
                raise serializers.ValidationError('Permission Denied.') 
               
        except Exception as e:
           print(traceback.print_exc())
           raise



