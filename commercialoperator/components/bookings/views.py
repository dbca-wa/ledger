from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.db import transaction

from datetime import datetime, timedelta

from commercialoperator.components.proposals.models import Proposal
from commercialoperator.components.compliances.models import Compliance
from commercialoperator.components.main.models import Park
from commercialoperator.components.bookings.context_processors import commercialoperator_url, template_context
from commercialoperator.components.bookings.invoice_pdf import create_invoice_pdf_bytes
from commercialoperator.components.bookings.confirmation_pdf import create_confirmation_pdf_bytes
from commercialoperator.components.bookings.email import (
    send_invoice_tclass_email_notification,
    send_confirmation_tclass_email_notification,
    send_application_fee_invoice_tclass_email_notification,
    send_application_fee_confirmation_tclass_email_notification,
)
from commercialoperator.components.bookings.utils import (
    create_booking,
    get_session_booking,
    set_session_booking,
    delete_session_booking,
    create_lines,
    checkout,
    create_fee_lines,
    get_session_application_invoice,
    set_session_application_invoice,
    delete_session_application_invoice
)

from commercialoperator.components.proposals.serializers import ProposalSerializer

from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission, get_cookie_basket
from ledger.payments.utils import oracle_parser_on_invoice,update_payments
import json
from decimal import Decimal

from commercialoperator.components.bookings.models import Booking, ParkBooking, BookingInvoice, ApplicationFee, ApplicationFeeInvoice
from ledger.payments.models import Invoice
from ledger.basket.models import Basket
from ledger.payments.mixins import InvoiceOwnerMixin
from oscar.apps.order.models import Order

import logging
logger = logging.getLogger('payment_checkout')


class ApplicationFeeView(TemplateView):
    template_name = 'commercialoperator/booking/success.html'

    def get_object(self):
        return get_object_or_404(Proposal, id=self.kwargs['proposal_pk'])

    def post(self, request, *args, **kwargs):

        #proposal_id = int(kwargs['proposal_pk'])
        #proposal = Proposal.objects.get(id=proposal_id)

        proposal = self.get_object()
        application_fee = ApplicationFee.objects.create(proposal=proposal, created_by=request.user, payment_type=3)
        #import ipdb; ipdb.set_trace()

        try:
            with transaction.atomic():
                set_session_application_invoice(request.session, application_fee)
                lines = create_fee_lines(proposal)
                checkout_response = checkout(
                    request,
                    proposal,
                    lines,
                    return_url_ns='fee_success',
                    return_preload_url_ns='fee_success',
                    invoice_text='Application Fee'
                )

                logger.info('{} built payment line item {} for Application Fee and handing over to payment gateway'.format('User {} with id {}'.format(proposal.submitter.get_full_name(),proposal.submitter.id), proposal.id))
                return checkout_response

        except Exception, e:
            logger.error('Error Creating Application Fee: {}'.format(e))
            if application_fee:
                application_fee.delete()
            raise


class MakePaymentView(TemplateView):
    #template_name = 'mooring/booking/make_booking.html'
    template_name = 'commercialoperator/booking/success.html'

    def post(self, request, *args, **kwargs):
        #import ipdb; ipdb.set_trace()

        proposal_id = int(kwargs['proposal_pk'])
        proposal = Proposal.objects.get(id=proposal_id)

        try:
            booking = create_booking(request, proposal_id)
            with transaction.atomic():
                set_session_booking(request.session,booking)
                lines = create_lines(request)
                checkout_response = checkout(
                    request,
                    proposal,
                    lines,
                    return_url_ns='public_booking_success',
                    return_preload_url_ns='public_booking_success',
                    invoice_text='Payment Invoice'
                )

                logger.info('{} built payment line items {} for Park Bookings and handing over to payment gateway'.format('User {} with id {}'.format(proposal.submitter.get_full_name(),proposal.submitter.id), proposal.id))
                #import ipdb; ipdb.set_trace()
                return checkout_response

#                # FIXME: replace with session check
#                invoice = None
#                if 'invoice=' in checkout_response.url:
#                    invoice = checkout_response.url.split('invoice=', 1)[1]
#                else:
#                    for h in reversed(checkout_response.history):
#                        if 'invoice=' in h.url:
#                            invoice = h.url.split('invoice=', 1)[1]
#                            break
#                print ("-== internal_booking ==-")
#                self.internal_create_booking_invoice(booking, invoice)
#                delete_session_booking(request.session)
#
#                return checkout_response

        except Exception, e:
            logger.error('Error Creating booking: {}'.format(e))
            if booking:
                booking.delete()
            raise

from commercialoperator.components.proposals.utils import proposal_submit
class ApplicationFeeSuccessView(TemplateView):
    template_name = 'commercialoperator/booking/success_fee.html'

    def get(self, request, *args, **kwargs):
        print (" APPLICATION FEE SUCCESS ")
