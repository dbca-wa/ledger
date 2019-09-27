from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from datetime import datetime, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from commercialoperator.components.main.models import Park
from commercialoperator.components.proposals.models import Proposal
from commercialoperator.components.organisations.models import Organisation
from commercialoperator.components.bookings.models import Booking, ParkBooking, BookingInvoice, ApplicationFee
from ledger.checkout.utils import create_basket_session, create_checkout_session, calculate_excl_gst
from ledger.payments.models import Invoice
from ledger.payments.utils import oracle_parser
import json
from decimal import Decimal


import logging
logger = logging.getLogger('payment_checkout')


def create_booking(request, proposal, booking_type=Booking.BOOKING_TYPE_TEMPORARY):
    """ Create the ledger lines - line items for invoice sent to payment system """

    if booking_type == Booking.BOOKING_TYPE_MONTHLY_INVOICING and proposal.org_applicant and proposal.org_applicant.monthly_invoicing_allowed:
        booking, created = Booking.objects.get_or_create(
            invoices__isnull=True,
            proposal_id=proposal_id,
            booking_type=booking_type,
            created__month=timezone.now().month,
            defaults={
                'created_by': request.user,
                'created': timezone.now(),
            }
        )
    else:
        booking = Booking.objects.create(proposal_id=proposal_id, created_by=request.user, booking_type=booking_type)

    #Booking.objects.filter(invoices__isnull=True, booking_type=4, proposal_id=478, proposal__org_applicant=org)

    tbody = json.loads(request.POST['payment'])['tbody']
    for row in tbody:
        park_id = row[0]['value']
        arrival = row[1]
        no_adults = int(row[2]) if row[2] else 0
        no_children = int(row[3]) if row[3] else 0
        no_free_of_charge = int(row[4]) if row[4] else 0
        park = Park.objects.get(id=park_id)

        if any([no_adults, no_children, no_free_of_charge]) > 0:
            park_booking = ParkBooking.objects.create(
                booking = booking,
                park_id = park_id,
                arrival = datetime.strptime(arrival, '%Y-%m-%d').date(),
                no_adults = no_adults,
                no_children = no_children,
                no_free_of_charge = no_free_of_charge,
                cost = no_adults*park.adult_price + no_children*park.child_price
            )
    if not park_booking:
        raise ValidationError('Must have at least one person visiting the park')

    return booking

def create_monthly_invoice(offset_months=-1):
    bookings = Booking.objects.filter(
        invoices__isnull=True,
        booking_type=Booking.BOOKING_TYPE_MONTHLY_INVOICING,
        created__month=(timezone.now() + relativedelta(months=offset_months)).month
    )

    failed_bookings = []
    for booking in bookings:
        with transaction.atomic():
            if booking.booking_type == Booking.BOOKING_TYPE_MONTHLY_INVOICING and booking.proposal.org_applicant and booking.proposal.org_applicant.monthly_invoicing_allowed:
                try:
                    order = create_invoice(booking, payment_method='monthly_invoicing')
                    invoice = Invoice.objects.get(order_number=order.number)
                    invoice.settlement_date = calc_payment_due_date(booking, invoice.created)
                    invoice.save()
                    book_inv = BookingInvoice.objects.create(booking=booking, invoice_reference=invoice.reference, payment_method=invoice.payment_method)
                    #send_monthly_invoice_tclass_email_notification(request, booking, invoice, recipients=[booking.proposal.applicant_email])
                except:
                    logger.error('Failed to create monthly invoice for booking_id {}'.format(booking.id))
                    failed_bookings.append(booking.id)

    return failed_bookings

def calc_payment_due_date(booking, _date):
    org_applicant = booking.proposal.org_applicant
    if isinstance(org_applicant, Organisation):
        return calc_monthly_invoicing_date(_date, org_applicant.monthly_invoicing_period) + relativedelta(days=org_applicant.monthly_payment_due_period)

def calc_monthly_invoicing_date(_date, offset_days):
    return _date + relativedelta(days=offset_days)

def get_session_booking(session):
    if 'cols_booking' in session:
        booking_id = session['cols_booking']
    else:
        raise Exception('Booking not in Session')

    try:
        return Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        raise Exception('Booking not found for booking_id {}'.format(booking_id))


def set_session_booking(session, booking):
    session['cols_booking'] = booking.id
    session.modified = True

def delete_session_booking(session):
    if 'cols_booking' in session:
        del session['cols_booking']
        session.modified = True

