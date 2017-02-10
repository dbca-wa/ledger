
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from parkstay.forms import MakeBookingsForm
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
from datetime import datetime, timedelta

from parkstay.helpers import is_officer
from parkstay.forms import LoginForm

class CampsiteBookingSelector(TemplateView):
    template_name = 'ps/campsite_booking_selector.html'

    def get(self, request, *args, **kwargs):
        return super(CampsiteBookingSelector, self).get(request, *args, **kwargs)

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(CampsiteBookingSelector, self).dispatch(*args, **kwargs)


class CampgroundFeed(ICalFeed):
    timezone = 'UTC+8'

    # permissions check
    def __call__(self, request, *args, **kwargs):
        if not is_officer(self.request.user):
            raise Http403('Insufficient permissions')

        return super(ICalFeed, self).__call__(request, *args, **kwargs)

    def get_object(self, request, ground_id):
        # FIXME: add authentication parameter check
        return Campground.objects.get(pk=ground_id)

    def title(self, obj):
        return 'Bookings for {}'.format(obj.name)

    def items(self, obj):
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

class DashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'ps/dash/dash_tables_campgrounds.html'

    def test_func(self):
        return is_officer(self.request.user)


def abort_booking_view(request, *args, **kwargs):
    if 'ps_booking' in request.session:
        booking = Booking.objects.get(pk=request.session['ps_booking'])
        booking.delete()
        del request.session['ps_booking']
    return redirect('public_make_booking')


class MakeBookingsView(TemplateView):
    template_name = 'ps/booking/make_booking.html'
    def get(self, request, *args, **kwargs):
        # TODO: find campsites related to campground
        form = MakeBookingsForm(args)
        booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
        expiry = (booking.expiry_time - timezone.now()).seconds if booking else -1
        # for now, we can assume that there's only one campsite per booking.
        # later on we might need to amend that
        campsite = booking.campsitebooking_set.all()[0].campsite if booking else None
        return render(request, self.template_name, {
            'form': form, 
            'booking': booking,
            'campsite': campsite,
            'expiry': expiry
        })


class MyBookingsView(LoginRequiredMixin, TemplateView):
    template_name = 'ps/booking/my_bookings.html'


class ParkstayRoutingView(TemplateView):
    template_name = 'ps/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_officer(self.request.user):
                return redirect('dash-campgrounds')
            return redirect('my-bookings')
        kwargs['form'] = LoginForm
        return super(ParkstayRoutingView, self).get(*args, **kwargs)


class MapView(TemplateView):
    template_name = 'ps/map.html'