#        for ss in request.session.keys():
#            print (ss)
#            print (request.session[ss])

        proposal = None
        submitter = None
        invoice = None
        try:
            print '0a Session: {}'.format(request.session['cols_app_invoice'] if 'cols_app_invoice' in request.session else '')
            print '0b Last Session: {}'.format(request.session['cols_last_app_invoice'] if 'cols_last_app_invoice' in request.session else '')
            #import ipdb; ipdb.set_trace()
            context = template_context(self.request)
            basket = None
            application_fee = get_session_application_invoice(request.session)
            print (" Session (App Fee) {}".format(application_fee))
            print (" 1 ")
            proposal = application_fee.proposal
            print (" 2 ")
            #proposal = get_session_application_invoice(request.session)

            try:
                recipient = proposal.applicant.email
                submitter = proposal.applicant
            except:
                recipient = proposal.submitter.email
                submitter = proposal.submitter

            print (" 3 ")
            if self.request.user.is_authenticated():
                basket = Basket.objects.filter(status='Submitted', owner=request.user).order_by('-id')[:1]
                #basket_open = Basket.objects.filter(status='Open', owner=request.user).order_by('-id')[:1]
                #print '3a - Basket ID: {}, Status: {}'.format(basket_open[0].id, basket_open[0].status)
                print (" 3a ")
            else:
                basket = Basket.objects.filter(status='Submitted', owner=booking.proposal.submitter).order_by('-id')[:1]
                print (" 3b ")

            print (" 4 ")
            order = Order.objects.get(basket=basket[0])
            print (" 5 ")
            invoice = Invoice.objects.get(order_number=order.number)
            print (" 6 ")
            invoice_ref = invoice.reference
            print (" 7 ")
            #book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=invoice_ref)
            fee_inv, created = ApplicationFeeInvoice.objects.get_or_create(application_fee=application_fee, invoice_reference=invoice_ref)

            #import ipdb; ipdb.set_trace()
            print 'Basket ID: {}, Status: {}, Order: {}, Invoice: {}'.format(basket[0].id, basket[0].status, order, invoice_ref)
            if application_fee.payment_type == 3:
                try:
                    inv = Invoice.objects.get(reference=invoice_ref)
                    order = Order.objects.get(number=inv.order_number)
                    order.user = submitter
                    order.save()
                    print (" 8 ")
                except Invoice.DoesNotExist:
                    print ("INVOICE ERROR")
                    logger.error('{} tried paying an application fee with an incorrect invoice'.format('User {} with id {}'.format(proposal.submitter.get_full_name(), proposal.submitter.id) if proposal.submitter else 'An anonymous user'))
                    return redirect('external-proposal-detail', args=(proposal.id,))
                #if inv.system not in ['S557']:
                print ("INVOICE SYSTEM {}, settings.PS_PAYMENT_SYSTEM_ID {}".format(inv.system, settings.PS_PAYMENT_SYSTEM_ID))
                if inv.system not in ['0557']:
                    print ("SYSTEM ERROR")
                    logger.error('{} tried paying an application fee with an invoice from another system with reference number {}'.format('User {} with id {}'.format(proposal.submitter.get_full_name(), proposal.submitter.id) if proposal.submitter else 'An anonymous user',inv.reference))
                    return redirect('external-proposal-detail', args=(proposal.id,))

                if fee_inv:
                    application_fee.payment_type = 1  # internet booking
                    application_fee.expiry_time = None
                    update_payments(invoice_ref)

                    print (" 9 ")
                    proposal = proposal_submit(proposal, request)
                    if proposal and (invoice.payment_status == 'paid' or invoice.payment_status == 'over_paid'):
                        proposal.fee_invoice_reference = invoice_ref
                        proposal.save()
                        print (" 10 ")
                    else:
                        logger.error('Invoice payment status is {}'.format(invoice.payment_status))
                        raise

                    application_fee.save()
                    print (" 11 ")
                    request.session['cols_last_app_invoice'] = application_fee.id
                    delete_session_application_invoice(request.session)
                    print '11a Session: {}'.format(request.session['cols_app_invoice'] if 'cols_app_invoice' in request.session else '')
                    print '11b Last Session: {}'.format(request.session['cols_last_app_invoice'] if 'cols_last_app_invoice' in request.session else '')

                    send_application_fee_invoice_tclass_email_notification(request, proposal, invoice, recipients=[recipient])
                    send_application_fee_confirmation_tclass_email_notification(request, proposal, invoice, recipients=[recipient])
                    print (" 12 ")

                    context = {
                        'proposal': proposal,
                        'submitter': submitter,
                        'fee_invoice': invoice
                    }
                    print (" 13 ")
                    return render(request, self.template_name, context)

        except Exception as e:
            print 'My Exception: {}'.format(e)
            if ('cols_last_app_invoice' in request.session) and ApplicationFee.objects.filter(id=request.session['cols_last_app_invoice']).exists():
                application_fee = ApplicationFee.objects.get(id=request.session['cols_last_app_invoice'])
                proposal = application_fee.proposal

                try:
                    recipient = proposal.applicant.email
                    submitter = proposal.applicant
                except:
                    recipient = proposal.submitter.email
                    submitter = proposal.submitter

                if ApplicationFeeInvoice.objects.filter(application_fee=application_fee).count() > 0:
                    afi = ApplicationFeeInvoice.objects.filter(application_fee=application_fee)
                    #invoice = afi[0].invoice_reference
                    invoice = afi[0]
                    print (" 13a: {} ".format(invoice))
