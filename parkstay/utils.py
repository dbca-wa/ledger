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
from django.utils import timezone

from ledger.payments.models import Invoice,OracleInterface
from ledger.payments.utils import oracle_parser
from parkstay.models import (Campground, Campsite, CampsiteRate, CampsiteBooking, Booking, BookingInvoice, CampsiteBookingRange, Rate, CampgroundBookingRange, CampsiteRate, ParkEntryRate)
from parkstay.serialisers import BookingRegoSerializer, CampsiteRateSerializer, ParkEntryRateSerializer,RateSerializer,CampsiteRateReadonlySerializer
from parkstay.emails import send_booking_invoice


def create_booking_by_class(campground_id, campsite_class_id, start_date, end_date, num_adult=0, num_concession=0, num_child=0, num_infant=0):
    """Create a new temporary booking in the system."""
    # get campground
    campground = Campground.objects.get(pk=campground_id)

    # TODO: date range check business logic
    # TODO: number of people check? this is modifiable later, don't bother

    # the CampsiteBooking table runs the risk of a race condition,
    # wrap all this behaviour up in a transaction
    with transaction.atomic():

        # fetch all the campsites and applicable rates for the campground
        sites_qs =  Campsite.objects.filter(
                        campground=campground,
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
            raise ValidationError('Campsite class unavailable for specified time period.')

        # TODO: add campsite sorting logic based on business requirements
        # for now, pick the first campsite in the list
        site = sites[0]

        # Create a new temporary booking with an expiry timestamp (default 20mins)
        booking =   Booking.objects.create(
                        booking_type=3,
                        arrival=start_date,
                        departure=end_date,
                        details={
                            'num_adult': num_adult,
                            'num_concession': num_concession,
                            'num_child': num_child,
                            'num_infant': num_infant
                        },
                        expiry_time=timezone.now()+timedelta(seconds=settings.BOOKING_TIMEOUT),
                        campground=campground
                    )
        for i in range((end_date-start_date).days):
            cb =    CampsiteBooking.objects.create(
                        campsite=site,
                        booking_type=3,
                        date=start_date+timedelta(days=i),
                        booking=booking
                    )

    # On success, return the temporary booking
    return booking


def create_booking_by_site(campsite_id, start_date, end_date, num_adult=0, num_concession=0, num_child=0, num_infant=0,cost_total=0,customer=None):
    """Create a new temporary booking in the system for a specific campsite."""
    # get campsite
    sites_qs = Campsite.objects.filter(pk=campsite_id)
    campsite = sites_qs.first()

    # TODO: date range check business logic
    # TODO: number of people check? this is modifiable later, don't bother

    # the CampsiteBooking table runs the risk of a race condition,
    # wrap all this behaviour up in a transaction
    with transaction.atomic():
        # get availability for campsite, error out if booked/closed
        availability = get_campsite_availability(sites_qs, start_date, end_date)
        for site_id, dates in availability.items():
            if not all([v[0] == 'open' for k, v in dates.items()]):
                raise ValidationError('Campsite unavailable for specified time period.')

        # Create a new temporary booking with an expiry timestamp (default 20mins)
        booking =   Booking.objects.create(
                        booking_type=3,
                        arrival=start_date,
                        departure=end_date,
                        details={
                            'num_adult': num_adult,
                            'num_concession': num_concession,
                            'num_child': num_child,
                            'num_infant': num_infant
                        },
                        cost_total= Decimal(cost_total),
                        expiry_time=timezone.now()+timedelta(seconds=settings.BOOKING_TIMEOUT),
                        campground=campsite.campground,
                        customer = customer
                    )
        for i in range((end_date-start_date).days):
            cb =    CampsiteBooking.objects.create(
                        campsite=campsite,
                        booking_type=3,
                        date=start_date+timedelta(days=i),
                        booking=booking
                    )

    # On success, return the temporary booking
    return booking


def get_open_campgrounds(campsites_qs, start_date, end_date):
    """Fetch the set of campgrounds (from a set of campsites) with spaces open over a range of visit dates."""
    # short circuit: if start date is before today, return nothing
    today = date.today()
    if start_date < today:
        return set()

    # remove from the campsite list any entries with bookings
    campsites_qs = campsites_qs.exclude(
        campsitebooking__date__range=(start_date, end_date-timedelta(days=1))
    # and also campgrounds where the book window is outside of the max advance range
    ).exclude(
        campground__max_advance_booking__lte=(end_date-today).days
    )

    # get closures at campsite and campground level
    cgbr_qs =    CampgroundBookingRange.objects.filter(
        Q(campground__in=[x[0] for x in campsites_qs.distinct('campground').values_list('campground')]),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
    )
    cgbr = set([x[0] for x in cgbr_qs.values_list('campground')])

    csbr_qs =    CampsiteBookingRange.objects.filter(
        Q(campsite__in=campsites_qs),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
    )
    csbr = set([x[0] for x in csbr_qs.values_list('campsite')])

    # generate a campground-to-campsite-list map with closures removed
    campground_map = {}
    for cs in campsites_qs:
        if (cs.pk in csbr) or (cs.campground.pk in cgbr):
            continue
        if cs.campground.pk not in campground_map:
            campground_map[cs.campground.pk] = []
        campground_map[cs.campground.pk].append(cs.pk)

    return set(campground_map.keys())


def get_campsite_availability(campsites_qs, start_date, end_date):
    """Fetch the availability of each campsite in a queryset over a range of visit dates."""
    # fetch all of the single-day CampsiteBooking objects within the date range for the sites
    bookings_qs =   CampsiteBooking.objects.filter(
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
    campground_map = {cg[0]: [cs.pk for cs in campsites_qs if cs.campground.pk == cg[0]] for cg in campsites_qs.distinct('campground').values_list('campground')}

    # strike out whole campground closures
    cgbr_qs =    CampgroundBookingRange.objects.filter(
        Q(campground__in=campground_map.keys()),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
    )
    for closure in cgbr_qs:
        start = max(start_date, closure.range_start)
        end = min(end_date, closure.range_end)
        for i in range((end-start).days):
            for cs in campground_map[closure.campground.pk]:
                results[cs][start+timedelta(days=i)][0] = 'closed'

    # strike out campsite closures
    csbr_qs =    CampsiteBookingRange.objects.filter(
        Q(campsite__in=campsites_qs),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date)|Q(range_end__isnull=True))
    )
    for closure in csbr_qs:
        start = max(start_date, closure.range_start)
        end = min(end_date, closure.range_end) if closure.range_end else end_date
        for i in range((end-start).days):
            results[closure.campsite.pk][start+timedelta(days=i)][0] = 'closed'

    # strike out days before today
    today = date.today()
    if start_date < today:
        for i in range((min(today, end_date)-start_date).days):
            for key, val in results.items():
                val[start_date+timedelta(days=i)][0] = 'tooearly'

    # strike out days after the max_advance_booking
    for site in campsites_qs:
        stop = today + timedelta(days=site.campground.max_advance_booking)
        stop_mark = min(max(stop, start_date), end_date)
        for i in range((end_date-stop_mark).days):
            results[site.pk][stop_mark+timedelta(days=i)][0] = 'toofar'

    return results


