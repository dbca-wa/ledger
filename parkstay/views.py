
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
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

class CampgroundFeed(ICalFeed):
    timezone = 'UTC+8'

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


class MakeBookingsView(LoginRequiredMixin, TemplateView):
    template_name = 'ps/booking/make_booking.html'
    def get(self,request,*args,**kwargs):
        # TODO: find campsites related to campground
        form = MakeBookingsForm(args,campsites =[('exp','example')])
        return render(request, self.template_name, {'form': form})

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
