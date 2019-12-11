from datetime import datetime, timedelta, date
import traceback
from decimal import *
import json
import calendar
import geojson
import requests
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from dateutil.tz.tz import tzoffset
from pytz import timezone as pytimezone
from ledger.payments.models import Invoice,OracleInterface,CashTransaction
from ledger.payments.utils import oracle_parser_on_invoice,update_payments
from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission, get_cookie_basket
from mooring.models import (MooringArea, Mooringsite, MooringsiteRate, MooringsiteBooking, Booking, BookingInvoice, MooringsiteBookingRange, Rate, MooringAreaBookingRange,MooringAreaStayHistory, MooringsiteRate, MarinaEntryRate, BookingVehicleRego, AdmissionsBooking, AdmissionsOracleCode, AdmissionsRate, AdmissionsLine, ChangePricePeriod, CancelPricePeriod, GlobalSettings, MooringAreaGroup, AdmissionsLocation, ChangeGroup, CancelGroup, BookingPeriod, BookingPeriodOption, AdmissionsBookingInvoice)
from mooring.serialisers import BookingRegoSerializer, MooringsiteRateSerializer, MarinaEntryRateSerializer, RateSerializer, MooringsiteRateReadonlySerializer, AdmissionsRateSerializer
from mooring.emails import send_booking_invoice,send_booking_confirmation
from oscar.apps.order.models import Order
from ledger.payments.invoice import utils

def create_booking_by_class(campground_id, campsite_class_id, start_date, end_date, num_adult=0, num_concession=0, num_child=0, num_infant=0, num_mooring=0, vessel_size=0):
    """Create a new temporary booking in the system."""
    # get campground
    campground = MooringArea.objects.get(pk=campground_id)

    # TODO: date range check business logic
    # TODO: number of people check? this is modifiable later, don't bother

    # the MooringsiteBooking table runs the risk of a race condition,
    # wrap all this behaviour up in a transaction
    with transaction.atomic():

        # fetch all the campsites and applicable rates for the campground
        sites_qs =  Mooringsite.objects.filter(
                        mooringarea=campground,
                        campsite_class=campsite_class_id
                    )

        if not sites_qs.exists():
            raise ValidationError('No matching campsites found.')

        # get availability for sites, filter out the non-clear runs
        availability = get_campsite_availability(sites_qs, start_date, end_date)
        excluded_site_ids = set()
        for site_id, dates in availability.items():
            if not all([v[0] == 'open' for k, v in dates.items()]):
                excluded_site_ids.add(site_id)

        # create a list of campsites without bookings for that period
        sites = [x for x in sites_qs if x.pk not in excluded_site_ids]

        if not sites:
            raise ValidationError('Mooringsite class unavailable for specified time period.')

        # TODO: add campsite sorting logic based on business requirements
        # for now, pick the first campsite in the list
        site = sites[0]

        # Prevent booking if max people passed
        total_people = num_adult + num_concession + num_child + num_infant + num_mooring
        if total_people > site.max_people:
            raise ValidationError('Maximum number of people exceeded for the selected campsite')
        # Prevent booking if less than min people 
        if total_people < site.min_people:
            raise ValidationError('Number of people is less than the minimum allowed for the selected campsite')

        # Create a new temporary booking with an expiry timestamp (default 20mins)
        booking =   Booking.objects.create(
                        booking_type=3,
                        arrival=start_date,
                        departure=end_date,
                        details={
                            'num_adult': num_adult,
                            'num_concession': num_concession,
                            'num_child': num_child,
                            'num_infant': num_infant,
                            'num_mooring' : num_mooring,
                            'vessel_size' : vessel_size
                        },
                        expiry_time=timezone.now()+timedelta(seconds=settings.BOOKING_TIMEOUT),
                        mooringarea=campground
                    )
        for i in range((end_date-start_date).days):
            cb =    MooringsiteBooking.objects.create(
                        campsite=site,
                        booking_type=3,
                        date=start_date+timedelta(days=i),
                        booking=booking
                    )

    # On success, return the temporary booking
    return booking

def create_booking_by_site(sites_qs, start_date, end_date, num_adult=0, num_concession=0, num_child=0, num_infant=0, num_mooring=0, vessel_size=0, cost_total=0, override_price=None, override_reason=None, override_reason_info=None, send_invoice=False, overridden_by=None, customer=None, updating_booking=False, override_checks=False):
    """Create a new temporary booking in the system for a set of specific campsites."""

    # the CampsiteBooking table runs the risk of a race condition,
    # wrap all this behaviour up in a transaction
    campsite_qs = Mooringsite.objects.filter(pk__in=sites_qs)
    with transaction.atomic():
        # get availability for campsite, error out if booked/closed
        availability = get_campsite_availability(campsite_qs, start_date, end_date, False)
        for site_id, dates in availability.items():
            if not override_checks:
                if updating_booking:
                    if not all([v[0] in ['open','tooearly'] for k, v in dates.items()]):
                        raise ValidationError('Mooring unavailable for specified time period.')
                else:
                    if not all([v[0] == 'open' for k, v in dates.items()]):
                        raise ValidationError('Mooring unavailable for specified time period.')
            else:
                if not all([v[0] in ['open','tooearly','closed'] for k, v in dates.items()]):
                    raise ValidationError('Mooring unavailable for specified time period.')
                
        if not override_checks:
            # Prevent booking if max people passed
            total_people = num_adult + num_concession + num_child + num_infant
            min_people = sum([cs.min_people for cs in campsite_qs]) 
            max_people = sum([cs.max_people for cs in campsite_qs])

            if total_people > max_people:
                raise ValidationError('Maximum number of people exceeded')
            # Prevent booking if less than min people 
            #if total_people < min_people:
            #    raise ValidationError('Number of people is less than the minimum allowed for the selected campsite(s)')

        # Create a new temporary booking with an expiry timestamp (default 20mins)       
        booking =   Booking.objects.create(
                        booking_type=3,
                        arrival=start_date,
                        departure=end_date,
                        details={
                            'num_adult': num_adult,
                            'num_concession': num_concession,
                            'num_child': num_child,
                            'num_infant': num_infant,
                            'num_mooring': num_mooring,
                            'vessel_size': vessel_size

                        },
                        cost_total = cost_total,
                        override_price = Decimal(override_price) if (override_price is not None) else None,
                        override_reason = override_reason,
                        override_reason_info = override_reason_info,
                        send_invoice = send_invoice,
                        overridden_by = overridden_by,
                        expiry_time=timezone.now()+timedelta(seconds=settings.BOOKING_TIMEOUT),
                        mooringarea=campsite_qs[0].mooringarea,
                        customer = customer
                    )
        for cs in campsite_qs:
            for i in range((end_date-start_date).days):
                cb =    MooringsiteBooking.objects.create(
                            campsite=cs,
                            booking_type=3,
                            date=start_date+timedelta(days=i),
                            booking=booking
                        )
                        
    # On success, return the temporary booking
    return booking

def ooolldcreate_booking_by_site(campsite_id, start_date, end_date, num_adult=0, num_concession=0, num_child=0, num_infant=0,num_mooring=0,vessel_size=0,cost_total=0,customer=None,updating_booking=False):
    """Create a new temporary booking in the system for a specific campsite."""
    # get campsite
    sites_qs = Mooringsite.objects.filter(pk=campsite_id)
    campsite = sites_qs.first()
    # TODO: date range check business logic
    # TODO: number of people check? this is modifiable later, don't bother

    # the MooringsiteBooking table runs the risk of a race condition,
    # wrap all this behaviour up in a transaction
    with transaction.atomic():
        # get availability for campsite, error out if booked/closed
        availability = get_campsite_availability(sites_qs, start_date, end_date)
        for site_id, dates in availability.items():
            if updating_booking:
                if not all([v[0] in ['open','tooearly'] for k, v in dates.items()]):
                    raise ValidationError('Mooringsite unavailable for specified time period.')
            else:
                if not all([v[0] == 'open' for k, v in dates.items()]):
                    raise ValidationError('Mooringsite unavailable for specified time period.')

        # Prevent booking if max people passed
        total_people = num_adult + num_concession + num_child + num_infant + num_mooring
        if total_people > campsite.max_people:
            raise ValidationError('Maximum number of people exceeded for the selected campsite')
        # Prevent booking if less than min people 
        if total_people < campsite.min_people:
            raise ValidationError('Number of people is less than the minimum allowed for the selected campsite')

        # Create a new temporary booking with an expiry timestamp (default 20mins)
        booking =   Booking.objects.create(
                        booking_type=3,
                        arrival=start_date,
                        departure=end_date,
                        details={
                            'num_adult': num_adult,
                            'num_concession': num_concession,
                            'num_child': num_child,
                            'num_infant': num_infant,
                            'num_mooring': num_mooring,
                            'vessel_size': vessel_size
                        },
                        cost_total= Decimal(cost_total),
                        expiry_time=timezone.now()+timedelta(seconds=settings.BOOKING_TIMEOUT),
                        mooringarea=campsite.mooringarea,
                        customer = customer
                    )
        for i in range((end_date-start_date).days):
            cb =    MooringsiteBooking.objects.create(
                        campsite=campsite,
                        booking_type=3,
                        date=start_date+timedelta(days=i),
                        booking=booking
                    )
    # On success, return the temporary booking
    return booking

def check_mooring_available_by_time(campsite_id, start_date_time, end_date_time):

     # Confirmed Bookings
     start_time_count = MooringsiteBooking.objects.filter(
          Q(campsite_id=campsite_id) &
          ( Q(from_dt__lte=start_date_time)  & Q(to_dt__gte=start_date_time))
     ).exclude(booking_type__in=[3,4]).count()

     end_time_count = MooringsiteBooking.objects.filter(
          Q(campsite_id=campsite_id) &
          ( Q(from_dt__lte=end_date_time)  & Q(to_dt__gte=end_date_time))
     ).exclude(booking_type__in=[3,4]).count()

     # Temp bookings
     start_time_temp_count = MooringsiteBooking.objects.filter(
          Q(campsite_id=campsite_id) & Q(booking_type__in=[3]) & Q(booking__expiry_time__gte=datetime.today())  &
          ( Q(from_dt__lte=start_date_time)  & Q(to_dt__gte=start_date_time))
     ).count()

     end_time_temp_count = MooringsiteBooking.objects.filter(
          Q(campsite_id=campsite_id) & Q(booking_type__in=[3]) & Q(booking__expiry_time__gte=datetime.today())  &
          ( Q(from_dt__lte=end_date_time)  & Q(to_dt__gte=end_date_time))
     ).count()

     if start_time_count > 0 or end_time_count > 0 or start_time_temp_count > 0 or end_time_temp_count >0:
        return True

     return False

def check_mooring_availablity(campsites_qs, start_date, end_date):

    avail_results = get_campsite_availability(campsites_qs, start_date, end_date,None, None)

    cs_array = {}
    for av in avail_results:
       open_periods = 0
       closed_periods = 0
       for date_rotate in avail_results[av]:
           bp = avail_results[av][date_rotate][1]
           
           for i in bp:
               if avail_results[av][date_rotate][1][i] == 'open':
                   open_periods = open_periods + 1
               else:
                   closed_periods = closed_periods + 1
       cs_array[av] = { 'open_periods': open_periods, 'closed_periods': closed_periods}
    return cs_array 