def get_visit_rates(campsites_qs, start_date, end_date):
    """Fetch the per-day pricing for each visitor type over a range of visit dates."""
    # fetch the applicable rates for the campsites
    rates_qs = CampsiteRate.objects.filter(
        Q(campsite__in=campsites_qs),
        Q(date_start__lt=end_date) & (Q(date_end__gte=start_date)|Q(date_end__isnull=True))
    ).prefetch_related('rate')

    # prefill all slots
    duration = (end_date-start_date).days
    results = {
        site.pk: {
            start_date+timedelta(days=i): {
                'adult': Decimal('0.00'),
                'child': Decimal('0.00'),
                'concession': Decimal('0.00'),
                'infant': Decimal('0.00')
            } for i in range(duration)
        } for site in campsites_qs
    }

    # make a record of the earliest CampsiteRate for each site
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
            results[rate.campsite.pk][start+timedelta(days=i)]['adult'] = rate.rate.adult
            results[rate.campsite.pk][start+timedelta(days=i)]['concession'] = rate.rate.concession
            results[rate.campsite.pk][start+timedelta(days=i)]['child'] = rate.rate.child
            results[rate.campsite.pk][start+timedelta(days=i)]['infant'] = rate.rate.infant

    # complain if there's a Campsite without a CampsiteRate
    if len(early_rates) < rates_qs.count():
        print('Missing CampsiteRate coverage!')
    # for ease of testing against the old datasets, if the visit dates are before the first
    # CampsiteRate date, use that CampsiteRate as the pricing model.
    for site_pk, rate in early_rates.items():
        if start_date < rate.date_start:
            start = start_date
            end = rate.date_start
            for i in range((end-start).days):
                results[site_pk][start+timedelta(days=i)]['adult'] = rate.rate.adult
                results[site_pk][start+timedelta(days=i)]['concession'] = rate.rate.concession
                results[site_pk][start+timedelta(days=i)]['child'] = rate.rate.child
                results[site_pk][start+timedelta(days=i)]['infant'] = rate.rate.infant

    return results

