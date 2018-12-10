import logging
import calendar
import json
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django import forms
from mooring.forms import LoginForm, MakeBookingsForm, AnonymousMakeBookingsForm, VehicleInfoFormset
from mooring.models import (MooringArea,
                                MooringsiteBooking,
                                Mooringsite,
                                MooringsiteRate,
                                Booking,
                                BookingInvoice,
                                PromoArea,
                                MarinePark,
                                Feature,
                                Region,
                                MooringsiteClass,
                                Booking,
                                BookingVehicleRego,
                                MooringsiteRate,
                                MarinaEntryRate,
                                AdmissionsBooking,
                                AdmissionsBookingInvoice,
                                AdmissionsRate,
                                DiscountReason,
                                RegisteredVessels
                                )
from mooring import emails
from ledger.accounts.models import EmailUser, Address
from ledger.payments.models import Invoice
from oscar.apps.order.models import Order
from django_ical.views import ICalFeed
from datetime import datetime, timedelta
from decimal import *

from mooring.helpers import is_officer
from mooring import utils
from ledger.payments.mixins import InvoiceOwnerMixin
from mooring.invoice_pdf import create_invoice_pdf_bytes
from mooring.context_processors import mooring_url

logger = logging.getLogger('booking_checkout')


class MooringsiteBookingSelector(TemplateView):
    template_name = 'mooring/campsite_booking_selector.html'

class MooringsiteAvailabilitySelector(TemplateView):
    template_name = 'mooring/campsite_booking_selector.html'

    def get(self, request, *args, **kwargs):
        # if page is called with ratis_id, inject the ground_id
        context = {}
        ratis_id = request.GET.get('mooring_site_id', None)
        if ratis_id:
            cg = MooringArea.objects.filter(ratis_id=ratis_id)
            if cg.exists():
                context['ground_id'] = cg.first().id
        return render(request, self.template_name, context)

class MooringAvailability2Selector(TemplateView):
    template_name = 'mooring/mooring_availablity_booking_selector.html'

    def get(self, request, *args, **kwargs):
        # if page is called with ratis_id, inject the ground_id
        context = {}
        ratis_id = request.GET.get('mooring_site_id', None)
        if ratis_id:
            cg = MooringArea.objects.filter(ratis_id=ratis_id)
            if cg.exists():
                context['ground_id'] = cg.first().id
        return render(request, self.template_name, context)

class AvailabilityAdmin(TemplateView):
    template_name = 'mooring/availability_admin.html'

class MooringAreaFeed(ICalFeed):
    timezone = 'UTC+8'

    # permissions check
    def __call__(self, request, *args, **kwargs):
        if not is_officer(self.request.user):
            raise Http403('Insufficient permissions')

        return super(ICalFeed, self).__call__(request, *args, **kwargs)

    def get_object(self, request, ground_id):
        # FIXME: add authentication parameter check
        return MooringArea.objects.get(pk=ground_id)

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
    template_name = 'mooring/dash/dash_tables_campgrounds.html'

    def test_func(self):
        return is_officer(self.request.user)

def abort_booking_view(request, *args, **kwargs):
    try:
        change = bool(request.GET.get('change',False))
        change_ratis = request.GET.get('change_ratis',None)
        change_id = request.GET.get('change_id',None)
        change_to = None
        booking = utils.get_session_booking(request.session)
        if change_ratis:
            try:
                c_id = MooringArea.objects.get(ratis_id=change_ratis).id
            except:
                c_id = booking.mooringarea.id
        elif change_id:
            try:
                c_id = MooringArea.objects.get(id=change_id).id
            except:
                c_id = booking.mooringarea.id
        else:
            c_id = booking.mooringarea.id
        
        if change:
            num_adults = booking.details['num_adults']
            num_children = booking.details['num_children']
            num_infants = booking.details['num_infants']
            vessel_size = booking.details['vessel_size']
            vessel_draft = booking.details['vessel_draft']
            vessel_beam = booking.details['vessel_beam']
            vessel_weight = booking.details['vessel_weight']
            vessel_rego = booking.details['vessel_rego']
            # Redirect to the availability screen
            #return redirect(reverse('campsite_availaiblity_selector') + '?site_id={}'.format(c_id)) 
            #mooring_availaiblity2_selector
            return redirect(reverse('mooring_availaiblity2_selector') + '?site_id={}&num_adult={}&num_children={}&num_infants={}&vessel_size={}&vessel_draft={}&vessel_beam={}&vessel_weight={}&vessel_rego={}'.format(c_id, num_adults, num_children, num_infants, vessel_size, vessel_draft, vessel_beam, vessel_weight, vessel_rego))
        else:
            # only ever delete a booking object if it's marked as temporary
            if booking.booking_type == 3:
                booking.delete()
            utils.delete_session_booking(request.session)
            # Redirect to explore parks
            return redirect('map')
    except Exception as e:
        pass
    return redirect('public_make_booking')

