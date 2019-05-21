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
from django.views.decorators.http import require_http_methods
from commercialoperator.context_processors import commercialoperator_url, template_context
from commercialoperator.components.proposals.models import Booking, ParkBooking
from commercialoperator.helpers import is_internal
from commercialoperator import pdf


@require_http_methods(['GET'])
def get_confirmation(request, *args, **kwargs):

    # Get branding configuration
    context_processor = template_context(request)
    # fetch booking for ID
    booking_id = kwargs.get('booking_id', None)
    if (booking_id is None):
        return HttpResponse('Booking ID not specified', status=400)

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return HttpResponse('Booking unavailable', status=403)

    try:
        park_bookings = ParkBooking.objects.filter(booking=booking).order_by('arrival')
    except ParkBooking.DoesNotExist:
        return HttpResponse('Park Booking unavailable', status=403)

    # check permissions
    #if not ((request.user == booking.proposal.submitter) or is_officer(request.user) or (booking.id == request.session.get('ps_last_booking', None))):
    if not ((request.user == booking.proposal.submitter) or is_internal(request) or (booking.id == request.session.get('cols_booking', None))):
        return HttpResponse('Booking unavailable', status=403)

    # check payment status
    #if (not is_officer(request.user)) and (not booking.paid):
    if (not is_internal(request)) and (not booking.paid):
        return HttpResponse('Booking unavailable', status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="confirmation-PS{}.pdf"'.format(booking_id)

    response.write(pdf.create_confirmation(response, booking, park_bookings, context_processor))
    return response

@require_http_methods(['GET'])
def _get_confirmation(request, *args, **kwargs):

    # Get branding configuration
    context_processor = template_context(request)
    # fetch booking for ID
    booking_id = kwargs.get('booking_id', None)
    if (booking_id is None):
        return HttpResponse('Booking ID not specified', status=400)

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return HttpResponse('Booking unavailable', status=403)

    try:
        park_bookings = ParkBooking.objects.filter(booking=booking).order_by('arrival')
    except ParkBooking.DoesNotExist:
        return HttpResponse('Park Booking unavailable', status=403)

    # check permissions
    #if not ((request.user == booking.proposal.submitter) or is_officer(request.user) or (booking.id == request.session.get('ps_last_booking', None))):
    if not ((request.user == booking.proposal.submitter) or is_internal(request) or (booking.id == request.session.get('cols_booking', None))):
        return HttpResponse('Booking unavailable', status=403)

    # check payment status
    #if (not is_officer(request.user)) and (not booking.paid):
    if (not is_internal(request)) and (not booking.paid):
        return HttpResponse('Booking unavailable', status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="confirmation-PS{}.pdf"'.format(booking_id)

    response.write(pdf.create_confirmation(response, booking, park_bookings, context_processor))
    return response