def get_open_marinas(campsites_qs, start_date, end_date):
    """Fetch the set of Marine Parks (from a set of Mooring Sites) with spaces open over a range of visit dates."""
    # short circuit: if start date is before today, return nothing
    exclude_moorings = []
    today = date.today()
    #if start_date < today:
    #    return set()

    campsites_qs = check_mooring_availablity(campsites_qs,start_date, end_date)

    # remove from the campsite list any entries with bookings
#    campsites_qs = campsites_qs.exclude(
#        id__in=exclude_moorings
#        mooringsitebooking__date__range=(start_date, end_date-timedelta(days=1))
    # and also campgrounds where the book window is outside of the max advance range
#    ).exclude(
#        campground__max_advance_booking__lte=(start_date-today).days - 1 
#        mooringarea__max_advance_booking__lt=(start_date-today).days 
#    )

    # get closures at campsite and campground level
 #   cgbr_qs = MooringAreaBookingRange.objects.filter(
#        Q(campground__in=[x[0] for x in campsites_qs.distinct('mooringarea').values_list('mooringarea')]),
#        Q(status=1),
#        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
#    )
#    cgbr = set([x[0] for x in cgbr_qs.values_list('campground')])
##    cgbr = set([x[0] for x in cgbr_qs.values_list('campground')])


#    csbr_qs = MooringsiteBookingRange.objects.filter(
#        Q(campsite__in=campsites_qs),
#        Q(status=1),
#        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
#    )
#    print csbr_qs
#    csbr = set([x[0] for x in csbr_qs.values_list('campsite')])

    # generate a campground-to-campsite-list map with closures removed
    mooring_map = {} 
    for cs in campsites_qs:
#        if cs == 5:
#            pass
#        else:
        #mooring_map = {}
        mooring_map[cs] = campsites_qs[cs]
        #mooring_map.append(row)


#    for cs in campsites_qs:
        
#        if (cs.pk in csbr) or (cs.mooringarea.pk in cgbr):
#            continue
#        if cs.mooringarea.pk not in mooring_map:
#            mooring_map[cs.mooringarea.pk] = []
#        mooring_map[cs.mooringarea.pk].append(cs.pk)
    return mooring_map

def generate_mooring_rate(mooringsites_qs,start_date, end_date, duration):
     mooring_rate = {} 
     mooring_site_ids = []
     search_filter = Q()

     for ms in mooringsites_qs:
         mooring_site_ids.append(ms.id)
         search_filter |= Q(campsite_id=ms.id)

     #print (mooring_site_ids)
     mooring_rate_search_filter = Q()
     mooring_rate_search_filter &= Q(search_filter)# & Q(date_start__lte=start_date) & Q(Q(date_end__gte=start_date)  | Q(date_end=None))
     #& Q(date_end__gte=end_date) 
     #& Q(date_end__lte=end_date)
     mr_resp = MooringsiteRate.objects.filter(mooring_rate_search_filter).order_by('date_start')
     #print (mr_resp)
     for i in range(duration):
         date_rotate_forward = start_date+timedelta(days=i)
         mooring_rate[date_rotate_forward] = {}
         for mrr in mr_resp:
            # this is to account for None end dates..
            if mrr.date_end is None:
                mrr.date_end = datetime.today().date()+timedelta(days=90)
                #+timedelta(days=90)
            if mrr.date_start <= date_rotate_forward and mrr.date_end >= date_rotate_forward:
                #print (str(mrr.id)+' '+str(mrr.date_start)+' '+str(mrr.date_end)+' '+str(mrr.campsite.id) )
            #mooring_rate[date_rotate_forward] = {}
                mooring_rate[date_rotate_forward][mrr.campsite_id] = mrr
        
     #print (mooring_rate)
     return mooring_rate 

     #for i in range(duration):
     #    date_rotate_forward = start_date+timedelta(days=i)    
     #    print (date_rotate_forward)
     #    mooring_rate_search_filter = Q()
     #    mooring_rate_search_filter &= Q(search_filter) & Q(date_start__lte=date_rotate_forward) & Q(date_end__gte=date_rotate_forward)
     #    #print MooringsiteRate.objects.filter(campsite_id__in=[mooring_site_ids])
     #    #campsite_id__in=mooring_site_ids
     #    print (MooringsiteRate.objects.filter(mooring_rate_search_filter).query)
     #    mr = MooringsiteRate.objects.filter(mooring_rate_search_filter).order_by('date_start')
     #    #mr = MooringsiteRate.objects.filter(campsite_id__in=[1,2,3,4,5,6],date_start__lte=date_rotate_forward, date_end__gte=date_rotate_forward).order_by('date_start')
     #    for msr in mr:
     #        mooring_rate[date_rotate_forward] = {}
     #        mooring_rate[date_rotate_forward][msr.campsite.id] = msr 
#    #         mooring_rate[date_rotate_forward][mr.campsite_id] = msr
     #    print (mr)
     #    print ("MOOO RATE")
     #    print (mooring_rate)
#     if MooringsiteRate.objects.filter(campsite_id=site.pk,date_start__lte=date_rotate_forward, date_end__gte=date_rotate_forward).count() > 0:
#           mooring_rate = MooringsiteRate.objects.filter(campsite_id=site.pk,date_start__lte=date_rotate_forward, date_end__gte=date_rotate_forward).order_by('-date_start')[0]
#     else:
##          if MooringsiteRate.objects.filter(campsite_id=site.pk,date_start__lte=date_rotate_forward, date_end=None).count() > 0:
#               mooring_rate = MooringsiteRate.objects.filter(campsite_id=site.pk,date_start__lte=date_rotate_forward, date_end=None).order_by('-date_start')[0]



def get_campsite_availability(campsites_qs, start_date, end_date, ongoing_booking, request=None):
    """Fetch the availability of each mooring in a queryset over a range of visit dates."""
    # fetch all of the single-day MooringsiteBooking objects within the date range for the sites

    end_date =end_date+timedelta(days=1)
    start_date_time = datetime.strptime(str(start_date)+str(' 00:00'), '%Y-%m-%d %H:%M')
    end_date_time = datetime.strptime(str(end_date)+str(' 23:59'), '%Y-%m-%d %H:%M')
    booking_id = None
    booking_period_option = None
    today = date.today()
    nowtime =  datetime.today() 
    mooring_date_selected = {} 

    if ongoing_booking:
       booking_id = ongoing_booking.id
       #booking_period_option = ongoing_booking.booking_period_option

    booking_old_id=None
    if request is not None:
        #if request.get('session', None):
        if request:
            if 'ps_booking_old' in request.session:
                booking_old_id = request.session['ps_booking_old']

    bookings_qs =   MooringsiteBooking.objects.filter(
                        campsite__in=campsites_qs,
                        #date__gte=start_date,
                        #date__lt=end_date
                        from_dt__gte=start_date_time,
                        to_dt__lt=end_date_time,
                        #booking__expiry_time__gte=datetime.now()
                    ).exclude(booking__id=booking_old_id).order_by('date', 'campsite__name')
 
    # booking__expiry_time__gte=datetime.now()
    booking_qs = None
    # prefill all slots as 'open'
    duration = (end_date-start_date).days 
    #results = {site.pk: {start_date+timedelta(days=i): ['open', ] for i in range(duration)} for site in campsites_qs}
    # Build Hash of open periods
    mooring_rate_hash = generate_mooring_rate(campsites_qs,start_date, end_date, duration)

    results = {}