def get_session_application_invoice(session):
    """ Application Fee session ID """
    if 'cols_app_invoice' in session:
        application_fee_id = session['cols_app_invoice']
    else:
        raise Exception('Application not in Session')

    try:
        #return Invoice.objects.get(id=application_invoice_id)
        #return Proposal.objects.get(id=proposal_id)
        return ApplicationFee.objects.get(id=application_fee_id)
    except Invoice.DoesNotExist:
        raise Exception('Application not found for application {}'.format(application_fee_id))

def set_session_application_invoice(session, application_fee):
    """ Application Fee session ID """
    session['cols_app_invoice'] = application_fee.id
    session.modified = True

def delete_session_application_invoice(session):
    """ Application Fee session ID """
    if 'cols_app_invoice' in session:
        del session['cols_app_invoice']
        session.modified = True

def create_fee_lines(proposal, invoice_text=None, vouchers=[], internal=False):
    """ Create the ledger lines - line item for application fee sent to payment system """

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    application_price = proposal.application_type.application_fee
    licence_price = proposal.licence_fee_amount
    line_items = [
        {   'ledger_description': 'Application Fee - {} - {}'.format(now, proposal.lodgement_number),
            'oracle_code': proposal.application_type.oracle_code_application,
            'price_incl_tax':  application_price,
            'price_excl_tax':  application_price if proposal.application_type.is_gst_exempt else calculate_excl_gst(application_price),
            'quantity': 1,
        },
        {   'ledger_description': 'Licence Charge {} - {} - {}'.format(proposal.other_details.get_preferred_licence_period_display(), now, proposal.lodgement_number),
            'oracle_code': proposal.application_type.oracle_code_licence,
            'price_incl_tax':  licence_price,
            'price_excl_tax':  licence_price if proposal.application_type.is_gst_exempt else calculate_excl_gst(licence_price),
            'quantity': 1,
        }
    ]
    logger.info('{}'.format(line_items))
    return line_items

#def create_lines(request, invoice_text=None, vouchers=[], internal=False):
#    """ Create the ledger lines - line items for invoice sent to payment system """
#
#    def add_line_item(park, arrival, age_group, price, no_persons):
#        price = Decimal(price)
#        if no_persons > 0:
#            return {
#                'ledger_description': '{} - {} - {}'.format(park.name, arrival, age_group),
#                'oracle_code': park.oracle_code,
#                'price_incl_tax':  price,
#                'price_excl_tax':  price if park.is_gst_exempt else calculate_excl_gst(price),
#                'quantity': no_persons,
#            }
#        return None
#
#    lines = []
#    tbody = json.loads(request.POST['payment'])['tbody']
#    for row in tbody:
#        park_id = row[0]['value']
#        arrival = row[1]
#        no_adults = int(row[2]) if row[2] else 0
#        no_children = int(row[3]) if row[3] else 0
#        no_free_of_charge = int(row[4]) if row[4] else 0
#        park= Park.objects.get(id=park_id)
#
#        if no_adults > 0:
#            lines.append(add_line_item(park, arrival, 'Adult', price=park.adult_price, no_persons=no_adults))
#
#        if no_children > 0:
#            lines.append(add_line_item(park, arrival, 'Child', price=park.child_price, no_persons=no_children))
#
#        if no_free_of_charge > 0:
#            lines.append(add_line_item(park, arrival, 'Free', price=0.0, no_persons=no_free_of_charge))
#
#    return lines

def checkout(request, proposal, lines, return_url_ns='public_booking_success', return_preload_url_ns='public_booking_success', invoice_text=None, vouchers=[], proxy=False, bpay_allowed=False, monthly_invoicing_allowed=False):
    basket_params = {
        'products': lines,
        'vouchers': vouchers,
        'system': settings.PAYMENT_SYSTEM_ID,
        'custom_basket': True,
        'bpay_allowed': bpay_allowed,
        'monthly_invoicing_allowed': monthly_invoicing_allowed,
    }

    basket, basket_hash = create_basket_session(request, basket_params)
    #fallback_url = request.build_absolute_uri('/')
    checkout_params = {
        'system': settings.PAYMENT_SYSTEM_ID,
        'fallback_url': request.build_absolute_uri('/'),                                      # 'http://mooring-ria-jm.dbca.wa.gov.au/'
        'return_url': request.build_absolute_uri(reverse(return_url_ns)),          # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
        'return_preload_url': request.build_absolute_uri(reverse(return_url_ns)),  # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
        #'fallback_url': fallback_url,
        #'return_url': fallback_url,
        #'return_preload_url': fallback_url,
        'force_redirect': True,
        #'proxy': proxy,
        'invoice_text': invoice_text,                                                         # 'Reservation for Jawaid Mushtaq from 2019-05-17 to 2019-05-19 at RIA 005'
    }