#                    book_inv = BookingInvoice.objects.get(booking=booking).invoice_reference
            else:
                #import ipdb; ipdb.set_trace()
                print (" 14 ")
                return redirect('home')

        context = {
            #'booking': booking,
            #'book_inv': [app_inv]
            'proposal': proposal,
            'submitter': submitter,
            'fee_invoice': invoice
        }
        print (" 15 ")
        return render(request, self.template_name, context)


class _ApplicationFeeSuccessView(TemplateView):
    template_name = 'commercialoperator/booking/success_fee.html'

    def get(self, request, *args, **kwargs):

        context = template_context(self.request)
        basket = None
        proposal = get_session_application_invoice(request.session)

        #import ipdb; ipdb.set_trace()
        if proposal.fee_paid:
            #proposal.fee_invoice_reference = request.session.pop('checkout_invoice')
            #proposal.save()
            #TODO must remove this ''if-block' - temp hack, the method is executing twice - need to FIX
            invoice = Invoice.objects.get(reference=proposal.fee_invoice_reference)
            try:
                recipient = proposal.applicant.email
                submitter = proposal.applicant
            except:
                recipient = proposal.submitter.email
                submitter = proposal.submitter
            send_application_fee_invoice_tclass_email_notification(request, proposal, invoice, recipients=[recipient])

            context.update({
                'proposal': proposal,
                'submitter': submitter,
                'fee_invoice': invoice
            })
            return render(request, self.template_name, context)

        print (" APPLICATION FEE SUCCESS ")
        if self.request.user.is_authenticated():
            basket = Basket.objects.filter(status='Submitted', owner=request.user).order_by('-id')[:1]
        else:
            basket = Basket.objects.filter(status='Submitted', owner=booking.proposal.submitter).order_by('-id')[:1]

        order = Order.objects.get(basket=basket[0])
        invoice = Invoice.objects.get(order_number=order.number)
        invoice_ref = invoice.reference
        #book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=invoice_ref)

        #import ipdb; ipdb.set_trace()
        proposal = proposal_submit(proposal, request)
        if proposal and (invoice.payment_status == 'paid' or invoice.payment_status == 'over_paid'):
            proposal.fee_invoice_reference = invoice_ref
            proposal.save()
        else:
            logger.error('Invoice payment status is {}'.format(invoice.payment_status))
            raise

        print ("APPLICATION FEE")
        try:
            recipient = proposal.applicant.email
            submitter = proposal.applicant
        except:
            recipient = proposal.submitter.email
            submitter = proposal.submitter
        #import ipdb; ipdb.set_trace()
        send_application_fee_invoice_tclass_email_notification(request, proposal, invoice, recipients=[recipient])
        send_application_fee_confirmation_tclass_email_notification(request, proposal, invoice, recipients=[recipient])

        #delete_session_booking(request.session)

        context.update({
            'proposal': proposal,
            'submitter': submitter,
            'fee_invoice': invoice
        })
        return render(request, self.template_name, context)


class BookingSuccessView(TemplateView):
    template_name = 'commercialoperator/booking/success.html'

    def get(self, request, *args, **kwargs):
        print (" BOOKING SUCCESS ")

        context = template_context(self.request)
        basket = None
        booking = get_session_booking(request.session)

        if self.request.user.is_authenticated():
            basket = Basket.objects.filter(status='Submitted', owner=request.user).order_by('-id')[:1]
        else:
            basket = Basket.objects.filter(status='Submitted', owner=booking.proposal.submitter).order_by('-id')[:1]

        order = Order.objects.get(basket=basket[0])
        invoice = Invoice.objects.get(order_number=order.number)
        invoice_ref = invoice.reference
        book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=invoice_ref)

        print ("BOOKING")

        try:
            recipient = booking.proposal.applicant.email
            submitter = booking.proposal.applicant
        except:
            recipient = booking.proposal.submitter.email
            submitter = booking.proposal.submitter

        #import ipdb; ipdb.set_trace()
        send_invoice_tclass_email_notification(request, booking, invoice, recipients=[recipient])
        send_confirmation_tclass_email_notification(request, booking, invoice, recipients=[recipient])

        #delete_session_booking(request.session)

        context.update({
            'booking_id': booking.id,
            'submitter': submitter,
            'book_inv': [book_inv]
        })
        return render(request, self.template_name, context)


class InvoicePDFView(InvoiceOwnerMixin,View):
    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        response = HttpResponse(content_type='application/pdf')
        response.write(create_invoice_pdf_bytes('invoice.pdf',invoice))
        return response

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice


class ConfirmationPDFView(InvoiceOwnerMixin,View):
    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        bi=BookingInvoice.objects.filter(invoice_reference=invoice.reference).last()

        response = HttpResponse(content_type='application/pdf')
        response.write(create_confirmation_pdf_bytes('confirmation.pdf',invoice, bi.booking))
        return response

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice

