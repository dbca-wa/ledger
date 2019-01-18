from datetime import datetime, timedelta, date
import traceback
from decimal import *
import json
import requests
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils import timezone

from ledger.payments.models import Invoice,OracleInterface,CashTransaction
from ledger.payments.utils import oracle_parser,update_payments
from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission
from mooring.models import (MooringArea, Mooringsite, MooringsiteRate, MooringsiteBooking, Booking, BookingInvoice, MooringsiteBookingRange, Rate, MooringAreaBookingRange,MooringAreaStayHistory, MooringsiteRate, MarinaEntryRate, BookingVehicleRego)
from mooring.serialisers import BookingRegoSerializer, MooringsiteRateSerializer, MarinaEntryRateSerializer, RateSerializer, MooringsiteRateReadonlySerializer
from mooring.emails import send_booking_invoice,send_booking_confirmation


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
        availability = get_campsite_availability(campsite_qs, start_date, end_date)
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
                raise ValidationError('Maximum number of people exceeded for the selected campsite(s)')
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

def get_open_marinas(campsites_qs, start_date, end_date):
    """Fetch the set of Marine Parks (from a set of Mooring Sites) with spaces open over a range of visit dates."""
    # short circuit: if start date is before today, return nothing
    today = date.today()
    if start_date < today:
        return set()

    # remove from the campsite list any entries with bookings
    campsites_qs = campsites_qs.exclude(
        mooringsitebooking__date__range=(start_date, end_date-timedelta(days=1))
    # and also campgrounds where the book window is outside of the max advance range
    ).exclude(
        #campground__max_advance_booking__lte=(start_date-today).days - 1 
        mooringarea__max_advance_booking__lt=(start_date-today).days 
    )

    # get closures at campsite and campground level
    cgbr_qs = MooringAreaBookingRange.objects.filter(
        Q(campground__in=[x[0] for x in campsites_qs.distinct('mooringarea').values_list('mooringarea')]),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
    )
#    cgbr = set([x[0] for x in cgbr_qs.values_list('campground')])
    cgbr = set([x[0] for x in cgbr_qs.values_list('campground')])


    csbr_qs = MooringsiteBookingRange.objects.filter(
        #Q(campsite__in=campsites_qs),
        Q(status=1),
        #Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
    )
    csbr = set([x[0] for x in csbr_qs.values_list('campsite')])

    # generate a campground-to-campsite-list map with closures removed
    mooring_map = {}
    for cs in campsites_qs:
        if (cs.pk in csbr) or (cs.mooringarea.pk in cgbr):
            continue
        if cs.mooringarea.pk not in mooring_map:
            mooring_map[cs.mooringarea.pk] = []
        mooring_map[cs.mooringarea.pk].append(cs.pk)

    return set(mooring_map.keys())


