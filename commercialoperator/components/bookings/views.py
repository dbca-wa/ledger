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

from datetime import datetime, timedelta, date
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from commercialoperator.components.proposals.models import Proposal
from commercialoperator.components.compliances.models import Compliance
from commercialoperator.components.main.models import Park
from commercialoperator.components.organisations.models import Organisation
from commercialoperator.components.bookings.context_processors import commercialoperator_url, template_context
from commercialoperator.components.bookings.invoice_pdf import create_invoice_pdf_bytes
from commercialoperator.components.bookings.confirmation_pdf import create_confirmation_pdf_bytes
from commercialoperator.components.bookings.monthly_confirmation_pdf import create_monthly_confirmation_pdf_bytes
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
    delete_session_application_invoice,
    calc_payment_due_date,
    create_bpay_invoice,
    create_other_invoice,
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
        application_fee = ApplicationFee.objects.create(proposal=proposal, created_by=request.user, payment_type=ApplicationFee.PAYMENT_TYPE_TEMPORARY)

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


class DeferredInvoicingPreviewView(TemplateView):
    template_name = 'commercialoperator/booking/preview.html'

    def post(self, request, *args, **kwargs):

        payment_method = self.request.GET.get('method')
        context = template_context(self.request)
        proposal_id = int(kwargs['proposal_pk'])
        proposal = Proposal.objects.get(id=proposal_id)
        try:
            recipient = proposal.applicant.email
            submitter = proposal.applicant
        except:
            recipient = proposal.submitter.email
            submitter = proposal.submitter

        #if isinstance(proposal.org_applicant, Organisation) and (proposal.org_applicant.monthly_invoicing_allowed or proposal.org_applicant.bpay_allowed or proposal.org_applicant.other_allowed):
        if isinstance(proposal.org_applicant, Organisation) and (proposal.org_applicant.monthly_invoicing_allowed or proposal.org_applicant.bpay_allowed):
            try:
                lines = create_lines(request)
                logger.info('{} Show Park Bookings Preview for BPAY/Other/monthly invoicing'.format('User {} with id {}'.format(proposal.submitter.get_full_name(),proposal.submitter.id), proposal.id))
                context.update({
                    'lines': lines,
                    'line_details': request.POST['payment'],
                    'proposal_id': proposal_id,
                    'submitter': submitter,
                    'payment_method': payment_method,
                })
                return render(request, self.template_name, context)


            except Exception, e:
                logger.error('Error creating booking preview: {}'.format(e))
        else:
            logger.error('Error creating booking preview: {}'.format(e))
            raise


class DeferredInvoicingView(TemplateView):
    #template_name = 'mooring/booking/make_booking.html'
    template_name = 'commercialoperator/booking/success.html'
    #template_name = 'commercialoperator/booking/preview.html'

    def post(self, request, *args, **kwargs):

        payment_method = self.request.POST.get('method')
        context = template_context(self.request)
        proposal_id = int(kwargs['proposal_pk'])
        proposal = Proposal.objects.get(id=proposal_id)
        try:
            recipient = proposal.applicant.email
            submitter = proposal.applicant
        except:
            recipient = proposal.submitter.email
            submitter = proposal.submitter

        if isinstance(proposal.org_applicant, Organisation):
            try:
                if proposal.org_applicant.bpay_allowed and payment_method=='bpay':
                    booking_type = Booking.BOOKING_TYPE_INTERNET
                elif proposal.org_applicant.monthly_invoicing_allowed and payment_method=='monthly_invoicing':
                    booking_type = Booking.BOOKING_TYPE_MONTHLY_INVOICING
                #elif proposal.org_applicant.other_allowed and payment_method=='other':
                else:
                    booking_type = Booking.BOOKING_TYPE_RECEPTION

                booking = create_booking(request, proposal, booking_type=booking_type)
                invoice_reference = None
                if booking and payment_method=='bpay':
                    # BPAY/OTHER invoice are created immediately. Monthly invoices are created later by Cron
                    ret = create_bpay_invoice(submitter, booking)
                    invoice_reference = booking.invoice.reference

                if booking and payment_method=='other':
                    # BPAY/Other invoice are created immediately. Monthly invoices are created later by Cron
                    ret = create_other_invoice(submitter, booking)
                    invoice_reference = booking.invoice.reference

                logger.info('{} Created Park Bookings with payment method {} for Proposal ID {}'.format('User {} with id {}'.format(proposal.submitter.get_full_name(),proposal.submitter.id), payment_method, proposal.id))
                #send_monthly_invoicing_confirmation_tclass_email_notification(request, booking, invoice, recipients=[recipient])
                context.update({
                    'booking': booking,
                    'booking_id': booking.id,
                    'submitter': submitter,
                    'monthly_invoicing': True if payment_method=='monthly_invoicing' else False,
                    'invoice_reference': invoice_reference
                })
                if payment_method=='other':
                    return HttpResponseRedirect(reverse('payments:invoice-payment') + '?invoice={}'.format(invoice_reference))
                else:
                    return render(request, self.template_name, context)


            except Exception, e:
                logger.error('Error Creating booking: {}'.format(e))
                if booking:
                    booking.delete()
                raise
        else:
            logger.error('Error Creating booking: {}'.format(e))
            raise


class MakePaymentView(TemplateView):
    #template_name = 'mooring/booking/make_booking.html'
    template_name = 'commercialoperator/booking/success.html'

    def post(self, request, *args, **kwargs):

        proposal_id = int(kwargs['proposal_pk'])
        proposal = Proposal.objects.get(id=proposal_id)

        try:
            booking = create_booking(request, proposal, booking_type=Booking.BOOKING_TYPE_TEMPORARY)
            with transaction.atomic():
                set_session_booking(request.session,booking)
                #lines = create_lines(request)
                checkout_response = checkout(
                    request,
                    proposal,
                    #lines,
                    booking.as_line_items,
                    return_url_ns='public_booking_success',
                    return_preload_url_ns='public_booking_success',
                    invoice_text='Payment Invoice',
                )

                logger.info('{} built payment line items {} for Park Bookings and handing over to payment gateway'.format('User {} with id {}'.format(proposal.submitter.get_full_name(),proposal.submitter.id), proposal.id))
                return checkout_response

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
            context = template_context(self.request)
            basket = None
            application_fee = get_session_application_invoice(request.session)
            proposal = application_fee.proposal

            try:
                recipient = proposal.applicant.email
                submitter = proposal.applicant
            except:
                recipient = proposal.submitter.email
                submitter = proposal.submitter

            if self.request.user.is_authenticated():
                basket = Basket.objects.filter(status='Submitted', owner=request.user).order_by('-id')[:1]
            else:
                basket = Basket.objects.filter(status='Submitted', owner=booking.proposal.submitter).order_by('-id')[:1]

            order = Order.objects.get(basket=basket[0])
            invoice = Invoice.objects.get(order_number=order.number)
            invoice_ref = invoice.reference
            fee_inv, created = ApplicationFeeInvoice.objects.get_or_create(application_fee=application_fee, invoice_reference=invoice_ref)

            if application_fee.payment_type == ApplicationFee.PAYMENT_TYPE_TEMPORARY:
                try:
                    inv = Invoice.objects.get(reference=invoice_ref)
                    order = Order.objects.get(number=inv.order_number)
                    order.user = submitter
                    order.save()
                except Invoice.DoesNotExist:
                    logger.error('{} tried paying an application fee with an incorrect invoice'.format('User {} with id {}'.format(proposal.submitter.get_full_name(), proposal.submitter.id) if proposal.submitter else 'An anonymous user'))
                    return redirect('external-proposal-detail', args=(proposal.id,))
                if inv.system not in ['0557']:
                    logger.error('{} tried paying an application fee with an invoice from another system with reference number {}'.format('User {} with id {}'.format(proposal.submitter.get_full_name(), proposal.submitter.id) if proposal.submitter else 'An anonymous user',inv.reference))
                    return redirect('external-proposal-detail', args=(proposal.id,))

                if fee_inv:
                    #application_fee.payment_type = 1  # internet booking
                    application_fee.payment_type = ApplicationFee.PAYMENT_TYPE_INTERNET
                    application_fee.expiry_time = None
                    update_payments(invoice_ref)

                    proposal = proposal_submit(proposal, request)
                    if proposal and (invoice.payment_status == 'paid' or invoice.payment_status == 'over_paid'):
                        proposal.fee_invoice_reference = invoice_ref
                        proposal.save()
                    else:
                        logger.error('Invoice payment status is {}'.format(invoice.payment_status))
                        raise

                    application_fee.save()
                    request.session['cols_last_app_invoice'] = application_fee.id
                    delete_session_application_invoice(request.session)

                    send_application_fee_invoice_tclass_email_notification(request, proposal, invoice, recipients=[recipient])
                    send_application_fee_confirmation_tclass_email_notification(request, application_fee, invoice, recipients=[recipient])

                    context = {
                        'proposal': proposal,
                        'submitter': submitter,
                        'fee_invoice': invoice
                    }
                    return render(request, self.template_name, context)

        except Exception as e:
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
                    invoice = afi[0]
            else:
                return redirect('home')

        context = {
            'proposal': proposal,
            'submitter': submitter,
            'fee_invoice': invoice
        }
        return render(request, self.template_name, context)