def get_available_campsitetypes(campground_id,start_date,end_date,_list=True):
    try:
        cg = Campground.objects.get(id=campground_id)

        if _list:
            available_campsiteclasses = []
        else:
            available_campsiteclasses = {}

        for _class in cg.campsite_classes:
            sites_qs =  Campsite.objects.filter(
                            campground=campground_id,
                            campsite_class=_class
                        )

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
    except Campground.DoesNotExist:
        raise Exception('The campsite you are searching does not exist')
    except:
        raise


def get_available_campsites_list(campsite_qs,request, start_date, end_date):
    from parkstay.serialisers import CampsiteSerialiser
    campsites = get_campsite_availability(campsite_qs, start_date, end_date)
    available = []
    for camp in campsites:
        av = [item for sublist in campsites[camp].values() for item in sublist]
        if ('booked' not in av):
            if ('closed' not in av):
                available.append(CampsiteSerialiser(Campsite.objects.filter(id = camp),many=True,context={'request':request}).data[0])

    return available

def get_campsite_current_rate(request,campsite_id,start_date,end_date):
    res = []
    if start_date and end_date:
        start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
        end_date = datetime.strptime(end_date,"%Y-%m-%d").date()
        for single_date in daterange(start_date, end_date):
            price_history = CampsiteRate.objects.filter(campsite=campsite_id,date_start__lte=single_date).order_by('-date_start')
            if price_history:
                rate = RateSerializer(price_history[0].rate,context={'request':request}).data
                rate['campsite'] = campsite_id
                res.append({
                    "date" : single_date.strftime("%Y-%m-%d") ,
                    "rate" : rate
                })
    return res

def get_park_entry_rate(request,start_date):
    res = []
    if start_date:
        start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
        price_history = ParkEntryRate.objects.filter(period_start__lte = start_date).order_by('-period_start')
        if price_history:
            serializer = ParkEntryRateSerializer(price_history,many=True,context={'request':request})
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
                rate_list[c['rate']['campsite']] = {c['rate']['id']:{'start':c['date'],'end':c['date'],'adult':c['rate']['adult'],'concession':c['rate']['concession'],'child':c['rate']['child'],'infant':c['rate']['infant']}}
            else:
                if c['rate']['id'] not in rate_list[c['rate']['campsite']].keys():
                    rate_list[c['rate']['campsite']] = {c['rate']['id']:{'start':c['date'],'end':c['date'],'adult':c['rate']['adult'],'concession':c['rate']['concession'],'child':c['rate']['child'],'infant':c['rate']['infant']}}
                else:
                    rate_list[c['rate']['campsite']][c['rate']['id']]['end'] = c['date']
    # Get Guest Details
    guests = {}
    for k,v in booking.details.items():
        if 'num_' in k:
            guests[k.split('num_')[1]] = v
    for k,v in guests.items():
        if int(v) > 0:
            for c,p in rate_list.items():
                for i,r in p.items():
                    price = Decimal(0)
                    end = datetime.strptime(r['end'],"%Y-%m-%d").date()
                    start = datetime.strptime(r['start'],"%Y-%m-%d").date()
                    num_days = int ((end - start).days) + 1
                    campsite = Campsite.objects.get(id=c)
                    if lines:
                        price = str((num_days * Decimal(r[k])))
                        if not booking.campground.oracle_code:
                            raise Exception('The campground selected does not have an Oracle code attached to it.')
                        invoice_lines.append({'ledger_description':'Campsite {} for {} ({} - {})'.format(campsite.name,k,start.strftime('%d-%m-%Y'),end.strftime('%d-%m-%Y')),"quantity":v,"price_incl_tax":price,"oracle_code":booking.campground.oracle_code})
                    else:
                        price = (num_days * Decimal(r[k])) * v
                        total_price += price
    # Create line items for vehicles
    if lines:
        vehicles = booking.regos.all()
    else:
        vehicles = old_booking.regos.all()
    if vehicles:
        if booking.campground.park.entry_fee_required and not booking.campground.park.oracle_code:
            raise Exception('A park entry Oracle code has not been set for the park that the campground belongs to.')
        park_entry_rate = get_park_entry_rate(request,booking.arrival.strftime('%Y-%m-%d'))
        vehicle_dict = {
            'vehicle': vehicles.filter(entry_fee=True, type='vehicle'),
            'motorbike': vehicles.filter(entry_fee=True, type='motorbike'),
            'concession': vehicles.filter(entry_fee=True, type='concession')
        }

        for k,v in vehicle_dict.items():
            if v.count() > 0:
                if lines:
                    price =  park_entry_rate[k]
                    regos = ', '.join([x[0] for x in v.values_list('rego')])
                    invoice_lines.append({
                        'ledger_description': 'Park Entry - {}'.format(k),
                        'quantity': v.count(),
                        'price_incl_tax': price,
                        'oracle_code': booking.campground.park.oracle_code
                    })
                else:
                    price =  Decimal(park_entry_rate[k]) * v.count()
                    total_price += price
    if lines:
        return invoice_lines
    else:
        return total_price

def check_date_diff(old_booking,new_booking):
    if old_booking.arrival == new_booking.arrival:
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

def create_temp_bookingupdate(request,arrival,departure,booking_details,old_booking,total_price,void_invoices=False):
    booking = create_booking_by_site(booking_details['campsites'][0],
            start_date = arrival,
            end_date = departure,
            num_adult = old_booking.details['num_adult'],
            num_concession= old_booking.details['num_concession'],
            num_child= old_booking.details['num_child'],
            num_infant= old_booking.details['num_infant'],
            cost_total = total_price,
            customer = old_booking.customer
    )
    lines = price_or_lineitems(request,booking,booking.campsite_id_list)
    booking_arrival = booking.arrival.strftime('%d-%m-%Y')
    booking_departure = booking.departure.strftime('%d-%m-%Y')
    reservation = "Reservation for {} from {} to {} at {}".format('{} {}'.format(booking.customer.first_name,booking.customer.last_name),booking_arrival,booking_departure,booking.campground.name)
    # Proceed to generate invoice
    checkout_response = checkout(request,booking,lines,invoice_text=reservation,internal=True)
    internal_create_booking_invoice(booking, checkout_response)

    # Attach new invoices to old booking
    if void_invoices:
        for i in old_booking.invoices.all():
            inv = Invoice.objects.get(reference=i.invoice_reference)
            inv.voided = True
            inv.save()
    for i in booking.invoices.all():
        i.booking = old_booking
        i.save()

    return booking

def update_booking(request,old_booking,booking_details):
    same_dates = False
    same_campsites = False
    same_campground = False
    with transaction.atomic():
        try:
            set_session_booking(request.session, old_booking)
            booking = Booking(
                arrival = booking_details['start_date'],
                departure =booking_details['end_date'],
                details = old_booking.details,
                customer=old_booking.customer,
                campground = Campground.objects.get(id=booking_details['campground']))
            # Check that the departure is not less than the arrival
            if booking.departure < booking.arrival:
                raise Exception('The departure date cannot be before the arrival date')

            # Check if it is the same campground
            if old_booking.campground.id == booking.campground.id:
                same_campground = True
            # Check if dates are the same
            if (old_booking.arrival == booking.arrival) and (old_booking.departure == booking.departure):
                same_dates = True
            # Check if the campsite is the same
            if old_booking.campsite_id_list.sort() == booking_details['campsites'].sort():
                same_campsites = True

            if same_campsites and same_dates:
                return old_booking

            # Check difference of dates in booking
            old_booking_days = int((old_booking.departure - old_booking.arrival).days)
            new_days = int((booking_details['end_date'] - booking_details['start_date']).days)
            date_diff = check_date_diff(old_booking,booking)

            total_price = price_or_lineitems(request,booking,booking_details['campsites'],lines=False,old_booking=old_booking)
            price_diff = False
            if old_booking.cost_total != total_price:
                price_diff = True

            if price_diff:
                if total_price > old_booking.cost_total:
                    if date_diff == 1: # Additional days
                        if same_campsites:
                            new_arrival = old_booking.departure
                            new_departure = new_arrival + timedelta(days=get_diff_days(old_booking,booking))

                            booking = create_temp_bookingupdate(request,new_arrival,new_departure,booking_details,old_booking,total_price)

                        else:
                            booking = create_temp_bookingupdate(request,booking.arrival,booking.departure,booking_details,old_booking,total_price)
                            old_booking.campsites.all().delete()

                        # Attach campsite booking objects to old booking
                        for c in booking.campsites.all():
                            c.booking = old_booking
                            c.save()
                        old_booking.cost_total = booking.cost_total
                        old_booking.departure = booking.departure
                        if not same_campground:
                            old_booking.campground = booking.campground
                        old_booking.save()
                        booking.delete()
                elif total_price < old_booking.cost_total:
                    if date_diff == 2: # Less days
                        if same_campsites:
                            old_booking.cost_total = total_price
                            # Remove extra campsite bookings
                            if booking.departure < old_booking.departure:
                                old_booking.campsites.filter(date__gte=booking.departure).delete()
                            elif booking.arrival > old_booking.arrival:
                                old_booking.campsites.filter(date__lte=booking.arrival).delete()
                            for i in old_booking.invoices.all():
                                inv = Invoice.objects.get(reference=i.invoice_reference)
                                inv.voided = True
                                inv.save()
                            # Generate New Invoice
                            lines = price_or_lineitems(request,old_booking,old_booking.campsite_id_list)
                            old_booking_arrival = datetime.strptime(old_booking.arrival,"%Y-%m-%d").date().strftime('%d-%m-%Y')
                            booking_departure = datetime.strptime(booking.departure,"%Y-%m-%d").date().strftime('%d-%m-%Y')
                            reservation = "Reservation for {} from {} to {} at {}".format('{} {}'.format(old_booking.customer.first_name,old_booking.customer.last_name),old_booking_arrival,booking_departure,old_booking.campground.name)
                            # Proceed to generate invoice
                            checkout_response = checkout(request,old_booking,lines,invoice_text=reservation,internal=True)
                            internal_create_booking_invoice(booking, checkout_response)
                        else:
                            booking = create_temp_bookingupdate(request,booking.arrival,booking.departure,booking_details,old_booking,total_price)
                            old_booking.campsites.all().delete()
                            # Attach campsite booking objects to old booking
                            for c in booking.campsites.all():
                                c.booking = old_booking
                                c.save()

                            old_booking.cost_total = booking.cost_total
                        old_booking.departure = booking.departure
                        old_booking.arrival = booking.arrival
                        if not same_campground:
                            old_booking.campground = booking.campground
                        old_booking.save()
                        if not same_campsites:
                            booking.delete()

            if date_diff == 3: # Different Days
                booking = create_temp_bookingupdate(request,booking.arrival,booking.departure,booking_details,old_booking,total_price,void_invoices=True)
                old_booking.campsites.all().delete()
                # Attach campsite booking objects to old booking
                for c in booking.campsites.all():
                    c.booking = old_booking
                    c.save()

                old_booking.cost_total = booking.cost_total
                old_booking.departure = booking.departure
                old_booking.arrival = booking.arrival
                if not same_campground:
                    old_booking.campground = booking.campground
                old_booking.save()
                booking.delete()
            delete_session_booking(request.session)
            send_booking_invoice(booking)
            return old_booking
        except:
            delete_session_booking(request.session)
            print(traceback.print_exc())
            raise