#    if not internal:
#        checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
    #if internal or request.user.is_anonymous():
    if proxy or request.user.is_anonymous():
        #checkout_params['basket_owner'] = booking.customer.id
        checkout_params['basket_owner'] = proposal.submitter_id


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


def oracle_integration(date,override):
    system = '0557'
    oracle_codes = oracle_parser(date, system, 'Commercial Operator Licensing', override=override)


def test_create_invoice(payment_method='bpay'):
    """
    This will create and invoice and order from a basket bypassing the session
    and payment bpoint code constraints.

    To test:
        from ledger.payments.invoice.utils import test_create_invoice


        from ledger.checkout.utils import createCustomBasket
        from ledger.payments.invoice.utils import CreateInvoiceBasket
        from decimal import Decimal

        products = [{u'oracle_code': u'ABC123 GST', u'price_incl_tax': Decimal('10.00'), u'price_excl_tax': Decimal('9.090909090909'), u'ledger_description': u'Booking Date 2019-09-24: Neale Junction Nature Reserve - 2019-09-24 - Adult', u'quantity': 1}]
        or
        products = Booking.objects.last().as_line_items

        user = EmailUser.objects.get(email__icontains='walter.genuit@dbca')
        payment_method = 'bpay' (or 'monthly_invoicing')

        basket  = createCustomBasket(products, user, 'S557', bpay_allowed=True, monthly_invoicing_allowed=True)
        order = CreateInvoiceBasket(payment_method='bpay', system='0557').create_invoice_and_order(basket, 0, None, None, user=user, invoice_text='CIB7')

        Invoice.objects.get(order_number=order.number)
        <Invoice: Invoice #05572188633>

        To view:
            http://localhost:8499/ledger/payments/invoice/05572188633

    """
    from ledger.checkout.utils import createCustomBasket
    from ledger.payments.invoice.utils import CreateInvoiceBasket
    from ledger.accounts.models import EmailUser
    from decimal import Decimal

    products = [{
        'oracle_code': 'ABC123 GST',
        'price_incl_tax': Decimal('10.00'),
        'price_excl_tax': Decimal('9.090909090909'),
        'ledger_description': 'Booking Date 2019-09-24: Neale Junction Nature Reserve - 2019-09-24 - Adult',
        'quantity': 1
    }]
    #products = Booking.objects.last().as_line_items

    user = EmailUser.objects.get(email='jawaid.mushtaq@dbca.wa.gov.au')
    #payment_method = 'bpay'
    payment_method = 'monthly_invoicing'

    basket  = createCustomBasket(products, user, 'S557', bpay_allowed=True, monthly_invoicing_allowed=True)
    order = CreateInvoiceBasket(payment_method=payment_method, system='0557').create_invoice_and_order(basket, 0, None, None, user=user, invoice_text='CIB7')
    print 'Created Order: {}'.format(order.number)
    print 'Created Invoice: {}'.format(Invoice.objects.get(order_number=order.number))

    return order

def create_invoice(booking, payment_method='bpay'):
    """
    This will create and invoice and order from a basket bypassing the session
    and payment bpoint code constraints.
    """
    from ledger.checkout.utils import createCustomBasket
    from ledger.payments.invoice.utils import CreateInvoiceBasket
    from ledger.accounts.models import EmailUser
    from decimal import Decimal

    products = [{
        'oracle_code': 'ABC123 GST',
        'price_incl_tax': Decimal('10.00'),
        'price_excl_tax': Decimal('9.090909090909'),
        'ledger_description': 'Booking Date 2019-09-24: Neale Junction Nature Reserve - 2019-09-24 - Adult',
        'quantity': 1
    }]
    #products = Booking.objects.last().as_line_items

    user = EmailUser.objects.get(email='jawaid.mushtaq@dbca.wa.gov.au')
    #payment_method = 'bpay'
    payment_method = 'monthly_invoicing'

    basket  = createCustomBasket(products, user, 'S557', bpay_allowed=True, monthly_invoicing_allowed=True)
    order = CreateInvoiceBasket(payment_method=payment_method, system='0557').create_invoice_and_order(basket, 0, None, None, user=user, invoice_text='CIB7')
    print 'Created Order: {}'.format(order.number)
    print 'Created Invoice: {}'.format(Invoice.objects.get(order_number=order.number))

    return order


