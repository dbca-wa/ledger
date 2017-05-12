
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
from parkstay.forms import LoginForm, MakeBookingsForm, AnonymousMakeBookingsForm, VehicleInfoFormset
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
from parkstay import emails
from ledger.accounts.models import EmailUser, Address
from django_ical.views import ICalFeed
from datetime import datetime, timedelta
from decimal import *

from parkstay.helpers import is_officer
from parkstay import utils

class CampsiteBookingSelector(TemplateView):
    template_name = 'ps/campsite_booking_selector.html'


class CampsiteAvailabilitySelector(TemplateView):
    template_name = 'ps/campsite_booking_selector.html'

    def get(self, request, *args, **kwargs):
        # if page is called with ratis_id, inject the ground_id
        context = {}
        ratis_id = request.GET.get('ratis_id', None)
        if ratis_id:
            cg = Campground.objects.filter(ratis_id=ratis_id)
            if cg.exists():
                context['ground_id'] = cg.first().id
        return render(request, self.template_name, context)


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
        booking = utils.get_session_booking(request.session)
        # only ever delete a booking object if it's marked as temporary
        if booking.booking_type == 3:
            booking.delete()
        utils.delete_session_booking(request.session)
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
        if request.user.is_anonymous():
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
        if request.user.is_anonymous():
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
            BookingVehicleRego.objects.create(
                    booking=booking, 
                    rego=vehicle.cleaned_data.get('vehicle_rego'), 
                    type=VEHICLE_CHOICES[vehicle.cleaned_data.get('vehicle_type')],
                    entry_fee=vehicle.cleaned_data.get('entry_fee')
            )

        # generate final pricing
        try:
            lines = utils.price_or_lineitems(request, booking, booking.campsite_id_list)
        except Exception as e:
            form.add_error(None, '{} Please contact Parks and Visitors services with this error message, the campground/campsite and the time of the request.'.format(str(e)))
            return self.render_page(request, booking, form, vehicles, show_errors=True)
            
        print(lines)
        total = sum([Decimal(p['price_incl_tax'])*p['quantity'] for p in lines])

        # get the customer object
        if request.user.is_anonymous():
            try:
                customer = EmailUser.objects.get(email=form.cleaned_data.get('email'))
            except EmailUser.DoesNotExist:
                customer = EmailUser.objects.create(
                        email=form.cleaned_data.get('email'), 
                        first_name=form.cleaned_data.get('first_name'),
                        last_name=form.cleaned_data.get('last_name'),
                        phone_number=form.cleaned_data.get('phone'),
                        mobile_number=form.cleaned_data.get('phone')
                )
                Address.objects.create(line1='address', user=customer, postcode=emailUser['postcode'], country=form.cleaned_data.get('country'))
        else:
            customer = request.user
        
        # FIXME: get feedback on whether to overwrite personal info if the EmailUser
        # already exists
 
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
        result =  HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers['Content-Type'],
        )

        # if we're anonymous add the basket cookie to the current session
        if request.user.is_anonymous() and settings.OSCAR_BASKET_COOKIE_OPEN in response.history[0].cookies:
            basket_cookie = response.history[0].cookies[settings.OSCAR_BASKET_COOKIE_OPEN]
            result.set_cookie(settings.OSCAR_BASKET_COOKIE_OPEN, basket_cookie)
        
        return result


class BookingSuccessView(TemplateView):
    template_name = 'ps/booking/success.html'

    def get(self, request, *args, **kwargs):
        try:
            booking = utils.get_session_booking(request.session)
            invoice_ref = request.GET.get('invoice')

            # FIXME: replace with server side notify_url callback
            book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=invoice_ref)
            
            # set booking to be permanent fixture
            booking.booking_type = 1  # internet booking
            booking.expiry_time = None
            booking.save()

            utils.delete_session_booking(request.session)
            request.session['ps_last_booking'] = booking.id
            
            # send out the invoice before the confirmation is sent
            emails.send_booking_invoice(booking)
            # for fully paid bookings, fire off confirmation email
            if booking.paid:
                emails.send_booking_confirmation(booking)

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
        if self.request.user.is_authenticated():
            if is_officer(self.request.user):
                return redirect('dash-campgrounds')
            return redirect('public_my_bookings')
        kwargs['form'] = LoginForm
        return super(ParkstayRoutingView, self).get(*args, **kwargs)


class MapView(TemplateView):
    template_name = 'ps/map.html'