#    return results
    for site in campsites_qs:
        results[site.pk] = {}

        cgbr_qs = MooringAreaBookingRange.objects.filter(
            Q(campground=site.mooringarea),
            Q(status=1),
            Q(range_start__lt=end_date_time+timedelta(days=1)) & (Q(range_end__gte=start_date_time-timedelta(days=3))|Q(range_end__isnull=True))
        )
        
        for i in range(duration):
            date_rotate_forward = start_date+timedelta(days=i)
            mooring_date_selected[date_rotate_forward] = 'notselected'
            mooring_rate = None
            if date_rotate_forward in mooring_rate_hash:
                 if site.pk in mooring_rate_hash[date_rotate_forward]:
                    
                    mooring_rate =  mooring_rate_hash[date_rotate_forward][site.pk]
                    #print mooring_rate
                    #print ("BOOKING PERIOD")
                    #print (mooring_rate.booking_period.booking_period.all())


            #print ("MOORING RATE")
            #print (mooring_rate)
            #if MooringsiteRate.objects.filter(campsite_id=site.pk,date_start__lte=date_rotate_forward, date_end__gte=date_rotate_forward).count() > 0:
            #    mooring_rate = MooringsiteRate.objects.filter(campsite_id=site.pk,date_start__lte=date_rotate_forward, date_end__gte=date_rotate_forward).order_by('-date_start')[0]
            #else:
            #    if MooringsiteRate.objects.filter(campsite_id=site.pk,date_start__lte=date_rotate_forward, date_end=None).count() > 0:
            #         mooring_rate = MooringsiteRate.objects.filter(campsite_id=site.pk,date_start__lte=date_rotate_forward, date_end=None).order_by('-date_start')[0]
            #print (mooring_rate)
            #print ("GET CMA 9")
            #print (datetime.utcnow())

            booking_period = {}
            selection_period = {}
            bp_result = []

            if mooring_rate:
                if mooring_rate.booking_period is None:
                   continue
                bp_result =  mooring_rate.booking_period.booking_period.all()
                if bp_result is None:
                   continue
                for bp in bp_result:
                    booking_period[bp.pk] = 'open'
                    selection_period[bp.pk] = 0

                    if bp.start_time is None or bp.finish_time is None: 
                        booking_period[bp.pk] = 'closed'
                        continue
                    nowtimewa = nowtime+timedelta(hours=8)
                    start_dt = datetime.strptime(str(date_rotate_forward)+' '+str(bp.start_time), '%Y-%m-%d %H:%M:%S')
                    finish_dt = datetime.strptime(str(date_rotate_forward)+' '+str(bp.finish_time), '%Y-%m-%d %H:%M:%S')
                    if start_dt > finish_dt:
                         finish_dt = finish_dt+timedelta(days=1)
                    if date_rotate_forward < today:
                        booking_period[bp.pk] = 'closed'
                    if today == date_rotate_forward:
                         if ongoing_booking:
                               if ongoing_booking.old_booking is None:
                                  pass
                               else:
                                    if nowtime > start_dt:
                                       pass
                                       #booking_period[bp.pk] = 'closed'
                         else:
                              pass
                              #if nowtime > start_dt:
                              #     booking_period[bp.pk] = 'closed'

                    for closure in cgbr_qs:
                        # CLOSURE INFORMATION
                        start = max(start_date, (closure.range_start+ timedelta(hours=8)).date() -timedelta(days=2))
                        end = min(end_date, (closure.range_end + timedelta(hours=8)).date()) if closure.range_end.date() else end_date
                        closure_range = (end-start).days + 1

                        closure_start = closure.range_start+ timedelta(hours=8)
                        closure_finish = closure.range_end+timedelta(hours=8)
                        
                        # BOOKING PERIOD
                        if closure_start.strftime('%Y-%m-%d %H:%M:%S') >= start_dt.strftime('%Y-%m-%d %H:%M:%S'):
                               if closure_start.strftime('%Y-%m-%d %H:%M:%S') <= finish_dt.strftime('%Y-%m-%d %H:%M:%S'):
                                     booking_period[bp.pk] = 'closed'

                        if closure_finish.strftime('%Y-%m-%d %H:%M:%S') >= start_dt.strftime('%Y-%m-%d %H:%M:%S'):
                               if closure_finish.strftime('%Y-%m-%d %H:%M:%S') <= finish_dt.strftime('%Y-%m-%d %H:%M:%S'):
                                      booking_period[bp.pk] = 'closed'

                        if closure_start.strftime('%Y-%m-%d %H:%M:%S') <= start_dt.strftime('%Y-%m-%d %H:%M:%S') and closure_finish.strftime('%Y-%m-%d %H:%M:%S') >= finish_dt.strftime('%Y-%m-%d %H:%M:%S'):
                               booking_period[bp.pk] = 'closed'

            results[site.pk][date_rotate_forward] = ['closed',booking_period,selection_period, bp_result]
            #results[site.pk][start_date+timedelta(days=i)] = ['closed',booking_period,selection_period, bp_result]

    # Determine availablity
    for b in bookings_qs:
        if b.booking.id == booking_old_id:
             continue

        if b.booking.booking_type == 4: 
             print ("CANCELLED BOOKING")
             continue
        # Release booking availablity on Expired Bookings
        if b.booking.booking_type == 3 or b.booking.booking_type == 5:
             if b.booking.expiry_time is not None:
                 if b.booking.expiry_time < datetime.now(tz=timezone.utc):
                    continue

        for i in range(duration):
            date_rotate_forward = start_date+timedelta(days=i)
            mooring_rate = None
            if date_rotate_forward in mooring_rate_hash:
                 if b.campsite.id  in mooring_rate_hash[date_rotate_forward]:
                    mooring_rate =  mooring_rate_hash[date_rotate_forward][b.campsite.id]

            if mooring_rate:
               for bp in mooring_rate.booking_period.booking_period.all():
                    start_dt = datetime.strptime(str(date_rotate_forward)+' '+str(bp.start_time), '%Y-%m-%d %H:%M:%S')
                    finish_dt = datetime.strptime(str(date_rotate_forward)+' '+str(bp.finish_time), '%Y-%m-%d %H:%M:%S')
                    if start_dt > finish_dt:
                         finish_dt = finish_dt+timedelta(days=1)
 
                    from_dt = b.from_dt + timedelta(hours=8)
                    to_dt = b.to_dt + timedelta(hours=8)
                    if from_dt.strftime('%Y-%m-%d %H:%M:%S') >= start_dt.strftime('%Y-%m-%d %H:%M:%S'):
                        if from_dt.strftime('%Y-%m-%d %H:%M:%S') <= finish_dt.strftime('%Y-%m-%d %H:%M:%S'):
                            if date_rotate_forward in results[b.campsite.id]:
                                if results[b.campsite.id][date_rotate_forward][1][bp.id] != 'selected':
                                    results[b.campsite.id][date_rotate_forward][1][bp.id] = 'closed'
                                if b.booking.id == booking_id:
                                    if bp.id == b.booking_period_option.id:
                                        results[b.campsite.id][date_rotate_forward][1][bp.id] = 'selected'
                                        results[b.campsite.id][date_rotate_forward][2][bp.id] = b.id
                                        mooring_date_selected[date_rotate_forward] = 'selected'
                                pass
                    if to_dt.strftime('%Y-%m-%d %H:%M:%S') >= start_dt.strftime('%Y-%m-%d %H:%M:%S'):
                        if to_dt.strftime('%Y-%m-%d %H:%M:%S') <= finish_dt.strftime('%Y-%m-%d %H:%M:%S'):
                            if date_rotate_forward in results[b.campsite.id]:
                               if bp.id in results[b.campsite.id][date_rotate_forward][1]:
                                if results[b.campsite.id][date_rotate_forward][1][bp.id] != 'selected':
                                    results[b.campsite.id][date_rotate_forward][1][bp.id] = 'closed'
                                if b.booking.id == booking_id:
                                    if bp.id == b.booking_period_option.id:
                                        results[b.campsite.id][date_rotate_forward][1][bp.id] = 'selected'
                                        results[b.campsite.id][date_rotate_forward][2][bp.id] = b.id
                                        mooring_date_selected[date_rotate_forward] = 'selected'
                                pass
                    if from_dt.strftime('%Y-%m-%d %H:%M:%S') <= start_dt.strftime('%Y-%m-%d %H:%M:%S') and to_dt.strftime('%Y-%m-%d %H:%M:%S') >= finish_dt.strftime('%Y-%m-%d %H:%M:%S'):
                        if date_rotate_forward in results[b.campsite.id]:
                           if bp.id in results[b.campsite.id][date_rotate_forward][1]:
                            if results[b.campsite.id][date_rotate_forward][1][bp.id] != 'selected':
                               results[b.campsite.id][date_rotate_forward][1][bp.id] = 'closed'
                            if b.booking.id == booking_id:
                                if bp.id == b.booking_period_option.id:
                                   results[b.campsite.id][date_rotate_forward][1][bp.id] = 'selected'
                                   results[b.campsite.id][date_rotate_forward][2][bp.id] = b.id
                                   mooring_date_selected[date_rotate_forward] = 'selected'
                            pass



    # prevent other mooring from being selected for same day preventing mooring lockouts
    for ma in results: 
        for ma_dt in results[ma]:
            if mooring_date_selected[ma_dt] == 'selected':
               for bp in results[ma][ma_dt][1]:
                    if results[ma][ma_dt][1][bp] == 'open':
                         pass
                         results[ma][ma_dt][1][bp] = 'perday' 
                 
    mooring_map = {cg[0]: [cs.pk for cs in campsites_qs if cs.mooringarea.pk == cg[0]] for cg in campsites_qs.distinct('mooringarea').values_list('mooringarea')}
    today = date.today()

    # strike out days after the max_advance_booking
    for site in campsites_qs:
        try:
            group = MooringAreaGroup.objects.get(moorings__in=[site.mooringarea])
        except:
            group = None
        if group:
            max_advance = int(GlobalSettings.objects.get(key=2, mooring_group__in=[group,]).value)
        else:
            qs = GlobalSettings.objects.filter(key=2)
            highest_val = 0
            for q in qs:
                if int(q.value) > highest_val:
                    highest_val = int(q.value)
            max_advance = highest_val       

        stop = today + timedelta(days=max_advance)
        stop_mark = min(max(stop, start_date), end_date)
        #if start_date > stop:
        for i in range((end_date-stop_mark).days):
             if stop_mark+timedelta(days=i) > stop:
                 results[site.pk][stop_mark+timedelta(days=i)][0] = 'toofar'
                 for b in results[site.pk][stop_mark+timedelta(days=i)][1]:
                     results[site.pk][stop_mark+timedelta(days=i)][1][b] = 'toofar'
    # Get the current stay history
    stay_history = None
    if campsites_qs.count() > 0:
         stay_history = MooringAreaStayHistory.objects.filter(
                    Q(range_start__lte=start_date,range_end__gte=start_date)|# filter start date is within period
                    Q(range_start__lte=end_date,range_end__gte=end_date)|# filter end date is within period
                    Q(Q(range_start__gt=start_date,range_end__lt=end_date)&Q(range_end__gt=today)) #filter start date is before and end date after period
                    ,mooringarea=campsites_qs.first().mooringarea
                    )

    if stay_history:
        max_days = min([x.max_days for x in stay_history])
    else:
        max_days = settings.PS_MAX_BOOKING_LENGTH
    # strike out days after the max_stay period
    for site in campsites_qs:

        stay_history = MooringAreaStayHistory.objects.filter(
                    Q(range_start__lte=start_date,range_end__gte=start_date)|# filter start date is within period
                    Q(range_start__lte=end_date,range_end__gte=end_date)|# filter end date is within period
                    Q(Q(range_start__gt=start_date,range_end__lt=end_date)&Q(range_end__gt=today)) #filter start date is before and end date after period
                    ,mooringarea=site.mooringarea
                    )
        if stay_history:
            max_days = min([x.max_days for x in stay_history])
        else:
            max_days = settings.PS_MAX_BOOKING_LENGTH

        stop = start_date + timedelta(days=max_days)
        stop_mark = min(max(stop, start_date), end_date)
        for i in range((end_date-stop_mark).days):
            date_key = stop_mark+timedelta(days=i)
            if date_key in results[site.pk]:
                results[site.pk][stop_mark+timedelta(days=i)][0] = 'toofar'
                for b in results[site.pk][stop_mark+timedelta(days=i)][1]:
                     if results[site.pk][stop_mark+timedelta(days=i)][1][b] == 'open': 
                         results[site.pk][stop_mark+timedelta(days=i)][1][b] = 'maxstay'


    return results


def get_visit_rates(campsites_qs, start_date, end_date):
    """Fetch the per-day pricing for each visitor type over a range of visit dates."""
    # fetch the applicable rates for the campsites
    rates_qs = MooringsiteRate.objects.filter(
        Q(campsite__in=campsites_qs),
        Q(date_start__lt=end_date) & (Q(date_end__gte=start_date)|Q(date_end__isnull=True))
    ).prefetch_related('rate')
    # prefill all slots
    duration = (end_date-start_date).days+1
    results = {
        site.pk: {
            start_date+timedelta(days=i): {
                'mooring':  '0.00',
                'adult': '0.00',
                'child': '0.00',
                'concession': '0.00',
                'infant': '0.00',
                'booking_period' : [] 
            } for i in range(duration)
        } for site in campsites_qs
    }

    # make a record of the earliest MooringsiteRate for each site
    early_rates = {}
    for rate in rates_qs:
        #if rate.campsite.pk not in early_rates:
        #    early_rates[rate.campsite.pk] = rate
        #elif early_rates[rate.campsite.pk].date_start > rate.date_start:
        #    early_rates[rate.campsite.pk] = rate
        
        # for the period of the visit overlapped by the rate, set the amounts
        start = max(start_date, rate.date_start)
        end = min(end_date, rate.date_end) if rate.date_end else end_date
        for i in range((end-start).days+1):
            if  rate.booking_period is None:
                 continue
            booking_period = rate.booking_period.booking_period.all()
            
            results[rate.campsite.pk][start+timedelta(days=i)]['mooring'] = str(rate.rate.mooring)
            results[rate.campsite.pk][start+timedelta(days=i)]['adult'] = str(rate.rate.adult)
            results[rate.campsite.pk][start+timedelta(days=i)]['concession'] = str(rate.rate.concession)
            results[rate.campsite.pk][start+timedelta(days=i)]['child'] = str(rate.rate.child)
            results[rate.campsite.pk][start+timedelta(days=i)]['infant'] = str(rate.rate.infant)
            for b in booking_period:
                if b.caption is None:
                     b.caption = ''    
                booking_period_row = {'id':b.id, 'period_name' : b.period_name, 'small_price': format(b.small_price,'.2f'), 'medium_price': format(b.medium_price,'.2f'), 'large_price' : format(b.large_price,'.2f'), 'start_time' : b.start_time, 'finish_time' : b.finish_time,'all_day' : b.all_day, 'caption': b.caption, 'created' : b.created }
