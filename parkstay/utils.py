from datetime import datetime, timedelta

from decimal import *

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q    
from django.utils import timezone

from parkstay.models import (Campground, Campsite, CampsiteRate, CampsiteBooking, Booking, CampsiteBookingRange, CampgroundBookingRange)


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
            raise ValidationError('No matching campsites found')

        # get availability for sites, filter out the non-clear runs
        availability = get_campsite_availability(sites_qs, start_date, end_date)
        excluded_site_ids = set()
        for site_id, dates in availability.items():
            if not all([v[0] == 'open' for k, v in dates.items()]):
                excluded_site_ids.add(site_id)
    
        # create a list of campsites without bookings for that period
        sites = [x for x in sites_qs if x.pk not in excluded_site_ids]

        if not sites:
            raise ValidationError('Campsite class unavailable for specified time period')

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
    

def create_booking_by_site(campsite_id, start_date, end_date, num_adult=0, num_concession=0, num_child=0, num_infant=0):
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
                raise ValidationError('Campsite unavailable for specified time period')

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
                        campground=campsite.campground
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


def get_campsite_availability(campsites_qs, start_date, end_date):
    """Fetch the status of each campsite in a queryset over a range of visit dates."""
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

    
    
