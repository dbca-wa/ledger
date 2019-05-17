from datetime import datetime, timedelta, date
import traceback
from decimal import *
import json
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from ledger.payments.models import Invoice,OracleInterface,CashTransaction
from ledger.payments.utils import oracle_parser,update_payments
from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission, get_cookie_basket
#from mooring.models import (MooringArea, Mooringsite, MooringsiteRate, MooringsiteBooking, Booking, BookingInvoice, MooringsiteBookingRange, Rate, MooringAreaBookingRange,MooringAreaStayHistory, MooringsiteRate, MarinaEntryRate, BookingVehicleRego, AdmissionsBooking, AdmissionsOracleCode, AdmissionsRate, AdmissionsLine, ChangePricePeriod, CancelPricePeriod, GlobalSettings, MooringAreaGroup, AdmissionsLocation, ChangeGroup, CancelGroup, BookingPeriod, BookingPeriodOption)
#from mooring.serialisers import BookingRegoSerializer, MooringsiteRateSerializer, MarinaEntryRateSerializer, RateSerializer, MooringsiteRateReadonlySerializer, AdmissionsRateSerializer
#from mooring.emails import send_booking_invoice,send_booking_confirmation


def checkout(request, booking, lines, invoice_text=None, vouchers=[], internal=False):
    import ipdb; ipdb.set_trace()
    basket_params = {
        'products': lines,
        'vouchers': vouchers,
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'custom_basket': True,
    }

    basket, basket_hash = create_basket_session(request, basket_params)
    checkout_params = {
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'fallback_url': request.build_absolute_uri('/'),                                      # 'http://mooring-ria-jm.dbca.wa.gov.au/'
        'return_url': request.build_absolute_uri(reverse('public_booking_success')),          # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
        'return_preload_url': request.build_absolute_uri(reverse('public_booking_success')),  # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
        'force_redirect': True,
        'proxy': True if internal else False,
        'invoice_text': invoice_text,                                                         # 'Reservation for Jawaid Mushtaq from 2019-05-17 to 2019-05-19 at RIA 005'
    }
#    if not internal:
#        checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
    if internal or request.user.is_anonymous():
        checkout_params['basket_owner'] = booking.customer.id


    create_checkout_session(request, checkout_params)

#    if internal:
#        response = place_order_submission(request)
#    else:
    response = HttpResponseRedirect(reverse('checkout:index'))
    # inject the current basket into the redirect response cookies
    # or else, anonymous users will be directionless
    response.set_cookie(
            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
    )

#    if booking.cost_total < 0:
#        response = HttpResponseRedirect('/refund-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )
#
#    # Zero booking costs
#    if booking.cost_total < 1 and booking.cost_total > -1:
#        response = HttpResponseRedirect('/no-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )

    return response