class BookingSuccessView(TemplateView):
    template_name = 'commercialoperator/booking/success.html'

    def get(self, request, *args, **kwargs):
        print (" BOOKING SUCCESS ")

        booking = None
        submitter = None
        invoice = None
        try:
            context = template_context(self.request)
            basket = None
            booking = get_session_booking(request.session)
            proposal = booking.proposal

            try:
                recipient = proposal.applicant.email
                submitter = proposal.applicant
            except:
                recipient = proposal.submitter.email
                submitter = proposal.submitter

            if self.request.user.is_authenticated():
                basket = Basket.objects.filter(status='Submitted', owner=request.user).order_by('-id')[:1]
            else:
                basket = Basket.objects.filter(status='Submitted', owner=booking.proposal.submitter).order_by('-id')[:1]

            order = Order.objects.get(basket=basket[0])
            invoice = Invoice.objects.get(order_number=order.number)
            invoice_ref = invoice.reference
            book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=invoice_ref, payment_method=invoice.payment_method)

            if booking.booking_type == Booking.BOOKING_TYPE_TEMPORARY:
                try:
                    inv = Invoice.objects.get(reference=invoice_ref)
                    #if (inv.payment_method == Invoice.PAYMENT_METHOD_BPAY):
                    #    # will return 1st of the next month + monthly_payment_due_period (days) e.g 20th of next month
                    #    now = timezone.now().date()
                    #    dt = date(now.year, now.month, 1) + relativedelta(months=1)
                    #    inv.settlement_date = calc_payment_due_date(booking, dt) - relativedelta(days=1)
                    #    inv.save()

                    order = Order.objects.get(number=inv.order_number)
                    order.user = submitter
                    order.save()
                except Invoice.DoesNotExist:
                    logger.error('{} tried paying an admission fee with an incorrect invoice'.format('User {} with id {}'.format(proposal.submitter.get_full_name(), proposal.submitter.id) if proposal.submitter else 'An anonymous user'))
                    return redirect('external-proposal-detail', args=(proposal.id,))
                if inv.system not in ['0557']:
                    logger.error('{} tried paying an admission fee with an invoice from another system with reference number {}'.format('User {} with id {}'.format(proposal.submitter.get_full_name(), proposal.submitter.id) if proposal.submitter else 'An anonymous user',inv.reference))
                    return redirect('external-proposal-detail', args=(proposal.id,))

                if book_inv:
                    booking.booking_type = Booking.BOOKING_TYPE_INTERNET
                    booking.expiry_time = None
                    #booking.set_admission_number()
                    update_payments(invoice_ref)

                    if not (invoice.payment_status == 'paid' or invoice.payment_status == 'over_paid') and invoice.payment_method == Invoice.PAYMENT_METHOD_CC:
                        logger.error('Payment Method={} - Admission Fee Invoice payment status is {}'.format(invoice.get_payment_method_display(), invoice.payment_status))
                        raise

                    booking.save()
                    request.session['cols_last_booking'] = booking.id
                    delete_session_booking(request.session)

                    send_invoice_tclass_email_notification(request, booking, invoice, recipients=[recipient])
                    send_confirmation_tclass_email_notification(request, booking, invoice, recipients=[recipient])

                    context.update({
                        'booking_id': booking.id,
                        'submitter': submitter,
                        'invoice_reference': invoice.reference
                    })
                    return render(request, self.template_name, context)

        except Exception as e:
            #logger.error('{}'.format(e))
            if ('cols_last_booking' in request.session) and Booking.objects.filter(id=request.session['cols_last_booking']).exists():
                booking = Booking.objects.get(id=request.session['cols_last_booking'])
                proposal = booking.proposal

                try:
                    recipient = proposal.applicant.email
                    submitter = proposal.applicant
                except:
                    recipient = proposal.submitter.email
                    submitter = proposal.submitter

                if BookingInvoice.objects.filter(booking=booking).count() > 0:
                    bi = BookingInvoice.objects.filter(booking=booking)
                    invoice = bi[0]
            else:
                return redirect('home')

        context.update({
            'booking_id': booking.id,
            'submitter': submitter,
            'invoice_reference': invoice.invoice_reference
        })
        return render(request, self.template_name, context)


class InvoicePDFView(InvoiceOwnerMixin,View):
    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        bi=BookingInvoice.objects.filter(invoice_reference=invoice.reference).last()
        if bi:
            proposal = bi.booking.proposal
        else:
            proposal = Proposal.objects.get(fee_invoice_reference=invoice.reference)

        response = HttpResponse(content_type='application/pdf')
        response.write(create_invoice_pdf_bytes('invoice.pdf', invoice, proposal))
        return response

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice


class ConfirmationPDFView(InvoiceOwnerMixin,View):
    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        bi=BookingInvoice.objects.filter(invoice_reference=invoice.reference).last()

        # GST ignored here because GST amount is not included on the confirmation PDF
        response = HttpResponse(content_type='application/pdf')
        response.write(create_confirmation_pdf_bytes('confirmation.pdf',invoice, bi.booking))
        return response

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice


class MonthlyConfirmationPDFView(View):
    def get(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, id=self.kwargs['id'])

        response = HttpResponse(content_type='application/pdf')
        response.write(create_monthly_confirmation_pdf_bytes('monthly_confirmation.pdf', booking))
        return response