#                booking_period_row = {} 
#                booking_period_row['id'] = b.id
#                booking_period_row['period_name'] = b.period_name
#                   , 'period_name' : b.period_name, 'small_price': str(b.small_price), 'medium_price': str(b.medium_price), 'large_price' : str(b.large_price), 'start_time' : str(b.start_time), 'finish_time' : str(b.finish_time),'all_day' : str(b.all_day), 'created' : str(b.created)  )
                results[rate.campsite.pk][start+timedelta(days=i)]['booking_period'].append(booking_period_row)

    # complain if there's a Mooringsite without a MooringsiteRate
    if len(early_rates) < rates_qs.count():
        print('Missing Mooring Site Rate coverage!')
    # for ease of testing against the old datasets, if the visit dates are before the first
    # MooringsiteRate date, use that MooringsiteRate as the pricing model.
    for site_pk, rate in early_rates.items():
        if start_date < rate.date_start:
            start = start_date
            end = rate.date_start
            for i in range((end-start).days):
                results[site_pk][start+timedelta(days=i)]['mooring'] = str(rate.rate.mooring)
                results[site_pk][start+timedelta(days=i)]['adult'] = str(rate.rate.adult)
                results[site_pk][start+timedelta(days=i)]['concession'] = str(rate.rate.concession)
                results[site_pk][start+timedelta(days=i)]['child'] = str(rate.rate.child)
                results[site_pk][start+timedelta(days=i)]['infant'] = str(rate.rate.infant)
                if  rate.booking_period is None:
                    continue
                for b in rate.booking_period.booking_period.all(): 
                    booking_period_row = {'id':b.id, 'period_name' : b.period_name, 'small_price': format(b.small_price,'.2f'), 'medium_price': format(b.medium_price,'.2f'), 'large_price' : format(b.large_price,'.2f'), 'start_time' : b.start_time, 'finish_time' : b.finish_time,'all_day' : b.all_day, 'created' : b.created  } 
                    results[site_pk][start+timedelta(days=i)]['booking_period'].append(booking_period_row) 
                    

    return results

def get_available_campsitetypes(campground_id,start_date,end_date,_list=True):
    try:
        cg = MooringArea.objects.get(id=campground_id)

        if _list:
            available_campsiteclasses = []
        else:
            available_campsiteclasses = {}

        for _class in cg.campsite_classes:
            sites_qs =  Mooringsite.objects.all()
#            sites_qs =  Mooringsite.objects.filter(
#                           campground=campground_id,
        #                    mooringsite_class=_class
#                        )
            sites_qs = None
            if sites_qs.exists():

                # get availability for sites, filter out the non-clear runs
                availability = get_campsite_availability(sites_qs, start_date, end_date)
                excluded_site_ids = set()
                for site_id, dates in availability.items():
                    if not all([v[0] == 'open' for k, v in dates.items()]):
                        excluded_site_ids.add(site_id)

                # create a list of campsites without bookings for that period
                sites = [x for x in sites_qs if x.pk not in excluded_site_ids]

                if sites:
                    if not _list:
                        available_campsiteclasses[_class] = sites
                    else:
                        available_campsiteclasses.append(_class)

        return available_campsiteclasses
    except MooringArea.DoesNotExist:
        raise Exception('The campsite you are searching does not exist')
    except:
        raise


def get_available_campsites_list(campsite_qs,request, start_date, end_date):
    from mooring.serialisers import MooringsiteSerialiser
    campsites = get_campsite_availability(campsite_qs, start_date, end_date)
    available = []
    for camp in campsites:
        av = [item for sublist in campsites[camp].values() for item in sublist]
        if ('booked' not in av):
            if ('closed' not in av):
                available.append(MooringsiteSerialiser(Mooringsite.objects.filter(id = camp),many=True,context={'request':request}).data[0])

    return available

def get_available_campsites_list_booking(campsite_qs,request, start_date, end_date,booking):
    '''
        Used to get the available campsites in the selected period
        and the ones currently attached to a booking
    '''
    from mooring.serialisers import MooringsiteSerialiser
    campsites = get_campsite_availability(campsite_qs, start_date, end_date)
    available = []
    for camp in campsites:
        av = [item for sublist in campsites[camp].values() for item in sublist]
        if ('booked' not in av or camp in booking.campsite_id_list):
            if ('closed' not in av):
                available.append(MooringsiteSerialiser(Mooringsite.objects.filter(id = camp),many=True,context={'request':request}).data[0])

    #complete = [MooringsiteSerialiser(Mooringsite.objects.filter(id = camp),many=True,context={'request':request}).data[0]]

    return available

def get_campsite_current_rate(request,campsite_id,start_date,end_date):
    res = []
    if start_date and end_date:
        start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
        end_date = datetime.strptime(end_date,"%Y-%m-%d").date()
        for single_date in daterange(start_date, end_date):
            price_history = MooringsiteRate.objects.filter(campsite=campsite_id,date_start__lte=single_date).order_by('-date_start')
            if price_history:
                rate = RateSerializer(price_history[0].rate,context={'request':request}).data
                rate['campsite'] = campsite_id
                res.append({
                    "date" : single_date.strftime("%Y-%m-%d"),
                    "rate" : rate
                })
    return res

def get_park_entry_rate(request,start_date):
    res = []
    if start_date:
        start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
        price_history = MarinaEntryRate.objects.filter(period_start__lte = start_date).order_by('-period_start')
        if price_history:
            serializer = MarinaEntryRateSerializer(price_history,many=True,context={'request':request})
            res = serializer.data[0]
    return res

def override_lineitems(override_price, override_reason, total_price, oracle_code, override_reason_info=""):
    invoice_line = []
    if oracle_code:
        #if override_reason:
        discount = Decimal(override_price) - Decimal(override_price) - Decimal(override_price)
        invoice_line.append({"ledger_description": '{} - {}'.format(override_reason.text, override_reason_info), "quantity": 1, 'price_incl_tax': discount, 'oracle_code': oracle_code, 'line_status': 1})
    return invoice_line

def nononline_booking_lineitems(oracle_code, request):
    invoice_line = []
    if oracle_code:
        group = MooringAreaGroup.objects.filter(members__in=[request.user])
        value = GlobalSettings.objects.get(mooring_group=group, key=0).value
        if Decimal(value) > 0:
            invoice_line.append({'ledger_description': 'Phone Booking Fee', 'quantity': 1, 'price_incl_tax': Decimal(value), 'oracle_code': oracle_code, 'line_status': 1})
#            invoice_line.append({'ledger_description': 'Phone Booking Fee', 'quantity': 1, 'price_incl_tax': Decimal(value), 'oracle_code': oracle_code})
    return invoice_line

def admission_lineitems(lines):
    invoice_lines = []
    if lines:
        for line in lines:
            if line['guests'] > 0:
                invoice_lines.append({'ledger_description': 'Admissions {} - {} ({} guests)'.format(line['from'], line['to'], line['guests']), "quantity": 1, 'price_incl_tax': line['admissionFee'], "oracle_code": line['oracle_code'], 'line_status': 1})

#            invoice_lines.append({'ledger_description': 'Admissions {} - {} ({} guests)'.format(line['from'], line['to'], line['guests']), "quantity": 1, 'price_incl_tax': line['admissionFee'], "oracle_code": line['oracle_code']})

    return invoice_lines