def get_campsite_availability(campsites_qs, start_date, end_date):
    """Fetch the availability of each campsite in a queryset over a range of visit dates."""
    # fetch all of the single-day MooringsiteBooking objects within the date range for the sites
    bookings_qs =   MooringsiteBooking.objects.filter(
                        campsite__in=campsites_qs,
                        date__gte=start_date,
                        date__lt=end_date
                    ).order_by('date', 'campsite__name')

    # prefill all slots as 'open'
    duration = (end_date-start_date).days
    results = {site.pk: {start_date+timedelta(days=i): ['open', ] for i in range(duration)} for site in campsites_qs}
    # strike out existing bookings
    for b in bookings_qs:
        results[b.campsite.pk][b.date][0] = 'closed' if b.booking_type == 2 else 'booked'

    # generate a campground-to-campsite-list map
    mooring_map = {cg[0]: [cs.pk for cs in campsites_qs if cs.mooringarea.pk == cg[0]] for cg in campsites_qs.distinct('mooringarea').values_list('mooringarea')}
    # strike out whole campground closures
    cgbr_qs =    MooringAreaBookingRange.objects.filter(
        Q(campground__in=mooring_map.keys()),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
    )
    for closure in cgbr_qs:
        start = max(start_date, closure.range_start)
        end = min(end_date, closure.range_end) if closure.range_end else end_date
        today = date.today()
        diff = (end-start).days + 1
        for i in range(diff):
            for cs in mooring_map[closure.campground.pk]:
                #results[cs][start+timedelta(days=i)][0] = 'closed'
                if start+timedelta(days=i) == today:
                    if not closure.campground._is_open(start+timedelta(days=i)):
                        if start+timedelta(days=i) in results[cs]:
                            results[cs][start+timedelta(days=i)][0] = 'closed'
                else:
                    if start+timedelta(days=i) in results[cs]:
                        results[cs][start+timedelta(days=i)][0] = 'closed'
    # strike out campsite closures
    csbr_qs =    MooringsiteBookingRange.objects.filter(
        Q(campsite__in=campsites_qs),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
    )
    for closure in csbr_qs:
        start = max(start_date, closure.range_start)
        end = min(end_date, closure.range_end) if closure.range_end else end_date
        today = date.today()
        diff = (end-start).days + 1
        for i in range(diff):
            #results[closure.campsite.pk][start+timedelta(days=i)][0] = 'closed'
            if start+timedelta(days=i) == today:
                if not closure.campsite._is_open(start+timedelta(days=i)):
                    if start+timedelta(days=i) in results[closure.campsite.pk]:
                        results[closure.campsite.pk][start+timedelta(days=i)][0] = 'closed'
            else:
                if start+timedelta(days=i) in results[closure.campsite.pk]:
                    results[closure.campsite.pk][start+timedelta(days=i)][0] = 'closed'
                
    # strike out days before today
    today = date.today()
    if start_date < today:
        for i in range((min(today, end_date)-start_date).days):
            for key, val in results.items():
                val[start_date+timedelta(days=i)][0] = 'tooearly'

    # strike out days after the max_advance_booking
    for site in campsites_qs:
        stop = today + timedelta(days=site.mooringarea.max_advance_booking)
        stop_mark = min(max(stop, start_date), end_date)
        if start_date > stop:
            for i in range((end_date-stop_mark).days):
                results[site.pk][stop_mark+timedelta(days=i)][0] = 'toofar'
    # Get the current stay history
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
        stop = start_date + timedelta(days=max_days)
        stop_mark = min(max(stop, start_date), end_date)
        for i in range((end_date-stop_mark).days):
            results[site.pk][stop_mark+timedelta(days=i)][0] = 'toofar'
    return results


def get_visit_rates(campsites_qs, start_date, end_date):
    """Fetch the per-day pricing for each visitor type over a range of visit dates."""
    # fetch the applicable rates for the campsites
    rates_qs = MooringsiteRate.objects.filter(
        Q(campsite__in=campsites_qs),
        Q(date_start__lt=end_date) & (Q(date_end__gte=start_date)|Q(date_end__isnull=True))
    ).prefetch_related('rate')

    # prefill all slots
    duration = (end_date-start_date).days
    results = {
        site.pk: {
            start_date+timedelta(days=i): {
                'mooring':  Decimal('0.00'),
                'adult': Decimal('0.00'),
                'child': Decimal('0.00'),
                'concession': Decimal('0.00'),
                'infant': Decimal('0.00')
            } for i in range(duration)
        } for site in campsites_qs
    }

    # make a record of the earliest MooringsiteRate for each site
    early_rates = {}
    for rate in rates_qs:
        if rate.campsite.pk not in early_rates:
            early_rates[rate.campsite.pk] = rate
        elif early_rates[rate.campsite.pk].date_start > rate.date_start:
            early_rates[rate.campsite.pk] = rate

        # for the period of the visit overlapped by the rate, set the amounts
        start = max(start_date, rate.date_start)
        end = min(end_date, rate.date_end) if rate.date_end else end_date
        for i in range((end-start).days):
            results[rate.campsite.pk][start+timedelta(days=i)]['mooring'] = rate.rate.mooring
            results[rate.campsite.pk][start+timedelta(days=i)]['adult'] = rate.rate.adult
            results[rate.campsite.pk][start+timedelta(days=i)]['concession'] = rate.rate.concession
            results[rate.campsite.pk][start+timedelta(days=i)]['child'] = rate.rate.child
            results[rate.campsite.pk][start+timedelta(days=i)]['infant'] = rate.rate.infant

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
                results[site_pk][start+timedelta(days=i)]['mooring'] = rate.rate.mooring
                results[site_pk][start+timedelta(days=i)]['adult'] = rate.rate.adult
                results[site_pk][start+timedelta(days=i)]['concession'] = rate.rate.concession
                results[site_pk][start+timedelta(days=i)]['child'] = rate.rate.child
                results[site_pk][start+timedelta(days=i)]['infant'] = rate.rate.infant

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