def create_or_update_booking(request,booking_details,updating=False):
    booking = None
    if not updating:
        booking = create_booking_by_site(campsite_id= booking_details['campsite_id'],
            start_date = booking_details['start_date'],
            end_date=booking_details['end_date'],
            num_adult=booking_details['num_adult'],
            num_concession=booking_details['num_concession'],
            num_child=booking_details['num_child'],
            num_infant=booking_details['num_infant'],
            cost_total=booking_details['cost_total'],
            customer=booking_details['customer'])
        
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
        booking.booking_type = 1
        booking.save()
    return booking

def checkout(request, booking, lines, invoice_text=None, vouchers=[], internal=False):
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
            "vouchers": vouchers
        }
        if internal or request.user.is_anonymous():
            parameters['basket_owner'] = booking.customer.id


        url = request.build_absolute_uri(
            reverse('payments:ledger-initial-checkout')
        )
        COOKIES = request.COOKIES
        if 'ps_booking' in request.session:
            COOKIES['ps_booking_internal'] = str(request.session['ps_booking'])
        response = requests.post(url, headers=JSON_REQUEST_HEADER_PARAMS, cookies=request.COOKIES,
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


def internal_create_booking_invoice(booking, checkout_response):
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


def internal_booking(request,booking_details,internal=True,updating=False):
    json_booking = request.data
    try:
        with transaction.atomic():
            booking = create_or_update_booking(request,booking_details,updating)
            set_session_booking(request.session,booking)
            # Get line items
            booking_arrival = booking.arrival.strftime('%d-%m-%Y')
            booking_departure = booking.departure.strftime('%d-%m-%Y')
            reservation = "Reservation for {} from {} to {} at {}".format('{} {}'.format(booking.customer.first_name,booking.customer.last_name),booking_arrival,booking_departure,booking.campground.name)
            lines = price_or_lineitems(request,booking,booking.campsite_id_list)

            # Proceed to generate invoice
            checkout_response = checkout(request,booking,lines,invoice_text=reservation,internal=True)
            internal_create_booking_invoice(booking, checkout_response)
            delete_session_booking(request.session)
            send_booking_invoice(booking)
            return booking

    except:
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


def oracle_integration(date):
    system = '0019'
    oracle_codes = oracle_parser(date,system,'Parkstay')