def calculate_price_booking_cancellation(booking, overide_cancel_fees=False):
    current_date_time = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    nowtime =  datetime.today()
    nowtimec = datetime.strptime(nowtime.strftime('%Y-%m-%d'),'%Y-%m-%d')
    mg = MooringAreaGroup.objects.all()

    booking = MooringsiteBooking.objects.filter(booking=booking)
    cancellation_fees = []
    adjustment_fee = Decimal('0.00')
    #{'additional_fees': 'true', 'description': 'Booking Change Fee','amount': Decimal('0.00')}

    for ob in booking:
         changed = True
         #for bc in booking_changes:
         #    if bc.campsite == ob.campsite and ob.from_dt == bc.from_dt and ob.to_dt == bc.to_dt and ob.booking_period_option == bc.booking_period_option:
         #       changed = False
         from_dt = datetime.strptime(ob.from_dt.strftime('%Y-%m-%d'),'%Y-%m-%d')
         daystillbooking =  (from_dt-nowtimec).days

         cancel_policy = None
         cancel_fee_amount = '0.00'
         #change_price_period = CancelPricePeriod.objects.filter(id=ob.booking_period_option.cancel_group_id).order_by('days')
         cancel_group =  CancelGroup.objects.get(id=ob.booking_period_option.cancel_group_id)
         cancel_price_period = cancel_group.cancel_period.all().order_by('days')
         mooring_group =None
         for i in mg:
            if i.moorings.count() > 0:
                    mooring_group = i.moorings.all()[0].id 


         for cpp in cancel_price_period:
             if daystillbooking < 0:
                  daystillbooking = 0
             if daystillbooking >= cpp.days:
                  cancel_policy =cpp

         if cancel_policy:
             if cancel_policy.calulation_type == 0:
                 # Percentage
                 cancel_fee_amount = float(ob.amount) * (cancel_policy.percentage / 100)
             elif cancel_policy.calulation_type == 1:
                 cancel_fee_amount = cancel_policy.amount
                 # Fixed Pricing
             description = 'Mooring {} ({} - {})'.format(ob.campsite.mooringarea.name,ob.from_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'),ob.to_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'))

             if overide_cancel_fees is True:
                  cancellation_fees.append({'additional_fees': 'true', 'description': 'Refund - '+description,'amount': str(ob.amount - ob.amount - ob.amount), 'mooring_group': mooring_group, 'oracle_code': str(ob.campsite.mooringarea.oracle_code)})
             else:

                  if datetime.strptime(ob.from_dt.astimezone(pytimezone('Australia/Perth')).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S') < current_date_time:
                      #cancellation_fees.append({'additional_fees': 'true', 'description': 'Past Booking - '+description,'amount': Decimal('0.00'), 'mooring_group': mooring_group})
                      cancellation_fees.append({'additional_fees': 'true', 'description': 'Past Booking - '+description,'amount': Decimal('0.00'), 'mooring_group': mooring_group, 'oracle_code': str(ob.campsite.mooringarea.oracle_code)})
                  else:
                      #change_fees['amount'] = str(refund_amount)
                      cancellation_fees.append({'additional_fees': 'true', 'description': 'Cancel Fee - '+description,'amount': cancel_fee_amount, 'mooring_group': mooring_group, 'oracle_code': str(ob.campsite.mooringarea.oracle_code)})
                      cancellation_fees.append({'additional_fees': 'true', 'description': 'Refund - '+description,'amount': str(ob.amount - ob.amount - ob.amount), 'mooring_group': mooring_group, 'oracle_code': str(ob.campsite.mooringarea.oracle_code)})
                      #cancellation_fees.append({'additional_fees': 'true', 'description': 'Cancel Fee - '+description,'amount': cancel_fee_amount, 'mooring_group': mooring_group})
                      #cancellation_fees.append({'additional_fees': 'true', 'description': 'Refund - '+description,'amount': str(ob.amount - ob.amount - ob.amount), 'mooring_group': mooring_group})
         else:

             print ("NO CANCELATION POLICY")

         #else:
         #    adjustment_fee = ob.amount + adjustment_fee
    #change_fees.append({'additional_fees': 'true', 'description': 'Mooring Adjustment Credit' ,'amount': str(adjustment_fee - adjustment_fee - adjustment_fee)})

    return cancellation_fees



def calculate_price_booking_change(old_booking, new_booking,overide_change_fees=False):
    nowtime =  datetime.today()
    nowtimec = datetime.strptime(nowtime.strftime('%Y-%m-%d'),'%Y-%m-%d')

    old_booking_mooring = MooringsiteBooking.objects.filter(booking=old_booking)
    booking_changes = MooringsiteBooking.objects.filter(booking=new_booking)
    change_fees = []
    adjustment_fee = Decimal('0.00')
    mg = MooringAreaGroup.objects.all()
    #{'additional_fees': 'true', 'description': 'Booking Change Fee','amount': Decimal('0.00')}

    for ob in old_booking_mooring:
         changed = True
         for bc in booking_changes:
             if bc.campsite == ob.campsite and ob.from_dt == bc.from_dt and ob.to_dt == bc.to_dt and ob.booking_period_option == bc.booking_period_option:
                changed = False
         from_dt = datetime.strptime(ob.from_dt.strftime('%Y-%m-%d'),'%Y-%m-%d')
         daystillbooking =  (from_dt-nowtimec).days
         refund_policy = None

         for i in mg:
            if i.moorings.count() > 0:
                    mooring_group = i.moorings.all()[0].id


         if changed is True:
             change_fee_amount = '0.00' 
 #            change_price_period = ChangePricePeriod.objects.filter(id=ob.booking_period_option.change_group_id).order_by('-days')
             change_group =  ChangeGroup.objects.get(id=ob.booking_period_option.change_group_id)
             change_price_period = change_group.change_period.all().order_by('days')
             for cpp in change_price_period:
                  if daystillbooking < 0:
                       daystillbooking = 0
#                  if cpp.days >= daystillbooking:
                  if daystillbooking >= cpp.days:
                      refund_policy =cpp
             if refund_policy:
                if refund_policy.calulation_type == 0:
                    # Percentage
                    change_fee_amount = float(ob.amount) * (refund_policy.percentage / 100)
                elif refund_policy.calulation_type == 1: 
                    change_fee_amount = refund_policy.amount
                    # Fixed Pricing

                description = 'Mooring {} ({} - {})'.format(ob.campsite.mooringarea.name,ob.from_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'),ob.to_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'))

                if overide_change_fees is True:
                     change_fees.append({'additional_fees': 'true', 'description': 'Refund - '+description,'amount': str(format(ob.amount - ob.amount - ob.amount, '.2f')), 'oracle_code': str(ob.campsite.mooringarea.oracle_code), 'mooring_group': mooring_group, 'line_status': 3})
                else:
                       #change_fees['amount'] = str(refund_amount)
                     #change_fees.append({'additional_fees': 'true', 'description': 'Change Fee - '+description,'amount': float(change_fee_amount), 'oracle_code': str(ob.campsite.mooringarea.oracle_code), 'mooring_group': mooring_group})
                     #change_fees.append({'additional_fees': 'true', 'description': 'Refund - '+description,'amount': str(ob.amount - ob.amount - ob.amount), 'oracle_code': str(ob.campsite.mooringarea.oracle_code), 'mooring_group': mooring_group})
                     change_fees.append({'additional_fees': 'true', 'description': 'Change Fee - '+description,'amount': str(format(change_fee_amount, '.2f')), 'oracle_code': str(ob.campsite.mooringarea.oracle_code), 'mooring_group': mooring_group, 'line_status': 2})
                     change_fees.append({'additional_fees': 'true', 'description': 'Refund - '+description,'amount': str(format(ob.amount - ob.amount - ob.amount, '.2f')), 'oracle_code': str(ob.campsite.mooringarea.oracle_code), 'mooring_group': mooring_group, 'line_status': 3})
             else:
                 print ("NO REFUND POLICY")
               
         else:
             #description = 'Mooring {} ({} - {})'.format(ob.campsite.mooringarea.name,ob.from_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'),ob.to_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'))
             adjustment_fee = float('0.00')
             adjustment_fee = float(ob.amount) + adjustment_fee
             description = 'Mooring {} ({} - {})'.format(ob.campsite.mooringarea.name,ob.from_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'),ob.to_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'))
#             change_fees.append({'additional_fees': 'true', 'description': 'Adjustment - '+description ,'amount': str(adjustment_fee - adjustment_fee - adjustment_fee), 'oracle_code': str(ob.campsite.mooringarea.oracle_code), 'mooring_group': mooring_group})   
             change_fees.append({'additional_fees': 'true', 'description': 'Adjustment - '+description ,'amount': str(format(adjustment_fee - adjustment_fee - adjustment_fee, '.2f')), 'oracle_code': str(ob.campsite.mooringarea.oracle_code), 'mooring_group': mooring_group, 'line_status': 3})

    return change_fees

def calculate_price_admissions_cancel(adBooking, change_fees, overide_cancel_fees=False):
    ad_lines = AdmissionsLine.objects.filter(admissionsBooking=adBooking)
    for line in ad_lines:
        if line.arrivalDate > date.today() or overide_cancel_fees is True:
            

            description = "Admission ({}) for {} guest(s)".format(datetime.strftime(line.arrivalDate, '%d/%m/%Y'), adBooking.total_admissions)
            oracle_code = AdmissionsOracleCode.objects.filter(mooring_group=line.location.mooring_group)[0]
    
            change_fees.append({'additional_fees': 'true', 'description': 'Refund - ' +  description,'amount': str(line.cost - line.cost - line.cost), 'oracle_code': str(oracle_code.oracle_code), 'mooring_group': line.location.mooring_group.id, 'line_status': 3})
    return change_fees


def calculate_price_admissions_change(adBooking, change_fees):
    ad_lines = AdmissionsLine.objects.filter(admissionsBooking=adBooking)
    for line in ad_lines:
          
        description = "Admission ({}) for {} guest(s)".format(datetime.strftime(line.arrivalDate, '%d/%m/%Y'), adBooking.total_admissions)
        oracle_code = AdmissionsOracleCode.objects.filter(mooring_group=line.location.mooring_group)[0]
        
        # Fees
        change_fees.append({'additional_fees': 'true', 'description': 'Adjustment - ' +  description,'amount': str(line.cost - line.cost - line.cost), 'oracle_code': str(oracle_code.oracle_code), 'mooring_group': line.location.mooring_group.id, 'line_status': 3 })


    return change_fees

def price_or_lineitems(request,booking,campsite_list,lines=True,old_booking=None):
    total_price = Decimal(0)
    booking_mooring = MooringsiteBooking.objects.filter(booking=booking)
    booking_mooring_old = []
    if booking.old_booking:
        booking_mooring_old = MooringsiteBooking.objects.filter(booking=booking.old_booking)

    invoice_lines = []
    if lines:
        for bm in booking_mooring:
            line_status = 1
            amount = bm.amount
            if str(bm.id) in booking.override_lines:
                amount = Decimal(booking.override_lines[str(bm.id)])
            for ob in booking_mooring_old:
                if bm.campsite == ob.campsite and ob.from_dt == bm.from_dt and ob.to_dt == bm.to_dt and ob.booking_period_option == bm.booking_period_option:
                      line_status = 2
            invoice_lines.append({'ledger_description':'Mooring {} ({} - {})'.format(bm.campsite.mooringarea.name,bm.from_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'),bm.to_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p')),"quantity":1,"price_incl_tax":amount,"oracle_code":bm.campsite.mooringarea.oracle_code, 'line_status': line_status})



#            invoice_lines.append({'ledger_description':'Mooring {} ({} - {})'.format(bm.campsite.mooringarea.name,bm.from_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p'),bm.to_dt.astimezone(pytimezone('Australia/Perth')).strftime('%d/%m/%Y %H:%M %p')),"quantity":1,"price_incl_tax":bm.amount,"oracle_code":bm.campsite.mooringarea.oracle_code})
        return invoice_lines
    else:
        return total_price

def price_or_lineitems_extras(request,booking,change_fees,invoice_lines=[]):
    total_price = Decimal(0)
    booking_mooring = MooringsiteBooking.objects.filter(booking=booking)
    for cf in change_fees:
#       invoice_lines.append({'ledger_description':cf['description'],"quantity":1,"price_incl_tax":cf['amount'],"oracle_code":cf['oracle_code']})
       invoice_lines.append({'ledger_description':cf['description'],"quantity":1,"price_incl_tax":cf['amount'],"oracle_code":cf['oracle_code'], 'line_status': cf['line_status']})
    return invoice_lines 

def old_price_or_lineitems(request,booking,campsite_list,lines=True,old_booking=None):
    total_price = Decimal(0)
    rate_list = {}
    invoice_lines = []
    if not lines and not old_booking:
        raise Exception('An old booking is required if lines is set to false')
    # Create line items for customers
    daily_rates = [get_campsite_current_rate(request,c,booking.arrival.strftime('%Y-%m-%d'),booking.departure.strftime('%Y-%m-%d')) for c in campsite_list]
    if not daily_rates:
        raise Exception('There was an error while trying to get the daily rates.')
    for rates in daily_rates:
        for c in rates:
            if c['rate']['campsite'] not in rate_list.keys():
                rate_list[c['rate']['campsite']] = {c['rate']['id']:{'start':c['date'],'end':c['date'],'mooring': c['rate']['mooring'] ,'adult':c['rate']['adult'],'concession':c['rate']['concession'],'child':c['rate']['child'],'infant':c['rate']['infant']}}
            else:
                if c['rate']['id'] not in rate_list[c['rate']['campsite']].keys():
                    rate_list[c['rate']['campsite']] = {c['rate']['id']:{'start':c['date'],'end':c['date'],'mooring': c['rate']['mooring'], 'adult':c['rate']['adult'],'concession':c['rate']['concession'],'child':c['rate']['child'],'infant':c['rate']['infant']}}
                else:
                    rate_list[c['rate']['campsite']][c['rate']['id']]['end'] = c['date']
    # Get Guest Details
    #guests = {}
    #for k,v in booking.details.items():
    #    if 'num_' in k:
    #        guests[k.split('num_')[1]] = v
    ##### Above is for poeple quantity (mooring are not based on people.. based on vessels)

    # guess is used as the quantity items for the check out basket.
    guests = {}
    guests['mooring'] = 1
    for k,v in guests.items():
        if int(v) > 0:
            for c,p in rate_list.items():
                for i,r in p.items():
                    price = Decimal(0)
                    end = datetime.strptime(r['end'],"%Y-%m-%d").date()
                    start = datetime.strptime(r['start'],"%Y-%m-%d").date()
                    num_days = int ((end - start).days) + 1
                    campsite = Mooringsite.objects.get(id=c)
                    if lines:
                        price = str((num_days * Decimal(r[k])))
                        #if not booking.mooringarea.oracle_code:
                        #    raise Exception('The mooringarea selected does not have an Oracle code attached to it.')
                        end_date = end + timedelta(days=1)