def price_or_lineitems(request,booking,campsite_list,lines=True,old_booking=None):
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
                        invoice_lines.append({'ledger_description':'Mooring fee {} ({} - {})'.format(k,start.strftime('%d-%m-%Y'),end_date.strftime('%d-%m-%Y')),"quantity":v,"price_incl_tax":price,"oracle_code":booking.mooringarea.oracle_code})
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
    if not internal:
        checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
    if internal or request.user.is_anonymous():
        checkout_params['basket_owner'] = booking.customer.id
    create_checkout_session(request, checkout_params)

    if internal:
        response = place_order_submission(request)
    else:
        response = HttpResponseRedirect(reverse('checkout:index'))
        # inject the current basket into the redirect response cookies
        # or else, anonymous users will be directionless
        response.set_cookie(
            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
        )
    return response

def iiicheckout(request, booking, lines, invoice_text=None, vouchers=[], internal=False):
    JSON_REQUEST_HEADER_PARAMS = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Referer": request.META.get('HTTP_REFERER'),
        "X-CSRFToken": request.COOKIES.get('csrftoken')
    }
    try:
        parameters = {
            'system': 'S019',
            'fallback_url': request.build_absolute_uri('/'),
            'return_url': request.build_absolute_uri(reverse('public_booking_success')),
            'forceRedirect': True,
            'proxy': True if internal else False,
            "products": lines,
            "custom_basket": True,
            "invoice_text": invoice_text,
            "vouchers": vouchers,
        }

        if not internal:
            parameters["check_url"] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
        if internal or request.user.is_anonymous():
            parameters['basket_owner'] = booking.customer.id

        url = request.build_absolute_uri(
            reverse('payments:ledger-initial-checkout')
        )
        COOKIES = request.COOKIES
        if 'ps_booking' in request.session:
            COOKIES['ps_booking_internal'] = str(request.session['ps_booking'])
        response = requests.post(url, headers=JSON_REQUEST_HEADER_PARAMS, cookies=COOKIES,
                                 data=json.dumps(parameters))
        response.raise_for_status()
        return response


    except requests.exceptions.HTTPError as e:
        if 400 <= e.response.status_code < 500:
            http_error_msg = '{} Client Error: {} for url: {} > {}'.format(e.response.status_code, e.response.reason, e.response.url,e.response._content)

        elif 500 <= e.response.status_code < 600:
            http_error_msg = '{} Server Error: {} for url: {}'.format(e.response.status_code, e.response.reason, e.response.url)
        e.message = http_error_msg

        e.args = (http_error_msg,)
        raise

def old_internal_create_booking_invoice(booking, checkout_response):
    if not checkout_response.history:
        raise Exception('There was a problem retrieving the invoice for this booking')
    last_redirect = checkout_response.history[-2]
    reference = last_redirect.url.split('=')[1]
    try:
        Invoice.objects.get(reference=reference)
    except Invoice.DoesNotExist:
        raise Exception("There was a problem attaching an invoice for this booking")
    book_inv = BookingInvoice.objects.create(booking=booking,invoice_reference=reference)
    return book_inv

def internal_create_booking_invoice(booking, reference):
    try:
        Invoice.objects.get(reference=reference)
    except Invoice.DoesNotExist:
        raise Exception("There was a problem attaching an invoice for this booking")
    book_inv = BookingInvoice.objects.create(booking=booking,invoice_reference=reference)
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
    oracle_codes = oracle_parser(date,system,'Mooring Booking',override=override)
