from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from parkstay.models import (Campground, Campsite, CampsiteBooking, Booking)


def create_booking_by_class(campground_id, campsite_class_id, start_date, end_date, num_adult=0, num_concession=0, num_child=0, num_infant=0):
    """Create a new temporary booking in the system."""
    # get campground
    campground = Campground.objects.get(pk=campground_id)

    # TODO: campground openness business logic
    # TODO: campsite openness business logic
    # TODO: date range check business logic
    # TODO: number of people check? this might be modifiable later

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

        # fetch all of the single-day CampsiteBooking objects within the date range for the sites
        bookings_qs =   CampsiteBooking.objects.filter(
                            campsite__in=sites_qs,
                            date__gte=start_date,
                            date__lt=end_date
                        ).order_by('date', 'campsite__name')

        excluded_site_ids = set([x[0] for x in bookings_qs.values_list('campsite')])
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
    campsite = Campsite.objects.get(pk=campsite_id)

    # TODO: campground openness business logic
    # TODO: campsite openness business logic
    # TODO: date range check business logic
    # TODO: number of people check? this might be modifiable later

    # the CampsiteBooking table runs the risk of a race condition,
    # wrap all this behaviour up in a transaction
    with transaction.atomic():
        # check for single-day CampsiteBooking objects within the date range for the site
        bookings_qs =   CampsiteBooking.objects.filter(
                            campsite=campsite,
                            date__gte=start_date,
                            date__lt=end_date
                        ).order_by('date', 'campsite__name')

        if bookings_qs.exists():
            raise ValidationError('Campsite unavailable for specified time period')

        # Create a new temporary booking with an expiry timestamp (default 20mins)
        booking =   Booking.objects.create(
                        booking_type=3,
                        arrival=start_date,
                        departure=end_date,
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