#                        invoice_lines.append({'ledger_description':'Mooring fee {} ({} - {})'.format(k,start.strftime('%d-%m-%Y'),end_date.strftime('%d-%m-%Y')),"quantity":v,"price_incl_tax":price,"oracle_code":booking.mooringarea.oracle_code})
                        invoice_lines.append({'ledger_description':'Admission fee on {} ({}) {}'.format(adLine.arrivalDate, group, overnightStay),"quantity":amount,"price_incl_tax":price, "oracle_code":oracle_code, 'line_status': 1})
                    else:
                        price = (num_days * Decimal(r[k])) * v
                        total_price += price
    # Create line items for vehicles
    if lines:
        vehicles = booking.regos.all()
    else:
        vehicles = old_booking.regos.all()
    if vehicles:
        if booking.mooringarea.park.entry_fee_required:
            # Update the booking vehicle regos with the park entry requirement
            vehicles.update(park_entry_fee=True)
            if not booking.mooringarea.park.oracle_code:
                raise Exception('A marine park entry Oracle code has not been set for the park that the mooringarea belongs to.')
        park_entry_rate = get_park_entry_rate(request,booking.arrival.strftime('%Y-%m-%d'))
        vehicle_dict = {
            'vessel' : vehicles.filter(entry_fee=True, type='vessel'),
            #'vehicle': vehicles.filter(entry_fee=True, type='vehicle'),
            'motorbike': vehicles.filter(entry_fee=True, type='motorbike'),
            'concession': vehicles.filter(entry_fee=True, type='concession')
        }

        for k,v in vehicle_dict.items():
            if v.count() > 0:
                if lines:
                    price =  park_entry_rate[k]
                    regos = ', '.join([x[0] for x in v.values_list('rego')])
                    invoice_lines.append({
                        'ledger_description': 'Mooring fee - {}'.format(k),
                        'quantity': v.count(),
                        'price_incl_tax': price,
                        'oracle_code': booking.mooringarea.park.oracle_code
                    })
                else:
                    price =  Decimal(park_entry_rate[k]) * v.count()
                    total_price += price
    if lines:
        return invoice_lines
    else:
        return total_price

def get_admissions_entry_rate(request,start_date, location):
    res = []
    if start_date:
        start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
        group = location.mooring_group
        price_history = AdmissionsRate.objects.filter(mooring_group__in=[group,], period_start__lte = start_date).order_by('-period_start')
        if price_history:
            serializer = AdmissionsRateSerializer(price_history,many=True,context={'request':request})
            res = serializer.data[0]
    return res

def admissions_price_or_lineitems(request, admissionsBooking,lines=True):
    total_price = Decimal(0)
    rate_list = {}
    invoice_lines = []
    line = lines
    daily_rates = []
    # Create line items for customers
    admissionsLines = AdmissionsLine.objects.filter(admissionsBooking=admissionsBooking)
    for adLine in admissionsLines:
        rate = get_admissions_entry_rate(request,adLine.arrivalDate.strftime('%Y-%m-%d'), adLine.location)
        daily_rate = {'date' : adLine.arrivalDate.strftime('%d/%m/%Y'), 'rate' : rate}
        daily_rates.append(daily_rate)
        oracle_codes = AdmissionsOracleCode.objects.filter(mooring_group__in=[adLine.location.mooring_group,])
        if not oracle_codes.count() > 0:
            if request.user.is_staff:
                raise Exception('Admissions Oracle Code missing, please set up in administration tool.')
            else:
                raise Exception('Please alert {} of the following error message:\nAdmissions Oracle Code missing.'.format(adLine['group']))
    if not daily_rates or daily_rates == []:
        raise Exception('There was an error while trying to get the daily rates.')
    family = 0
    adults = admissionsBooking.noOfAdults
    children = admissionsBooking.noOfChildren
    if adults > 1 and children > 1:
        if adults == children:
            if adults % 2 == 0:
                family = adults/2
                adults = 0
                children = 0
            else:
                adults -= 1
                family = adults/2
                adults = 1
                children = 1

        elif adults > children: #Adults greater - tickets based on children
            if children % 2 == 0:
                family = children/2
                adults -= children
                children = 0
            else:
                children -= 1
                family = children/2
                adults -= children
                children = 1
        else: #Children greater - tickets based on adults
            if adults % 2 == 0:
                family = adults/2
                children -= adults
                adults = 0
            else:
                adults -= 1
                family = adults/2
                children -= adults
                adults = 1
    people = {'Adults': adults,'Concessions': admissionsBooking.noOfConcessions,'Children': children,'Infants': admissionsBooking.noOfInfants, 'Family': family}

    for adLine in admissionsLines:
        for group, amount in people.items():
            if line:
                if (amount > 0):
                    if group == 'Adults':
                        gr = 'adult'
                    elif group == 'Children':
                        gr = group
                    elif group == 'Infants':
                        gr = 'infant'
                    elif group == 'Family':
                        gr = 'family'
                    if adLine.overnightStay:
                        costfield = gr.lower() + "_overnight_cost"
                        overnightStay = "Overnight Included"
                    else:
                        costfield = gr.lower() + "_cost"
                        overnightStay = "Day Visit Only"
                    daily_rate = next(item for item in daily_rates if item['date'] == adLine.arrivalDate.strftime('%d/%m/%Y'))['rate']
                    price = daily_rate.get(costfield)
                    oracle_codes = AdmissionsOracleCode.objects.filter(mooring_group=adLine.location.mooring_group)
                    if oracle_codes.count() > 0:
                        oracle_code = oracle_codes[0].oracle_code
                    invoice_lines.append({'ledger_description':'Admission fee on {} ({}) {}'.format(adLine.arrivalDate, group, overnightStay),"quantity":amount,"price_incl_tax":price, "oracle_code":oracle_code, 'line_status': 1})
                
            else:
                daily_rate = daily_rates[adLine.arrivalDate.strftime('%d/%m/%Y')]
                price = Decimal(daily_rate)
                total_cost += price
    if line:
        return invoice_lines
    else:
        return total_price

def check_date_diff(old_booking,new_booking):
    if old_booking.arrival == new_booking.arrival and old_booking.departure == new_booking.departure:
        return 4 # same days
    elif old_booking.arrival == new_booking.arrival:
        old_booking_days = int((old_booking.departure - old_booking.arrival).days)
        new_days = int((new_booking.departure - new_booking.arrival).days)
        if new_days > old_booking_days:
            return 1 #additional days
        else:
            return 2 #reduced days
    elif old_booking.departure == new_booking.departure:
        old_booking_days = int((old_booking.departure - old_booking.arrival).days)
        new_days = int((new_booking.departure - new_booking.arrival).days)
        if new_days > old_booking_days:
            return 1 #additional days
        else:
            return 2 #reduced days
    else:
        return 3 # different days

def get_diff_days(old_booking,new_booking,additional=True):
    if additional:
        return int((new_booking.departure - old_booking.departure).days)
    return int((old_booking.departure - new_booking.departure).days)

def create_temp_bookingupdate(request,arrival,departure,booking_details,old_booking,total_price):
    # delete all the campsites in the old moving so as to transfer them to the new booking
    old_booking.campsites.all().delete()
    booking = create_booking_by_site(booking_details['campsites'],
            start_date = arrival,
            end_date = departure,
            num_adult = booking_details['num_adult'],
            num_concession= booking_details['num_concession'],
            num_child= booking_details['num_child'],
            num_infant= booking_details['num_infant'],
            num_mooring = booking_details['num_mooring'],
            cost_total = total_price,
            customer = old_booking.customer,
            override_price=old_booking.override_price,
            updating_booking = True,
            override_checks=True
    )
    # Move all the vehicles to the new booking
    for r in old_booking.regos.all():
        r.booking = booking
        r.save()
    
    lines = price_or_lineitems(request,booking,booking.campsite_id_list)
    booking_arrival = booking.arrival.strftime('%d-%m-%Y')
    booking_departure = booking.departure.strftime('%d-%m-%Y')
    reservation = u'Reservation for {} confirmation PS{}'.format(
            u'{} {}'.format(booking.customer.first_name, booking.customer.last_name), booking.id)
    # Proceed to generate invoice

    checkout_response = checkout(request,booking,lines,invoice_text=reservation,internal=True)

    # FIXME: replace with session check
    invoice = None
    if 'invoice=' in checkout_response.url:
        invoice = checkout_response.url.split('invoice=', 1)[1]
    else:
        for h in reversed(checkout_response.history):
            if 'invoice=' in h.url:
                invoice = h.url.split('invoice=', 1)[1]
                break
    
    # create the new invoice
    new_invoice = internal_create_booking_invoice(booking, invoice)

    # Check if the booking is a legacy booking and doesn't have an invoice
    if old_booking.legacy_id and old_booking.invoices.count() < 1:
        # Create a cash transaction in order to fix the outstnding invoice payment
        CashTransaction.objects.create(
            invoice = Invoice.objects.get(reference=new_invoice.invoice_reference),
            amount = old_booking.cost_total,
            type = 'move_in',
            source = 'cash',
            details = 'Transfer of funds from migrated booking',
            movement_reference='Migrated Booking Funds'
        )
        # Update payment details for the new invoice
        update_payments(new_invoice.invoice_reference)

    # Attach new invoices to old booking
    for i in old_booking.invoices.all():
        inv = Invoice.objects.get(reference=i.invoice_reference)
        inv.voided = True
        #transfer to the new invoice
        inv.move_funds(inv.transferable_amount,Invoice.objects.get(reference=new_invoice.invoice_reference),'Transfer of funds from {}'.format(inv.reference))
        inv.save()
    # Change the booking for the selected invoice
    new_invoice.booking = old_booking
    new_invoice.save()

    return booking

