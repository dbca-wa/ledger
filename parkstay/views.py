
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django import forms
from parkstay.forms import LoginForm, MakeBookingsForm, VehicleInfoFormset
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
                                BookingVehicleRego,
                                CampsiteRate,
                                ParkEntryRate
                                )
from ledger.accounts.models import EmailUser
from django_ical.views import ICalFeed
from datetime import datetime, timedelta
from decimal import *

from parkstay.helpers import is_officer
from parkstay import utils

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
            x[0] for x in item.campsites.values_list('campsite__name').distinct()
        ] ))

class DashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'ps/dash/dash_tables_campgrounds.html'

    def test_func(self):
        return is_officer(self.request.user)


def abort_booking_view(request, *args, **kwargs):
    if 'ps_booking' in request.session:
        booking = Booking.objects.get(pk=request.session['ps_booking'])
        # only ever delete a booking object if it's marked as temporary
        if booking.booking_type == 3:
            booking.delete()
        del request.session['ps_booking']
    return redirect('public_make_booking')


class MakeBookingsView(TemplateView):
    template_name = 'ps/booking/make_booking.html'

    def render_page(self, request, booking, form, vehicles, show_errors=False):
        # for now, we can assume that there's only one campsite per booking.
        # later on we might need to amend that
        expiry = booking.expiry_time.isoformat() if booking else ''
        timer = (booking.expiry_time-timezone.now()).seconds if booking else -1
        campsite = booking.campsites.all()[0].campsite if booking else None
        entry_fees = ParkEntryRate.objects.filter(Q(period_start__lte = booking.arrival), Q(period_end__gt=booking.arrival)|Q(period_end__isnull=True)).order_by('-period_start').first() if (booking and campsite.campground.park.entry_fee_required) else None
        pricing = {
            'adult': Decimal('0.00'),
            'concession': Decimal('0.00'),
            'child': Decimal('0.00'),
            'infant': Decimal('0.00'),
            'vehicle': entry_fees.vehicle if entry_fees else Decimal('0.00'),
            'vehicle_conc': entry_fees.concession if entry_fees else Decimal('0.00'),
            'motorcycle': entry_fees.motorbike if entry_fees else Decimal('0.00')
        }
        if booking:
            pricing_list = utils.get_visit_rates(Campsite.objects.filter(pk=campsite.pk), booking.arrival, booking.departure)[campsite.pk]
            pricing['adult'] = sum([x['adult'] for x in pricing_list.values()])
            pricing['concession'] = sum([x['concession'] for x in pricing_list.values()])
            pricing['child'] = sum([x['child'] for x in pricing_list.values()])
            pricing['infant'] = sum([x['infant'] for x in pricing_list.values()])


        return render(request, self.template_name, {
            'form': form, 
            'vehicles': vehicles,
            'booking': booking,
            'campsite': campsite,
            'expiry': expiry,
            'timer': timer,
            'pricing': pricing,
            'show_errors': show_errors
        })


    def get(self, request, *args, **kwargs):
        # TODO: find campsites related to campground
        booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
        form_context = {
            'num_adult': booking.details.get('num_adult', 0) if booking else 0,
            'num_concession': booking.details.get('num_concession', 0) if booking else 0,
            'num_child': booking.details.get('num_child', 0) if booking else 0,
            'num_infant': booking.details.get('num_infant', 0) if booking else 0
        }
        form = MakeBookingsForm(form_context)
        vehicles = VehicleInfoFormset()
        return self.render_page(request, booking, form, vehicles)


    def post(self, request, *args, **kwargs):
        booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
        form = MakeBookingsForm(request.POST)
        vehicles = VehicleInfoFormset(request.POST)   
        
        # re-render the page if there's no booking in the session
        if not booking:
            return self.render_page(request, booking, form, vehicles)
    
        # re-render the page if the form doesn't validate
        if (not form.is_valid()) or (not vehicles.is_valid()):
            return self.render_page(request, booking, form, vehicles, show_errors=True)

        # update the booking object with information from the form
        if not booking.details:
            booking.details = {}
        booking.details['num_adult'] = form.cleaned_data.get('num_adult')
        booking.details['num_concession'] = form.cleaned_data.get('num_concession')
        booking.details['num_child'] = form.cleaned_data.get('num_child')
        booking.details['num_infant'] = form.cleaned_data.get('num_infant')

        # update vehicle registrations from form
        VEHICLE_CHOICES = {'0': 'vehicle', '1': 'concession', '2': 'motorbike'}
        BookingVehicleRego.objects.filter(booking=booking).delete()
        for vehicle in vehicles:
            BookingVehicleRego.objects.create(
                    booking=booking, 
                    rego=vehicle.cleaned_data.get('vehicle_rego'), 
                    type=VEHICLE_CHOICES[vehicle.cleaned_data.get('vehicle_type')]
            )

        # generate final pricing
        lines = utils.price_or_lineitems(request, booking, booking.campsite_id_list)
        print(lines)
        total = sum([Decimal(p['price_incl_tax'])*p['quantity'] for p in lines])

        # get the customer object
        # FIXME: get feedback on whether to overwrite personal info if the EmailUser
        # already exists
        try:
            customer = EmailUser.objects.get(email=form.cleaned_data.get('email'))
        except EmailUser.DoesNotExist:
            customer = EmailUser.objects.create(
                    email=form.cleaned_data.get('email'), 
                    first_name=form.cleaned_data.get('first_name'),
                    last_name=form.cleaned_data.get('last_name'),
                    phone_number=form.cleaned_data.get('phone')
            )

        
        # finalise the booking object
        booking.customer = customer
        booking.cost_total = total
        booking.save()

        # generate invoice
        reservation = "Reservation for {} from {} to {} at {}".format(
                '{} {}'.format(booking.customer.first_name, booking.customer.last_name),
                booking.arrival,
                booking.departure,
                booking.campground.name
        )
        

        response = utils.checkout(request, booking, lines, invoice_text=reservation)
        return HttpResponse(response.content)


class MyBookingsView(LoginRequiredMixin, TemplateView):
    template_name = 'ps/booking/my_bookings.html'

    def get(self, request, *args, **kwargs):
        bookings = Booking.objects.filter(customer=request.user, booking_type__in=(0, 1))
        today = timezone.now().date()

        context = {
            'current_bookings': bookings.filter(departure__gte=today).order_by('arrival'),
            'past_bookings': bookings.filter(departure__lt=today).order_by('-arrival')
        }
        return render(request, self.template_name, context)


class ParkstayRoutingView(TemplateView):
    template_name = 'ps/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_officer(self.request.user):
                return redirect('dash-campgrounds')
            return redirect('public_my_bookings')
        kwargs['form'] = LoginForm
        return super(ParkstayRoutingView, self).get(*args, **kwargs)


class MapView(TemplateView):
    template_name = 'ps/map.html'
