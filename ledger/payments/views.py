import json
from datetime import date
from six.moves.urllib import parse as urlparse
from django.views import generic
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import Template, Context, TemplateDoesNotExist
from django.http import HttpResponse
from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger.payments.utils import checkURL
from ledger.payments.cash.models import REGION_CHOICES
#
from oscar.apps.order.models import Order
from ledger.payments.models import Invoice
from ledger.payments.mixins import InvoiceOwnerMixin
from ledger.basket import models as basket_models
from ledger.payments import models as payments_models
#
from confy import env
#

class InvoicePDFView(InvoiceOwnerMixin,generic.View):
    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        response = HttpResponse(content_type='application/pdf')
        response.write(create_invoice_pdf_bytes('invoice.pdf',invoice))
        return response

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice

class InvoiceDetailView(InvoiceOwnerMixin,generic.DetailView):
    model = Invoice
    template_name = 'dpaw_payments/invoice/invoice.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        ctx = super(InvoiceDetailView,self).get_context_data(**kwargs)
        ctx['bpay_allowed'] = settings.BPAY_ALLOWED
        return ctx

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice

class PaymentErrorView(generic.TemplateView):
    template_name = 'dpaw_payments/payment_error.html'

class InvoiceSearchView(generic.TemplateView):

    template_name = 'dpaw_payments/invoice/invoice_search.html'

class OraclePayments(generic.TemplateView):
    template_name = 'dpaw_payments/oracle_payments.html'

    def get_context_data(self, **kwargs):
        ctx = super(OraclePayments,self).get_context_data(**kwargs)
        invoice_group_id = self.request.GET.get('invoice_group_id','');
        invoice_no = self.request.GET.get('invoice_no','')
        booking_reference = self.request.GET.get('booking_reference','')
   #&current_invoice_no="+ledger_payments.var.current_invoice_no+"&current_booking_reference="+ledger_payments.var.current_booking_reference,

        ctx['invoice_group_id'] = invoice_group_id
        ctx['invoice_no'] = invoice_no
        ctx['booking_reference'] = booking_reference
        ctx['oracle_code_refund_allocation_pool'] =  settings.UNALLOCATED_ORACLE_CODE
        self.get_booking_history(invoice_group_id)
        return ctx

    def get_booking_history(self, invoice_group_id):
        print ("get_booking_history")
        return


class InvoicePaymentView(InvoiceOwnerMixin,generic.TemplateView):
    template_name = 'dpaw_payments/invoice/payment.html'
    num_years = 10
    #context_object_name = 'invoice'

    def check_owner(self, user):
        return self.is_payment_admin(user)

    def month_choices(self):
        return ["%.2d" %x for x in range(1,13)]

    def year_choices(self):
        return [x for x in range(
            date.today().year,
            date.today().year + self.num_years
        )]

    def get_context_data(self, **kwargs):
        ctx = super(InvoicePaymentView, self).get_context_data(**kwargs)
        invoices = []
        UPDATE_PAYMENT_ALLOCATION = env('UPDATE_PAYMENT_ALLOCATION', False)
        ctx['payment_allocation'] = UPDATE_PAYMENT_ALLOCATION
        ctx['bpay_allowed'] = settings.BPAY_ALLOWED
        ctx['months'] = self.month_choices
        ctx['years'] = self.year_choices
        ctx['regions'] = list(REGION_CHOICES)

        #invoices = []

        #invoices_obj = Invoice.objects.filter(reference__in=self.request.GET.getlist('invoice')).values('created','text','amount','order_number','reference','system','token','voided','previous_invoice','settlement_date','payment_method').order_by('created')
        #order_numbers = []
        #for i in invoices_obj:
        #    row = {'created': None, 'text': None, 'amount': None, 'order_number': None,'reference': None, 'system': None, 'token' : None, 'voided': None, 'previous_invoice': None,'settlement_date': None, 'payment_method': None, 'order': {}}
        #    row['created'] = i['created']
        #    row['text'] = i['text']
        #    row['amount'] = i['amount']
        #    row['order_number'] = i['order_number']
        #    row['reference'] = i['reference']
        #    row['system'] = i['system']
        #    row['token'] = i['token']
        #    row['voided'] = i['voided']
        #    row['previous_invoice'] =  i['previous_invoice']
        #    row['settlement_date'] = i['settlement_date']
        #    row['payment_method'] = i['payment_method']
        #    #row[''] =
        #    #row[''] =
        #    #row[''] =
        #    #row[''] =
        #    #row[''] =

        #    print (i['order_number'])
        #    #order_numbers.append(i.order_number)
        #    order_obj = Order.objects.filter(number=i['order_number'])

        #    row['order'] = order_obj[0]
        #    invoices.append(row)

        invoices = Invoice.objects.filter(reference__in=self.request.GET.getlist('invoice')).order_by('created')
        ctx['invoices'] = invoices
        if self.request.GET.get('amountProvided') == 'true':
            ctx['amountProvided'] = True
        if self.request.GET.get('redirect_url'):
            try:
                checkURL(self.request.GET.get('redirect_url'))
                ctx['redirect_url'] = self.request.GET.get('redirect_url')
            except:
                pass
        if self.request.GET.get('callback_url'):
            try:
                checkURL(self.request.GET.get('callback_url'))
                domain = urlparse(self.request.GET.get('callback_url')).netloc.split('.')[1]
                if 'dbca.wa.gov.au' == domain or settings.DEBUG:
                    ctx['callback_url'] = self.request.GET.get('callback_url')
            except:
                pass
        if self.request.GET.get('custom_template'):
            try:
                ctx['custom_block'] = get_template(self.request.GET.get('custom_template'))
            except TemplateDoesNotExist as e:
                pass
        return ctx