def iiiicreate_temp_bookingupdate(request,arrival,departure,booking_details,old_booking,total_price):
    # delete all the campsites in the old moving so as to transfer them to the new booking
    old_booking.campsites.all().delete()
    booking = create_booking_by_site(booking_details['campsites'][0],
            start_date = arrival,
            end_date = departure,
            num_adult = booking_details['num_adult'],
            num_concession= booking_details['num_concession'],
            num_child= booking_details['num_child'],
            num_infant= booking_details['num_infant'],
            num_mooring = booking_details['num_mooring'],
            cost_total = total_price,
            customer = old_booking.customer,
            updating_booking = True
    )

    # Move all the vehicles to the new booking
    for r in old_booking.regos.all():
        r.booking = booking
        r.save()
    
    lines = price_or_lineitems(request,booking,booking.campsite_id_list)
    booking_arrival = booking.arrival.strftime('%d-%m-%Y')
    booking_departure = booking.departure.strftime('%d-%m-%Y')
    reservation = "Reservation for {} from {} to {} at {}".format('{} {}'.format(booking.customer.first_name,booking.customer.last_name),booking_arrival,booking_departure,booking.mooringarea.name)

    # Proceed to generate invoice
    checkout_response = checkout(request,booking,lines,invoice_text=reservation,internal=True)
    internal_create_booking_invoice(booking, checkout_response)
    
    # Get the new invoice
    new_invoice = booking.invoices.first()

    # Check if the booking is a legacy booking and doesn't have an invoice
    if old_booking.legacy_id and old_booking.invoices.count() < 1:
        # Create a cash transaction in order to fix the outstnding invoice payment
        CashTransaction.objects.create(
            invoice = Invoice.objects.get(reference=new_invoice.invoice_reference),
            amount = old_booking.cost_total,
            type = 'move_in',
            source = 'cash',
            details = 'Transfer of funds from migrated booking',
            movement_reference='Migrated Booking Funds'
        )
        # Update payment details for the new invoice
        update_payments(new_invoice.invoice_reference)

    # Attach new invoices to old booking
    for i in old_booking.invoices.all():
        inv = Invoice.objects.get(reference=i.invoice_reference)
        inv.voided = True
        #transfer to the new invoice
        inv.move_funds(inv.transferable_amount,Invoice.objects.get(reference=new_invoice.invoice_reference),'Transfer of funds from {}'.format(inv.reference))
        inv.save()
    # Change the booking for the selected invoice
    new_invoice.booking = old_booking
    new_invoice.save()
    return booking

def update_booking(request,old_booking,booking_details):
    same_dates = False
    same_campsites = False
    same_campground = False
    same_details = False
    same_vehicles = True

    with transaction.atomic():
        try:
            set_session_booking(request.session, old_booking)
            new_details = {}
            new_details.update(old_booking.details)
            # Update the guests
            new_details['num_adult'] =  booking_details['num_adult']
            new_details['num_concession'] = booking_details['num_concession']
            new_details['num_child'] = booking_details['num_child']
            new_details['num_infant'] = booking_details['num_infant']
            booking = Booking(
                arrival = booking_details['start_date'],
                departure =booking_details['end_date'],
                details = new_details,
                customer=old_booking.customer,
                mooringarea = MooringArea.objects.get(id=booking_details['mooringarea']))
            # Check that the departure is not less than the arrival
            if booking.departure < booking.arrival:
                raise Exception('The departure date cannot be before the arrival date')
            today = datetime.now().date()
            if today > old_booking.departure:
                raise ValidationError('You cannot change a booking past the departure date.')
            # Check if it is the same campground
            if old_booking.mooringarea.id == booking.mooringarea.id:
                same_campground = True
            # Check if dates are the same
            if (old_booking.arrival == booking.arrival) and (old_booking.departure == booking.departure):
                same_dates = True
            # Check if the campsite is the same
            if sorted(old_booking.campsite_id_list) == sorted(booking_details['campsites']):
                same_campsites = True
            # Check if the details have changed
            if new_details == old_booking.details:
                same_details = True
            # Check if the vehicles have changed
            current_regos = old_booking.regos.all()
            current_vehicle_regos= sorted([r.rego for r in current_regos])

            # Add history
            new_history = old_booking._generate_history(user=request.user)
            
            if request.data.get('entryFees').get('regos'):
                new_regos = request.data['entryFees'].pop('regos')
                sent_regos = [r['rego'] for r in new_regos]
                regos_serializers = []
                update_regos_serializers = []
                for n in new_regos:
                    if n['rego'] not in current_vehicle_regos:
                        n['booking'] = old_booking.id
                        regos_serializers.append(BookingRegoSerializer(data=n))
                        same_vehicles = False
                    else:
                        booking_rego = BookingVehicleRego.objects.get(booking=old_booking,rego=n['rego'])
                        n['booking'] = old_booking.id
                        if booking_rego.type != n['type'] or booking_rego.entry_fee != n['entry_fee']:
                            update_regos_serializers.append(BookingRegoSerializer(booking_rego,data=n))
                # Create the new regos if they are there
                if regos_serializers:
                    for r in regos_serializers:
                        r.is_valid(raise_exception=True)
                        r.save()
                # Update the new regos if they are there
                if update_regos_serializers:
                    for r in update_regos_serializers:
                        r.is_valid(raise_exception=True)
                        r.save()
                    same_vehicles = False

                # Check if there are regos in place that need to be removed
                stale_regos = []
                for r in current_regos:
                    if r.rego not in sent_regos:
                        stale_regos.append(r.id)
                # delete stale regos
                if stale_regos:
                    same_vehicles = False
                    BookingVehicleRego.objects.filter(id__in=stale_regos).delete()
            else:
                same_vehicles = False
                if current_regos:
                    current_regos.delete()

            if same_campsites and same_dates and same_vehicles and same_details:
                if new_history is not None:
                   new_history.delete()
                return old_booking

            # Check difference of dates in booking
            old_booking_days = int((old_booking.departure - old_booking.arrival).days)
            new_days = int((booking_details['end_date'] - booking_details['start_date']).days)
            date_diff = check_date_diff(old_booking,booking)

            total_price = price_or_lineitems(request,booking,booking_details['campsites'],lines=False,old_booking=old_booking)
            price_diff = True
            if old_booking.cost_total != total_price:
                price_diff = True
            if price_diff:

                booking = create_temp_bookingupdate(request,booking.arrival,booking.departure,booking_details,old_booking,total_price)
                # Attach campsite booking objects to old booking
                for c in booking.campsites.all():
                    c.booking = old_booking
                    c.save()
                # Move all the vehicles to the in new booking to the old booking
                for r in booking.regos.all():
                    r.booking = old_booking
                    r.save()
                old_booking.cost_total = booking.cost_total
                old_booking.departure = booking.departure
                old_booking.arrival = booking.arrival
                old_booking.details.update(booking.details)
                if not same_campground:
                    old_booking.campground = booking.campground
                old_booking.save()
                booking.delete()
            delete_session_booking(request.session)
            send_booking_invoice(old_booking)
            # send out the confirmation email if the booking is paid or over paid
            if old_booking.status == 'Paid' or old_booking.status == 'Over Paid':
                send_booking_confirmation(old_booking,request)
            return old_booking
        except:
            delete_session_booking(request.session)
            print(traceback.print_exc())
            raise

def create_or_update_booking(request,booking_details,updating=False,override_checks=False):
    booking = None
    if not updating:
        booking = create_booking_by_site(booking_details['campsites'],
            start_date = booking_details['start_date'],
            end_date=booking_details['end_date'],
            num_adult=booking_details['num_adult'],
            num_concession=booking_details['num_concession'],
            num_child=booking_details['num_child'],
            num_infant=booking_details['num_infant'],
            num_mooring=booking_details['num_mooring'],
            vessel_size=booking_details['vessel_size'],
            cost_total=booking_details['cost_total'],
            override_price=booking_details['override_price'],
            override_reason=booking_details['override_reason'],
            override_reason_info=booking_details['override_reason_info'],
            overridden_by=booking_details['overridden_by'],
            customer=booking_details['customer'],
            override_checks=override_checks
        )
        
        booking.details['first_name'] = booking_details['first_name']
        booking.details['last_name'] = booking_details['last_name']
        booking.details['phone'] = booking_details['phone']
        booking.details['country'] = booking_details['country']
        booking.details['postcode'] = booking_details['postcode']

        # Add booking regos
        if 'regos' in booking_details:
            regos = booking_details['regos']
            for r in regos:
                r['booking'] = booking.id
            regos_serializers = [BookingRegoSerializer(data=r) for r in regos]
            for r in regos_serializers:
                r.is_valid(raise_exception=True)
                r.save()
        booking.save()
    return booking

def old_create_or_update_booking(request,booking_details,updating=False):
    booking = None
    if not updating:
        booking = create_booking_by_site(campsite_id= booking_details['campsite_id'],
            start_date = booking_details['start_date'],
            end_date=booking_details['end_date'],
            num_adult=booking_details['num_adult'],
            num_concession=booking_details['num_concession'],
            num_child=booking_details['num_child'],
            num_infant=booking_details['num_infant'],
            num_mooring=booking_details['num_mooring'],
            vessel_size=booking_details['vessel_size'],
            cost_total=booking_details['cost_total'],
            customer=booking_details['customer'])
        
        booking.details['first_name'] = booking_details['first_name']
        booking.details['last_name'] = booking_details['last_name']
        booking.details['phone'] = booking_details['phone']
        booking.details['country'] = booking_details['country']
        booking.details['postcode'] = booking_details['postcode']

        # Add booking regos
        if request.data.get('parkEntry').get('regos'):
            regos = request.data['parkEntry'].pop('regos')
            for r in regos:
                r[u'booking'] = booking.id
            regos_serializers = [BookingRegoSerializer(data=r) for r in regos]
            for r in regos_serializers:
                r.is_valid(raise_exception=True)
                r.save()
        booking.save()
    return booking

def admissionsCheckout(request, admissionsBooking, lines, invoice_text=None, vouchers=[], internal=False):
    basket_params = {
        'products': lines,
        'vouchers': vouchers,
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'custom_basket': True,
    }
    
    basket, basket_hash = create_basket_session(request, basket_params)
    checkout_params = {
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'fallback_url': request.build_absolute_uri('/'),
        'return_url': request.build_absolute_uri(reverse('public_admissions_success')),
        'return_preload_url': request.build_absolute_uri(reverse('public_admissions_success')),
        'force_redirect': True,
        'proxy': True if internal else False,
        'invoice_text': invoice_text,
    }
    
    if internal or request.user.is_anonymous():
        checkout_params['basket_owner'] = admissionsBooking.customer.id
    create_checkout_session(request, checkout_params)

    if internal:
        responseJson = place_order_submission(request)
    else:
        print(reverse('checkout:index'))
        responseJson = HttpResponse(geojson.dumps({'status': 'success','redirect': reverse('checkout:index'),}), content_type='application/json')
        # response = HttpResponseRedirect(reverse('checkout:index'))

        # inject the current basket into the redirect response cookies
        # or else, anonymous users will be directionless
        responseJson.set_cookie(
            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
        )
    return responseJson

def get_basket(request):
    return get_cookie_basket(settings.OSCAR_BASKET_COOKIE_OPEN,request)


def checkout(request, booking, lines, invoice_text=None, vouchers=[], internal=False):
    basket_params = {
        'products': lines,
        'vouchers': vouchers,
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'custom_basket': True,
    }
 
    basket, basket_hash = create_basket_session(request, basket_params)
    checkout_params = {
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'fallback_url': request.build_absolute_uri('/'),
        'return_url': request.build_absolute_uri(reverse('public_booking_success')),
        'return_preload_url': request.build_absolute_uri(reverse('public_booking_success')),
        'force_redirect': True,
        'proxy': True if internal else False,
        'invoice_text': invoice_text,
    }
#    if not internal:
#        checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
    if internal or request.user.is_anonymous():
        checkout_params['basket_owner'] = booking.customer.id


    create_checkout_session(request, checkout_params)



#    if internal:
#        response = place_order_submission(request)
#    else:
    response = HttpResponseRedirect(reverse('checkout:index'))
    # inject the current basket into the redirect response cookies
    # or else, anonymous users will be directionless
    response.set_cookie(
            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
    )

    if booking.cost_total < 0:
        response = HttpResponseRedirect('/refund-payment')
        response.set_cookie(
            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
        )

    # Zero booking costs
    if booking.cost_total < 1 and booking.cost_total > -1:
        response = HttpResponseRedirect('/no-payment')
        response.set_cookie(
            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
        )
    return response