class MakeBookingsView(TemplateView):
    template_name = 'mooring/booking/make_booking.html'

    def render_page(self, request, booking, form, vehicles, show_errors=False):
        booking_mooring = None
        booking_total = '0.00'
        # for now, we can assume that there's only one campsite per booking.
        # later on we might need to amend that
        expiry = booking.expiry_time.isoformat() if booking else ''
        timer = (booking.expiry_time-timezone.now()).seconds if booking else -1
        campsite = booking.campsites.all()[0].campsite if booking else None
        entry_fees = MarinaEntryRate.objects.filter(Q(period_start__lte = booking.arrival), Q(period_end__gt=booking.arrival)|Q(period_end__isnull=True)).order_by('-period_start').first() if (booking and campsite.mooringarea.park.entry_fee_required) else None
        pricing = {
            'mooring': Decimal('0.00'),
            'adult': Decimal('0.00'),
            'concession': Decimal('0.00'),
            'child': Decimal('0.00'),
            'infant': Decimal('0.00'),
            'family': Decimal('0.00'),
            'adult_on': Decimal('0.00'),
            'child_on': Decimal('0.00'),
            'infant_on': Decimal('0.00'),
            'family_on': Decimal('0.00'),
            'vessel': entry_fees.vessel if entry_fees else Decimal('0.00'),
            'vehicle': entry_fees.vehicle if entry_fees else Decimal('0.00'),
            'vehicle_conc': entry_fees.concession if entry_fees else Decimal('0.00'),
            'motorcycle': entry_fees.motorbike if entry_fees else Decimal('0.00')
        }
        details = {
            'num_adults':0,
            'num_children':0,
            'num_infants':0,
            'vessel_size':0,
            'vessel_draft':0,
            'vessel_beam':0,
            'vessel_weight':0,
            'vessel_rego':0,
        }
        lines = []

        if booking:
            booking_mooring = MooringsiteBooking.objects.filter(booking=booking)
            booking_total = sum(Decimal(i.amount) for i in booking_mooring)
            details = booking.details
            # pricing_list = utils.get_visit_rates(Mooringsite.objects.filter(pk=campsite.pk), booking.arrival, booking.departure)[campsite.pk]
            # pricing_list = {}
#            print (pricing_list)if request.user.is_staff:
        #     result = utils.checkout(request, booking, lines, invoice_text=reservation, internal=True)    
        # else:
#            for x in pricing_lisif request.user.is_staff:
        #     result = utils.checkout(request, booking, lines, invoice_text=reservation, internal=True)    
        # else:s():
#                print x['mooringif request.user.is_staff:
        #     result = utils.checkout(request, booking, lines, invoice_text=reservation, internal=True)    
        # else:
#                print "---------if request.user.is_staff:
        #     result = utils.checkout(request, booking, lines, invoice_text=reservation, internal=True)    
        # else:-----------"
            # pricing['mooring'] if request.user.is_staff:
        #     result = utils.checkout(request, booking, lines, invoice_text=reservation, internal=True)    
        # else:float(x['mooring']) for x in pricing_list.values()])
            # pricing['adult'] = if request.user.is_staff:
        #     result = utils.checkout(request, booking, lines, invoice_text=reservation, internal=True)    
        # else:oat(x['adult']) for x in pricing_list.values()])
            # pricing['concessionif request.user.is_staff:
        #     result = utils.checkout(request, booking, lines, invoice_text=reservation, internal=True)    
        # else:m([float(x['concession']) for x in pricing_list.values()])
            # pricing['child'] = if request.user.is_staff:
        #     result = utils.checkout(request, booking, lines, invoice_text=reservation, internal=True)    
        # else:oat(x['child']) for x in pricing_list.values()])
            # pricing['infant'] = sum([float(x['infant']) for x in pricing_list.values()])
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
                    lines.append({'from': from_dt, 'to': to_dt})
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
                    lines.append({'from':datetime.strftime(latest_from, '%d %b %Y'), 'to': datetime.strftime(latest_to, '%d %b %Y'), 'admissionFee': 0})
                    if i < len(new_lines)-1:
                        latest_from = new_lines[i+1]['from'].date()
                        latest_to = None
                i+= 1


            rate = AdmissionsRate.objects.filter(Q(period_start__lte=booking.arrival), (Q(period_end=None) | Q(period_end__gte=booking.arrival)))[0]
            if rate:
                pricing['adult'] = rate.adult_cost
                pricing['child'] = rate.children_cost
                pricing['infant'] = rate.infant_cost
                pricing['family'] = rate.family_cost
                pricing['adult_on'] = rate.adult_overnight_cost
                pricing['child_on'] = rate.children_overnight_cost
                pricing['infant_on'] = rate.infant_overnight_cost
                pricing['family_on'] = rate.family_overnight_cost

        
        staff = request.user.is_staff
        if(staff):
            staff = "true"
        else:
            staff = "false"

        return render(request, self.template_name, {
            'form': form, 
            'vehicles': vehicles,
            'booking': booking,
            'booking_mooring': booking_mooring,
            'booking_total' : booking_total,
            'campsite': campsite,
            'expiry': expiry,
            'timer': timer,
            'details': details,
            'pricing': pricing,
            'show_errors': show_errors,
            'lines': lines,
            'staff': staff
         
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

        if request.user.is_anonymous() or request.user.is_staff:
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
        mooring_booking = ""
        if booking:
            mooring_booking = MooringsiteBooking.objects.filter(booking=booking)
        if request.user.is_anonymous() or request.user.is_staff:
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
        # booking.details['num_adult'] = form.cleaned_data.get('num_adult')
        booking.details['num_concession'] = form.cleaned_data.get('num_concession')
        # booking.details['num_child'] = form.cleaned_data.get('num_child')
        # booking.details['num_infant'] = form.cleaned_data.get('num_infant')
        booking.details['num_adult'] = int(request.POST.get('num_adults')) if request.POST.get('num_adults') else 0
        booking.details['num_child'] = int(request.POST.get('num_children')) if request.POST.get('num_children') else 0
        booking.details['num_infant'] = int(request.POST.get('num_infants')) if request.POST.get('num_infants') else 0
        booking.details['non_online_booking'] = True if request.POST.get('nononline') else False
        overidden = True if request.POST.get('override') else False

        if overidden:
            override_price = Decimal(request.POST.get('overridePrice')) if request.POST.get('overridePrice') else 0
            if override_price > 0:
                booking.override_price = override_price
                booking.overridden_by = request.user
                override_reason = request.POST.get('overrideReason') if request.POST.get('overrideReason') else None
                if override_reason is not None:
                    booking.override_reason = DiscountReason.objects.get(id=override_reason)
                booking.override_reason_info = request.POST.get('overrideDetail') if request.POST.get('overrideDetail') else ""


        oracle_code = ''
        if booking.mooringarea.oracle_code:
            oracle_code = booking.mooringarea.oracle_code
        rego = request.POST.get('form-0-vehicle_rego') if request.POST.get('form-0-vehicle_rego') else None

        admissionsJson = json.loads(request.POST.get('admissionsLines')) if request.POST.get('admissionsLines') else []
        admissions = []
        for line in admissionsJson:
            admissions.append({
                'from': line['from'],
                'to': line['to'],
                'admissionFee': Decimal(line['admissionFee']),
                'guests': booking.num_guests,
                'oracle_code': oracle_code
                })
        admissionLines = utils.admission_lineitems(admissions)
        if RegisteredVessels.objects.filter(rego_no=rego).count() > 0:
            vessel = RegisteredVessels.objects.get(rego_no=rego)
            if vessel.admissionsPaid:
                admissionLines = []
        

        # update vehicle registrations from form
        VEHICLE_CHOICES = {'0': 'vessel', '1': 'concession', '2': 'motorbike'}
        BookingVehicleRego.objects.filter(booking=booking).delete()
        for vehicle in vehicles:
            BookingVehicleRego.objects.create(
                    booking=booking, 
                    rego=vehicle.cleaned_data.get('vehicle_rego'), 
                    type=VEHICLE_CHOICES[vehicle.cleaned_data.get('vehicle_type')],
                    entry_fee=vehicle.cleaned_data.get('entry_fee')
            )

        # Check if number of people is exceeded in any of the campsites
        for c in booking.campsites.all():
            if booking.num_guests > c.campsite.max_people:
                form.add_error(None, 'Number of people exceeded for the current camp site.')
                return self.render_page(request, booking, form, vehicles, show_errors=True)
            # Prevent booking if less than min people 
#            if booking.num_guests < c.campsite.min_people:
#                form.add_error('Number of people is less than the minimum allowed for the current campsite.')
#                return self.render_page(request, booking, form, vehicles, show_errors=True)
        # generate final pricing
        lines = utils.price_or_lineitems(request, booking, booking.campsite_id_list)
        
        if booking.details['non_online_booking']:
            booking_line = utils.nononline_booking_lineitems(oracle_code)
            for line in booking_line:
                lines.append(line)
        if mooring_booking:
            lines_required = False
            for bm in mooring_booking:
                if bm.campsite.mooringarea.park.entry_fee_required:
                    lines_required = True
            if lines_required:
                for line in admissionLines:
                    lines.append(line)
        try:
            pass
#            lines = utils.price_or_lineitems(request, booking, booking.campsite_id_list)
        except Exception as e:
            form.add_error(None, '{} Please contact Marine Park and Visitors services with this error message and the time of the request.'.format(str(e)))
            return self.render_page(request, booking, form, vehicles, show_errors=True)
            
        #print(lines)
        total = sum([Decimal(p['price_incl_tax'])*p['quantity'] for p in lines])

        # if was discounted, include discount line and set total cost of booking.
        if booking.override_price and overidden:
            discount_line = utils.override_lineitems(booking.override_price, booking.override_reason, total, oracle_code, booking.override_reason_info)
            for line in discount_line:
                lines.append(line)
            total = booking.override_price

        # get the customer object
        if request.user.is_anonymous() or request.user.is_staff:
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
        reservation = u"Reservation for {} from {} to {} at {}".format(
               u'{} {}'.format(booking.customer.first_name, booking.customer.last_name),
                booking.arrival.strftime('%d-%m-%Y'),
                booking.departure.strftime('%d-%m-%Y'),
                booking.mooringarea.name
        )
        
        logger.info('{} built booking {} and handing over to payment gateway'.format('User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else 'An anonymous user',booking.id))

        # if request.user.is_staff:
        #     result = utils.checkout(request, booking, lines, invoice_text=reservation, internal=True)    
        # else:
        result = utils.checkout(request, booking, lines, invoice_text=reservation)
#        result =  HttpResponse(
#            content=response.content,
#            status=response.status_code,
#            content_type=response.headers['Content-Type'],
#        )

        # if we're anonymous add the basket cookie to the current session
        #if request.user.is_anonymous() and settings.OSCAR_BASKET_COOKIE_OPEN in response.history[0].cookies:
        #    basket_cookie = response.history[0].cookies[settings.OSCAR_BASKET_COOKIE_OPEN]
        #    result.set_cookie(settings.OSCAR_BASKET_COOKIE_OPEN, basket_cookie)
        
        return result

class AdmissionsBasketCreated(TemplateView):
    template_name = 'mooring/admissions/admissions_success.html'

    def get(request, *args, **kwargs):
        return HttpResponseRedirect(reverse('checkout:index'))

class AdmissionsBookingSuccessView(TemplateView):
    template_name = 'mooring/admissions/admission_success.html'

    def get(self, request, *args, **kwargs):
        try:
            booking = utils.get_session_admissions_booking(request.session)
            invoice_ref = request.GET.get('invoice')

            if booking.booking_type == 3:
                try:
                    inv = Invoice.objects.get(reference=invoice_ref)
                    order = Order.objects.get(number=inv.order_number)
                    order.user = booking.customer
                    order.save()
                except Invoice.DoesNotExist:
                    logger.error('{} tried making a booking with an incorrect invoice'.format('User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else 'An anonymous user'))
                    return redirect('admissions')

                if inv.system not in ['0516']:
                    logger.error('{} tried making a booking with an invoice from another system with reference number {}'.format('User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else 'An anonymous user',inv.reference))
                    return redirect('admissions')

                try:
                    b = AdmissionsBookingInvoice.objects.get(invoice_reference=invoice_ref)
                    logger.error('{} tried making a booking with an already used invoice with reference number {}'.format('User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else 'An anonymous user',inv.reference))
                    return redirect('admissions')
                except AdmissionsBookingInvoice.DoesNotExist:
                    logger.info('{} finished temporary booking {}, creating new BookingInvoice with reference {}'.format('User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else 'An anonymous user',booking.id, invoice_ref))
                    # FIXME: replace with server side notify_url callback
                    admissionsInvoice = AdmissionsBookingInvoice.objects.get_or_create(admissions_booking=booking, invoice_reference=invoice_ref)

                    # set booking to be permanent fixture
                    booking.booking_type = 1  # internet booking
                    booking.save()
                    request.session['ad_last_booking'] = booking.id
                    utils.delete_session_admissions_booking(request.session)

                    # send out the invoice before the confirmation is sent
                    emails.send_admissions_booking_invoice(booking)
                    # for fully paid bookings, fire off confirmation email
                    emails.send_admissions_booking_confirmation(booking,request)

        except Exception as e:
            print(e)
            if ('ad_last_booking' in request.session) and AdmissionsBooking.objects.filter(id=request.session['ad_last_booking']).exists():
                booking = AdmissionsBooking.objects.get(id=request.session['ad_last_booking'])
                invoice_ref = AdmissionsBookingInvoice.objects.get(admissions_booking=booking).invoice_reference
            else:
                return redirect('home')

        if request.user.is_staff:
            return redirect('home')
        context = {
            'admissionsBooking': booking,
            'admissionsInvoice': invoice_ref
        }
        return render(request, self.template_name, context)

class BookingSuccessView(TemplateView):
    template_name = 'mooring/booking/success.html'

    def get(self, request, *args, **kwargs):
        print " BOOKING SUCCESS " 
        try:
            booking = utils.get_session_booking(request.session)
            invoice_ref = request.GET.get('invoice')
            print "SUCCESS 2 "
            if booking.booking_type == 3:
                try:
                    inv = Invoice.objects.get(reference=invoice_ref)
                    order = Order.objects.get(number=inv.order_number)
                    order.user = booking.customer
                    order.save()
                except Invoice.DoesNotExist:
                    logger.error('{} tried making a booking with an incorrect invoice'.format('User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else 'An anonymous user'))
                    return redirect('public_make_booking')

                if inv.system not in ['0516']:
                    logger.error('{} tried making a booking with an invoice from another system with reference number {}'.format('User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else 'An anonymous user',inv.reference))
                    return redirect('public_make_booking')

                try:
                    b = BookingInvoice.objects.get(invoice_reference=invoice_ref)
                    logger.error('{} tried making a booking with an already used invoice with reference number {}'.format('User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else 'An anonymous user',inv.reference))
                    return redirect('public_make_booking')
                except BookingInvoice.DoesNotExist:
                    logger.info('{} finished temporary booking {}, creating new BookingInvoice with reference {}'.format('User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else 'An anonymous user',booking.id, invoice_ref))
                    # FIXME: replace with server side notify_url callback
                    book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=invoice_ref)

                    if booking.old_booking:
                        old_booking = Booking.objects.get(id=booking.old_booking.id)
                        logger.info("old booking")
                        old_booking.booking_type = 4
                        old_booking.save()
                        logger.info("old logger 2")
                        booking_items = MooringsiteBooking.objects.filter(booking=old_booking)
                        logger.info("old logger 3")
                        for bi in booking_items:
                            logger.info("old logger 4")
                            bi.booking_type = 4
                            bi.save()
 

                          

                    # set booking to be permanent fixture
                    booking.booking_type = 1  # internet booking
                    booking.expiry_time = None
                    booking.save()

                    if not request.user.is_staff:
                        print "USER IS NOT STAFF."
                        request.session['ps_last_booking'] = booking.id
                    utils.delete_session_booking(request.session)
                    
                    # send out the invoice before the confirmation is sent
                    emails.send_booking_invoice(booking)
                    print "SUCCESS 3"
                    # for fully paid bookings, fire off confirmation email
                    if booking.paid:
                        emails.send_booking_confirmation(booking,request)

        except Exception as e:
            print e
            if 'ps_booking_internal' in request.COOKIES:
                return redirect('home')
            elif ('ps_last_booking' in request.session) and Booking.objects.filter(id=request.session['ps_last_booking']).exists():
                booking = Booking.objects.get(id=request.session['ps_last_booking'])
                book_inv = BookingInvoice.objects.get(booking=booking).invoice_reference
            else:
                return redirect('home')

        if request.user.is_staff:
            return redirect('home')
        context = {
            'booking': booking,
            'book_inv': book_inv
        }
        return render(request, self.template_name, context)


class MyBookingsView(LoginRequiredMixin, TemplateView):
    template_name = 'mooring/booking/my_bookings.html'

    def get(self, request, *args, **kwargs):
        bookings = Booking.objects.filter(customer=request.user, booking_type__in=(0, 1), is_canceled=False)
        admissions = AdmissionsBooking.objects.filter(customer=request.user, booking_type__in=(0, 1))
        today = timezone.now().date()

        ad_currents = admissions.filter(arrivalDate__gte=today).order_by('arrivalDate')
        ad_current = []
        for ad in ad_currents:
            to_add = [ad, AdmissionsBookingInvoice.objects.get(admissions_booking=ad).invoice_reference]
            ad_current.append(to_add)
        ad_pasts = admissions.filter(arrivalDate__lt=today).order_by('-arrivalDate')
        ad_past = []
        for ad in ad_pasts:
            to_add = [ad, AdmissionsBookingInvoice.objects.get(admissions_booking=ad).invoice_reference]
            ad_past.append(to_add)

        bk_currents = bookings.filter(departure__gte=today).order_by('arrival')
        bk_current = []
        for bk in bk_currents:
            to_add = [bk, BookingInvoice.objects.get(booking=bk).invoice_reference]
            bk_current.append(to_add)
        bk_pasts = bookings.filter(departure__lt=today).order_by('-arrival')
        bk_past = []
        for bk in bk_pasts:
            to_add = [bk, BookingInvoice.objects.get(booking=bk).invoice_reference]
            bk_past.append(to_add)
        context = {
            'current_bookings': bk_current,
            'past_bookings': bk_past,
            'current_admissions': ad_current,
            'past_admissions': ad_past,
            # 'admissions_invoice': AdmissionsBookingInvoice.objects.filter(admissions_booking__in=admissions)
        }
        return render(request, self.template_name, context)

class ViewBookingView(LoginRequiredMixin, TemplateView):
    template_name = 'mooring/booking/change_booking.html'

    def get(self, request, *args, **kwargs):
        booking_id = kwargs['pk']
        booking = None
        if request.user.is_staff or request.user.is_superuser or Booking.objects.filter(customer=request.user,pk=booking_id).count() == 1:
#             booking = Booking.objects.get(customer=request.user, booking_type__in=(0, 1), is_canceled=False, pk=booking_id)
             booking = Booking.objects.get(pk=booking_id)
        context = {
           'booking_id': booking_id,
           'booking': booking
 #           'past_bookings': bk_past,
 #           'current_admissions': ad_current,
 #           'past_admissions': ad_past,
            # 'admissions_invoice': AdmissionsBookingInvoice.objects.filter(admissions_booking__in=admissions)
        }
        return render(request, self.template_name, context)


class ChangeBookingView(LoginRequiredMixin, TemplateView):
    template_name = 'mooring/booking/change_booking.html'

    def get(self, request, *args, **kwargs):
        booking_id = kwargs['pk']
        booking = None
        if request.user.is_staff or request.user.is_superuser or Booking.objects.filter(customer=request.user,pk=booking_id).count() == 1:

#             booking = Booking.objects.get(customer=request.user, booking_type__in=(0, 1), is_canceled=False, pk=booking_id)
             booking = Booking.objects.get(pk=booking_id)
             if booking.booking_type == 4:
                  print "BOOKING HAS BEEN CANCELLED"
                  return HttpResponseRedirect(reverse('home'))
                 
             booking_temp = Booking.objects.create(mooringarea=booking.mooringarea,
                                                   booking_type=3,
                                                   expiry_time=timezone.now()+timedelta(seconds=settings.BOOKING_TIMEOUT),
                                                   details=booking.details,
                                                   arrival=booking.arrival,departure=booking.departure, old_booking=booking)
       
	     #request.session['ps_booking'] = booking_temp.id
             #request.session.modified = True
             booking_items = MooringsiteBooking.objects.filter(booking=booking)
             for bi in booking_items:
                  cb =  MooringsiteBooking.objects.create(
                         campsite=bi.campsite,
                         booking_type=3,
                         date=bi.date,
                         from_dt=bi.from_dt,
                         to_dt=bi.to_dt,
                         booking=booking_temp,
                         amount=bi.amount,
                         booking_period_option=bi.booking_period_option
                       )

             request.session['ps_booking'] = booking_temp.id
             #request.session['ps_booking_old'] =  booking.id
             request.session.modified = True
             return HttpResponseRedirect(reverse('mooring_availaiblity2_selector'))
         
#        ad_currents = admissions.filter(arrivalDate__gte=today).order_by('arrivalDate')
#        ad_current = []
#        for ad in ad_currents:
#            to_add = [ad, AdmissionsBookingInvoice.objects.get(admissions_booking=ad).invoice_reference]
#            ad_current.append(to_add)
#        ad_pasts = admissions.filter(arrivalDate__lt=today).order_by('-arrivalDate')
#        ad_past = []
#        for ad in ad_pasts:
#            to_add = [ad, AdmissionsBookingInvoice.objects.get(admissions_booking=ad).invoice_reference]
#            ad_past.append(to_add)
#
#        bk_currents = bookings.filter(departure__gte=today).order_by('arrival')
#        bk_current = []
#        for bk in bk_currents:
#            to_add = [bk, BookingInvoice.objects.get(booking=bk).invoice_reference]
#            bk_current.append(to_add)
#        bk_pasts = bookings.filter(departure__lt=today).order_by('-arrival')
#        bk_past = []
#        for bk in bk_pasts:
#            to_add = [bk, BookingInvoice.objects.get(booking=bk).invoice_reference]
#            bk_past.append(to_add)
 #       context = {
#           'booking_id': booking_id,    
#           'booking': booking
 #           'past_bookings': bk_past,
 #           'current_admissions': ad_current,
 #           'past_admissions': ad_past,
            # 'admissions_invoice': AdmissionsBookingInvoice.objects.filter(admissions_booking__in=admissions)
#        }
#        return render(request, self.template_name, context)



#        cb =    MooringsiteBooking.objects.create(
#                  campsite=mooringsite,
#                  booking_type=3,
#                  date=booking_date,
#                  from_dt=start_booking_date+' '+str(booking_period.start_time),
#                  to_dt=finish_booking_date+' '+str(booking_period.finish_time),
#                  booking=booking,
#                  amount=amount,
#                  booking_period_option=booking_period
#                  )

#        response_data['result'] = 'success'
#        response_data['message'] = ''


        return HttpResponseRedirect(reverse('home'))


class AdmissionFeesView(TemplateView):
    template_name = 'mooring/admissions/admissions_form.html'

class AdmissionsCostView(TemplateView):
    template_name = 'mooring/admissions/admissions_cost.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if self.request.user.is_staff:
                return render(self.request, self.template_name)
            return redirect('ps_home')
        return redirect('ps_home')

class MarinastayRoutingView(TemplateView):
    template_name = 'mooring/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_officer(self.request.user):
                return redirect('dash-campgrounds')
            return redirect('public_my_bookings')
        kwargs['form'] = LoginForm
        return super(MarinastayRoutingView, self).get(*args, **kwargs)

class InvoicePDFView(InvoiceOwnerMixin,View):
    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        response = HttpResponse(content_type='application/pdf')
        mooring_var = mooring_url(request)
        response.write(create_invoice_pdf_bytes('invoice.pdf',invoice, request, mooring_var))
        return response

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice

class MapView(TemplateView):
    template_name = 'mooring/map.html'

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'mooring/profile.html'