class RefundPaymentView(generic.TemplateView):
    template_name = 'checkout/refund_payment_api_wrapper.html'

    #def get_booking_info(self, request, *args, **kwargs):

    #    booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
    #    bpoint_id = None
    #    form_context = {
    #    }
    #    form = MakeBookingsForm(form_context)

    #    booking_invoice = BookingInvoice.objects.filter(booking=booking.old_booking)
    #    for bi in booking_invoice:
    #        inv = Invoice.objects.filter(reference=bi.invoice_reference)
    #        for i in inv:
    #            for b in i.bpoint_transactions:
    #               if b.action == 'payment':
    #                  bpoint_id = b.id

    #    return booking,bpoint_id

    def get(self, request, *args, **kwargs):

    #    booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
    #    if request.user.is_staff or request.user.is_superuser or Booking.objects.filter(customer=request.user,pk=booking.id).count() == 1:
         #basket = utils.get_basket(request)
         basket = None
         basket_hash = request.COOKIES.get('ledgergw_basket','')
         basket_hash_split = basket_hash.split("|")
         basket = basket_models.Basket.objects.get(id=basket_hash_split[0])
    #        #basket_total = [sum(Decimal(b.line_price_incl_tax)) for b in basket.all_lines()] 
    #        basket_total = Decimal('0.00')
    #        for b in basket.all_lines():
    #           basket_total = basket_total + b.line_price_incl_tax
    #        booking,bpoint_id = self.get_booking_info(request, *args, **kwargs)

    #        #    return self.render_page(request, booking, form)
         return render(request, self.template_name, {'basket': basket})
    #    else:
    #        return HttpResponseRedirect(reverse('home'))

    #def post(self, request, *args, **kwargs):
    #     print ("POST --> RefundPaymentView ")
         #context_processor = template_context(request)
         #ps_booking = request.session['ps_booking']
         #print (ps_booking)


         #booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
         #if request.user.is_staff or request.user.is_superuser or Booking.objects.filter(customer=request.user,pk=booking.id).count() == 1:

         #    bpoint = None
         #    invoice = None
         #    refund  = None
         #    failed_refund = False
         #    basket = utils.get_basket(request)
         #    booking,bpoint_id = self.get_booking_info(request, *args, **kwargs)
         #    basket_total = Decimal('0.00')
         #    for b in basket.all_lines():
         #        basket_total = basket_total + b.line_price_incl_tax

         #    b_total =  Decimal('{:.2f}'.format(float(basket_total - basket_total - basket_total)))
         #    info = {'amount': Decimal('{:.2f}'.format(float(basket_total - basket_total - basket_total))), 'details' : 'Refund via system'}

         #    try:
         #       bpoint = BpointTransaction.objects.get(id=bpoint_id)
         #       refund = bpoint.refund(info,request.user)
         #       invoice = Invoice.objects.get(reference=bpoint.crn1)
         #       update_payments(invoice.reference)
         #       emails.send_refund_completed_email_customer(booking, context_processor)
         #    except:
         #       failed_refund = True
         #       emails.send_refund_failure_email(booking, context_processor)
         #       emails.send_refund_failure_email_customer(booking, context_processor)
         #       booking_invoice = BookingInvoice.objects.filter(booking=booking.old_booking).order_by('id')
         #       for bi in booking_invoice:
         #           invoice = Invoice.objects.get(reference=bi.invoice_reference)
         #       RefundFailed.objects.create(booking=booking, invoice_reference=invoice.reference, refund_amount=b_total,status=0)
         #    order_response = place_order_submission(request)
         #    new_order = Order.objects.get(basket=basket)
         #    new_invoice = Invoice.objects.get(order_number=new_order.number)
         #    new_invoice.settlement_date = None
         #    new_invoice.save()

#        #     book_inv, created = BookingInvoice.objects.create(booking=booking, invoice_reference=invoice.reference)

         #    BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=new_invoice.reference)
         #    if refund:
         #        invoice.voided = True
         #        invoice.save()
         #        bpoint_refund = BpointTransaction.objects.get(txn_number=refund.txn_number)
         #        bpoint_refund.crn1 = new_invoice.reference
         #        bpoint_refund.save()
         #        update_payments(invoice.reference)
         #    update_payments(new_invoice.reference)


         #    if failed_refund is True:
         #        # Refund Failed Assign Refund amount to allocation pool.
         #        lines = [{'ledger_description':'Refund assigned to unallocated pool',"quantity":1,"price_incl_tax":abs(info['amount']),"oracle_code":settings.UNALLOCATED_ORACLE_CODE, 'line_status': 1}]
         #        utils.allocate_failedrefund_to_unallocated(request, booking, lines, invoice_text=None, internal=False,order_total=abs(info['amount']),user=booking.customer)

         #    return HttpResponseRedirect('/success/')
         #else:
         #    return HttpResponseRedirect(reverse('home'))



class FailedTransaction(generic.TemplateView):
    template_name = 'dpaw_payments/failed_transaction.html'

    def get_context_data(self, **kwargs):
        ctx = super(FailedTransaction,self).get_context_data(**kwargs)
        system_id = self.request.GET.get('system_id','')
        ctx['oracle_systems'] = payments_models.OracleInterfaceSystem.objects.all()
        ctx['system_id'] = system_id
        #self.get_booking_history(invoice_group_id)
        return ctx

    #def get_booking_history(self, invoice_group_id):
   #     print ("get_booking_history")
   #     return