def allocate_failedrefund_to_unallocated(request, booking, lines, invoice_text=None, internal=False, order_total='0.00',user=None):
        basket_params = {
            'products': lines,
            'vouchers': [],
            'system': settings.PS_PAYMENT_SYSTEM_ID,
            'custom_basket': True,
        }

        basket, basket_hash = create_basket_session(request, basket_params)
        ci = utils.CreateInvoiceBasket()
        order  = ci.create_invoice_and_order(basket, total=None, shipping_method='No shipping required',shipping_charge=False, user=user, status='Submitted', invoice_text='Refund Allocation Pool', )
        #basket.status = 'Submitted'
        #basket.save()
        #new_order = Order.objects.get(basket=basket)
        new_invoice = Invoice.objects.get(order_number=order.number)
        update_payments(new_invoice.reference)
        if booking.__class__.__name__ == 'AdmissionsBooking':
            print ("AdmissionsBooking")
            book_inv, created = AdmissionsBookingInvoice.objects.get_or_create(admissions_booking=booking, invoice_reference=new_invoice.reference, system_invoice=True)
        else:
            book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=new_invoice.reference, system_invoice=True)

        return order

def allocate_refund_to_invoice(request, booking, lines, invoice_text=None, internal=False, order_total='0.00',user=None):

        basket_params = {
            'products': lines,
            'vouchers': [],
            'system': settings.PS_PAYMENT_SYSTEM_ID,
            'custom_basket': True,
        }

        basket, basket_hash = create_basket_session(request, basket_params)
        ci = utils.CreateInvoiceBasket()
        order  = ci.create_invoice_and_order(basket, total=None, shipping_method='No shipping required',shipping_charge=False, user=user, status='Submitted', invoice_text='Oracle Allocation Pools', )
        #basket.status = 'Submitted'
        #basket.save()
        #new_order = Order.objects.get(basket=basket)
        new_invoice = Invoice.objects.get(order_number=order.number)
        update_payments(new_invoice.reference)
        if booking.__class__.__name__ == 'AdmissionsBooking':
            print ("AdmissionsBooking")
            book_inv, created = AdmissionsBookingInvoice.objects.get_or_create(admissions_booking=booking, invoice_reference=new_invoice.reference, system_invoice=True)
        else:
            book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=new_invoice.reference, system_invoice=True)

        return order

def old_internal_create_booking_invoice(booking, checkout_response):
    if not checkout_response.history:
        raise Exception('There was a problem retrieving the invoice for this booking')
    last_redirect = checkout_response.history[-2]
    reference = last_redirect.url.split('=')[1]
    try:
        Invoice.objects.get(reference=reference)
    except Invoice.DoesNotExist:
        raise Exception("There was a problem attaching an invoice for this booking")
    book_inv = BookingInvoice.objects.get_or_create(booking=booking,invoice_reference=reference)
    return book_inv

def internal_create_booking_invoice(booking, reference):
    try:
        Invoice.objects.get(reference=reference)
    except Invoice.DoesNotExist:
        raise Exception("There was a problem attaching an invoice for this booking")
    book_inv = BookingInvoice.objects.get_or_create(booking=booking,invoice_reference=reference)
    return book_inv



def internal_booking(request,booking_details,internal=True,updating=False):
    json_booking = request.data
    booking = None
    try:
        booking = create_or_update_booking(request, booking_details, updating, override_checks=internal)
        with transaction.atomic():
            set_session_booking(request.session,booking)
            # Get line items
            booking_arrival = booking.arrival.strftime('%d-%m-%Y')
            booking_departure = booking.departure.strftime('%d-%m-%Y')
            reservation = u"Reservation for {} confirmation PS{}".format(u'{} {}'.format(booking.customer.first_name,booking.customer.last_name), booking.id)
            lines = price_or_lineitems(request,booking,booking.campsite_id_list)

            # Proceed to generate invoice
            checkout_response = checkout(request,booking,lines,invoice_text=reservation,internal=True)
            # Change the type of booking
            booking.booking_type = 0
            booking.save()

            # FIXME: replace with session check
            invoice = None
            if 'invoice=' in checkout_response.url:
                invoice = checkout_response.url.split('invoice=', 1)[1]
            else:
                for h in reversed(checkout_response.history):
                    if 'invoice=' in h.url:
                        invoice = h.url.split('invoice=', 1)[1]
                        break
            print ("-== internal_booking ==-")
            internal_create_booking_invoice(booking, invoice)
            delete_session_booking(request.session)
            send_booking_invoice(booking)
            return booking

    except:
        if booking: 
            booking.delete()
        raise


def old_internal_booking(request,booking_details,internal=True,updating=False):
    json_booking = request.data
    booking = None
    try:
        booking = create_or_update_booking(request,booking_details,updating)
        with transaction.atomic():
            set_session_booking(request.session,booking)
            # Get line items
            booking_arrival = booking.arrival.strftime('%d-%m-%Y')
            booking_departure = booking.departure.strftime('%d-%m-%Y')
            reservation = u"Reservation for {} from {} to {} at {}".format(u'{} {}'.format(booking.customer.first_name,booking.customer.last_name),booking_arrival,booking_departure,booking.mooringarea.name)
            lines = price_or_lineitems(request,booking,booking.campsite_id_list)

            # Proceed to generate invoice
            checkout_response = checkout(request,booking,lines,invoice_text=reservation,internal=True)
            # Change the type of booking
            booking.booking_type = 0
            booking.save()
            internal_create_booking_invoice(booking, checkout_response)
            delete_session_booking(request.session)
            send_booking_invoice(booking)
            return booking

    except:
        if booking: 
            booking.delete()
        raise

def set_session_booking(session, booking):
    session['ps_booking'] = booking.id
    session.modified = True

def get_session_admissions_booking(session):
    if 'ad_booking' in session:
        booking_id = session['ad_booking']
    else:
        raise Exception('Admissions booking not in Session')

    try:
        return AdmissionsBooking.objects.get(id=booking_id)
    except AdmissionsBooking.DoesNotExist:
        raise Exception('Admissions booking not found for booking_id {}'.format(booking_id))


def delete_session_admissions_booking(session):
    if 'ad_booking' in session:
        del session['ad_booking']
        session.modified = True

def get_session_booking(session):
    if 'ps_booking' in session:
        booking_id = session['ps_booking']
    else:
        raise Exception('Booking not in Session')

    try:
        return Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        raise Exception('Booking not found for booking_id {}'.format(booking_id))

def delete_session_booking(session):
    if 'ps_booking' in session:
        del session['ps_booking']
        session.modified = True

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def oracle_integration(date,override):
    system = '0516'
    oracle_codes = oracle_parser_on_invoice(date,system,'Mooring Booking',override=override)

def admissions_lines(booking_mooring):
    lines = []
    for bm in booking_mooring:
        # Convert the from and to dates of this booking to just plain dates in local time.
        # Append them to a list.
        if bm.campsite.mooringarea.park.entry_fee_required:
            from_dt = bm.from_dt
            timestamp = calendar.timegm(from_dt.timetuple())
            local_dt = datetime.fromtimestamp(timestamp)
            from_dt = local_dt.replace(microsecond=from_dt.microsecond)
            to_dt = bm.to_dt
            timestamp = calendar.timegm(to_dt.timetuple())
            local_dt = datetime.fromtimestamp(timestamp)
            to_dt = local_dt.replace(microsecond=to_dt.microsecond)
            group = MooringAreaGroup.objects.filter(moorings__in=[bm.campsite.mooringarea,])[0].id
            lines.append({'from': from_dt, 'to': to_dt, 'group':group})
    # Sort the list by date from.
    new_lines = sorted(lines, key=lambda line: line['from'])
    i = 0
    lines = []
    latest_from = None
    latest_to = None
    # Loop through the list, if first instance, then this line's from date is the first admission fee.
    # Then compare this TO value to the next FROM value. If they are not the same or overlapping dates
    # add this date to the list, using the latest from and this TO value.
    while i < len(new_lines):
        if i == 0:
            latest_from = new_lines[i]['from'].date()
        if i < len(new_lines)-1:
            if new_lines[i]['to'].date() < new_lines[i+1]['from'].date():
                latest_to = new_lines[i]['to'].date()
        else:
            # if new_lines[i]['from'].date() > new_lines[i-1]['to'].date():
            latest_to = new_lines[i]['to'].date()
        
        if latest_to:
            lines.append({"rowid":'admission_fee_id'+str(i), 'id': i,'from':datetime.strftime(latest_from, '%d %b %Y'), 'to': datetime.strftime(latest_to, '%d %b %Y'), 'admissionFee': 0, 'group': new_lines[i]['group']})
            if i < len(new_lines)-1:
                latest_from = new_lines[i+1]['from'].date()
                latest_to = None
        i+= 1
    return lines

# Access Level check for Group   
def mooring_group_access_level_change(pk,request):
     mooring_groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
     if request.user.is_superuser is True:
          return True
     else:
          if ChangeGroup.objects.filter(pk=pk,mooring_group__in=mooring_groups).count() > 0:
              return True

     return False

def mooring_group_access_level_cancel(pk,request):
     mooring_groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
     if request.user.is_superuser is True:
          return True
     else:
          if CancelGroup.objects.filter(pk=pk,mooring_group__in=mooring_groups).count() > 0:
              return True

     return False

def mooring_group_access_level_change_options(cg,pk,request):
     mooring_groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
     if request.user.is_superuser is True:
          return True
     else:
          cpp = ChangePricePeriod.objects.get(id=pk)
          if ChangeGroup.objects.filter(id=cg,change_period__in=[cpp],mooring_group__in=mooring_groups).count() > 0:
              return True

     return False

def mooring_group_access_level_cancel_options(cg,pk,request):
     mooring_groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
     if request.user.is_superuser is True:
          return True
     else:
          cpp = CancelPricePeriod.objects.get(id=pk)
          if CancelGroup.objects.filter(id=cg,cancel_period__in=[cpp],mooring_group__in=mooring_groups).count() > 0:
              return True

     return False
 
def mooring_group_access_level_booking_period(pk,request):
     mooring_groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
     if request.user.is_superuser is True:
          return True
     else:
          if BookingPeriod.objects.filter(pk=pk,mooring_group__in=mooring_groups).count() > 0:
              return True
    
     return False

def mooring_group_access_level_booking_period_option(pk,bp_group_id,request):
     mooring_groups = MooringAreaGroup.objects.filter(members__in=[request.user,])
     if request.user.is_superuser is True:
          return True
     else:
          bpo = BookingPeriodOption.objects.get(id=pk)
          if BookingPeriod.objects.filter(pk=bp_group_id,booking_period__in=[bpo],mooring_group__in=mooring_groups).count() > 0:
              return True
     return False


def check_mooring_admin_access(request): 
    if request.user.is_superuser is True:
        return True
    else:
      if request.user.groups.filter(name__in=['Mooring Admin']).exists():
          return True
    return False


