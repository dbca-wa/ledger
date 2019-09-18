import logging
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django import forms
from parkstay.forms import LoginForm, MakeBookingsForm, AnonymousMakeBookingsForm, VehicleInfoFormset
from parkstay.exceptions import BindBookingException
from parkstay.models import (Campground,
                                CampsiteBooking,
                                Campsite,
                                CampsiteRate,
                                Booking,
                                BookingInvoice,
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
from ledger.accounts.models import EmailUser, Address, EmailIdentity
from ledger.payments.models import Invoice
from django_ical.views import ICalFeed
from datetime import datetime, timedelta
from decimal import *

from parkstay.helpers import is_officer
from parkstay import utils

logger = logging.getLogger('booking_checkout')

class CampsiteBookingSelector(TemplateView):
    template_name = 'ps/campsite_booking_selector.html'


class CampsiteAvailabilitySelector(TemplateView):
    template_name = 'ps/campsite_booking_selector.html'

    def get(self, request, *args, **kwargs):
        # if page is called with ratis_id, inject the ground_id
        context = {}
        ratis_id = request.GET.get('parkstay_site_id', None)
        if ratis_id:
            cg = Campground.objects.filter(ratis_id=ratis_id)
            if cg.exists():
                context['ground_id'] = cg.first().id
        return render(request, self.template_name, context)

class AvailabilityAdmin(TemplateView):
    template_name = 'ps/availability_admin.html'

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
    try:
        change = bool(request.GET.get('change',False))
        change_ratis = request.GET.get('change_ratis',None)
        change_id = request.GET.get('change_id',None)
        change_to = None
        booking = utils.get_session_booking(request.session)
        arrival = booking.arrival
        departure = booking.departure
        if change_ratis:
            try:
                c_id = Campground.objects.get(ratis_id=change_ratis).id
            except:
                c_id = booking.campground.id
        elif change_id:
            try:
                c_id = Campground.objects.get(id=change_id).id
            except:
                c_id = booking.campground.id
        else:
            c_id = booking.campground.id
        # only ever delete a booking object if it's marked as temporary
        if booking.booking_type == 3:
            booking.delete()
        utils.delete_session_booking(request.session)
        if change:
            # Redirect to the availability screen
            return redirect(reverse('campsite_availaiblity_selector') + '?site_id={}&arrival={}&departure={}'.format(c_id, arrival.strftime('%Y/%m/%d'), departure.strftime('%Y/%m/%d')))
        else:
            # Redirect to explore parks
            return redirect(settings.EXPLORE_PARKS_URL+'/park-stay')
    except Exception as e:
        pass
    return redirect('public_make_booking')


class MakeBookingsView(TemplateView):
    template_name = 'ps/booking/make_booking.html'

    def render_page(self, request, booking, form, vehicles, show_errors=False):
        # for now, we can assume that there's only one campsite per booking.
        # later on we might need to amend that
        expiry = booking.expiry_time.isoformat() if booking else ''
        timer = (booking.expiry_time-timezone.now()).seconds if booking else -1
        campsite = booking.campsites.all()[0].campsite if booking else None
        entry_fees = ParkEntryRate.objects.filter(Q(period_start__lte = booking.arrival), Q(period_end__gte=booking.arrival)|Q(period_end__isnull=True)).order_by('-period_start').first() if (booking and campsite.campground.park.entry_fee_required) else None
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
        if request.user.is_anonymous:
            form = AnonymousMakeBookingsForm(form_context)
        else:
            form_context['first_name'] = request.user.first_name
            form_context['last_name'] = request.user.last_name
            form_context['phone'] = request.user.phone_number
            form = MakeBookingsForm(form_context)

        vehicles = VehicleInfoFormset()
        return self.render_page(request, booking, form, vehicles)


    def post(self, request, *args, **kwargs):
        booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
        if request.user.is_anonymous:
            form = AnonymousMakeBookingsForm(request.POST)
        else:
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
        booking.details['first_name'] = form.cleaned_data.get('first_name')
        booking.details['last_name'] = form.cleaned_data.get('last_name')
        booking.details['phone'] = form.cleaned_data.get('phone')
        booking.details['country'] = form.cleaned_data.get('country').iso_3166_1_a2
        booking.details['postcode'] = form.cleaned_data.get('postcode')
        booking.details['num_adult'] = form.cleaned_data.get('num_adult')
        booking.details['num_concession'] = form.cleaned_data.get('num_concession')
        booking.details['num_child'] = form.cleaned_data.get('num_child')
        booking.details['num_infant'] = form.cleaned_data.get('num_infant')

        # update vehicle registrations from form
        VEHICLE_CHOICES = {'0': 'vehicle', '1': 'concession', '2': 'motorbike'}
        BookingVehicleRego.objects.filter(booking=booking).delete()
        for vehicle in vehicles:
            obj_check = BookingVehicleRego.objects.filter(booking = booking,
            rego = vehicle.cleaned_data.get('vehicle_rego'),
            type=VEHICLE_CHOICES[vehicle.cleaned_data.get('vehicle_type')],
            entry_fee=vehicle.cleaned_data.get('entry_fee')).exists()

            if(not obj_check):
                BookingVehicleRego.objects.create(
                    booking=booking, 
                    rego=vehicle.cleaned_data.get('vehicle_rego'), 
                    type=VEHICLE_CHOICES[vehicle.cleaned_data.get('vehicle_type')],
                    entry_fee=vehicle.cleaned_data.get('entry_fee')
                )
            else:
                form.add_error(None, 'Duplicate regos not permitted.If unknown add number, e.g. Hire1, Hire2.')
                return self.render_page(request, booking, form, vehicles,show_errors=True)
       
        # Check if number of people is exceeded in any of the campsites
        for c in booking.campsites.all():
            if booking.num_guests > c.campsite.max_people:
                form.add_error(None, 'Number of people exceeded for the current camp site.')
                return self.render_page(request, booking, form, vehicles, show_errors=True)
            # Prevent booking if less than min people 
            if booking.num_guests < c.campsite.min_people:
                form.add_error('Number of people is less than the minimum allowed for the current campsite.')
                return self.render_page(request, booking, form, vehicles, show_errors=True)

        # generate final pricing
        try:
            lines = utils.price_or_lineitems(request, booking, booking.campsite_id_list)
        except Exception as e:
            form.add_error(None, '{} Please contact Parks and Visitors services with this error message, the campground/campsite and the time of the request.'.format(str(e)))
            return self.render_page(request, booking, form, vehicles, show_errors=True)
            
        print(lines)
        total = sum([Decimal(p['price_incl_tax'])*p['quantity'] for p in lines])

        # get the customer object
        if request.user.is_anonymous:
            # searching on EmailIdentity looks for both EmailUser and Profile objects with the email entered by user
            customer_qs = EmailIdentity.objects.filter(email__iexact=form.cleaned_data.get('email'))
            if customer_qs:
                customer = customer_qs.first().user
            else:
                customer = EmailUser.objects.create(
                        email=form.cleaned_data.get('email'), 
                        first_name=form.cleaned_data.get('first_name'),
                        last_name=form.cleaned_data.get('last_name'),
                        phone_number=form.cleaned_data.get('phone'),
                        mobile_number=form.cleaned_data.get('phone')
                )
                Address.objects.create(line1='address', user=customer, postcode=form.cleaned_data.get('postcode'), country=form.cleaned_data.get('country').iso_3166_1_a2)
        else:
            customer = request.user
        
        # FIXME: get feedback on whether to overwrite personal info if the EmailUser
        # already exists
 
        # finalise the booking object
        booking.customer = customer
        booking.cost_total = total
        booking.save()

        # generate invoice
        reservation = u"Reservation for {} confirmation {}".format(u'{} {}'.format(booking.customer.first_name, booking.customer.last_name), booking.id)
        
        logger.info(u'{} built booking {} and handing over to payment gateway'.format(u'User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else u'An anonymous user',booking.id))

        result = utils.checkout(request, booking, lines, invoice_text=reservation)

        return result


class BookingSuccessView(TemplateView):
    template_name = 'ps/booking/success.html'

    def get(self, request, *args, **kwargs):
        try:
            booking = utils.get_session_booking(request.session)
            invoice_ref = request.GET.get('invoice')
            
            try:
                utils.bind_booking(request, booking, invoice_ref)
            except BindBookingException:
                return redirect('public_make_booking')
            
        except Exception as e:
            if ('ps_last_booking' in request.session) and Booking.objects.filter(id=request.session['ps_last_booking']).exists():
                booking = Booking.objects.get(id=request.session['ps_last_booking'])
            else:
                return redirect('home')

        context = {
            'booking': booking
        }
        return render(request, self.template_name, context)


class MyBookingsView(LoginRequiredMixin, TemplateView):
    template_name = 'ps/booking/my_bookings.html'

    def get(self, request, *args, **kwargs):
        bookings = Booking.objects.filter(customer=request.user, booking_type__in=(0, 1), is_canceled=False)
        today = timezone.now().date()

        context = {
            'current_bookings': bookings.filter(departure__gte=today).order_by('arrival'),
            'past_bookings': bookings.filter(departure__lt=today).order_by('-arrival')
        }
        return render(request, self.template_name, context)


class ParkstayRoutingView(TemplateView):
    template_name = 'ps/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if is_officer(self.request.user):
                return redirect('dash-campgrounds')
            return redirect('public_my_bookings')
        kwargs['form'] = LoginForm
        return super(ParkstayRoutingView, self).get(*args, **kwargs)


class MapView(TemplateView):
    template_name = 'ps/map.html'

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'ps/profile.html'
