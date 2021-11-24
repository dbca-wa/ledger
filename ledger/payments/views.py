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
from ledger.payments import helpers
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
        if helpers.is_payment_admin(self.request.user) is True:
            invoice_group_id = self.request.GET.get('invoice_group_id','');
            invoice_no = self.request.GET.get('invoice_no','')
            booking_reference = self.request.GET.get('booking_reference','')
   #&cur    rent_invoice_no="+ledger_payments.var.current_invoice_no+"&current_booking_reference="+ledger_payments.var.current_booking_reference,
              
            ctx['invoice_group_id'] = invoice_group_id
            ctx['invoice_no'] = invoice_no
            ctx['booking_reference'] = booking_reference
            ctx['oracle_code_refund_allocation_pool'] =  settings.UNALLOCATED_ORACLE_CODE
            #self.get_booking_history(invoice_group_id)
        else:
            self.template_name = 'dpaw_payments/forbidden.html'
        return ctx


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

    def get(self, request, *args, **kwargs):
         basket = None
         basket_hash = request.COOKIES.get('ledgergw_basket','')
         basket_hash_split = basket_hash.split("|")
         basket = basket_models.Basket.objects.get(id=basket_hash_split[0])
         return render(request, self.template_name, {'basket': basket})

class ZeroPaymentView(generic.TemplateView):
    template_name = 'checkout/zero_payment_api_wrapper.html'

    def get(self, request, *args, **kwargs):
         basket = None
         basket_hash = request.COOKIES.get('ledgergw_basket','')
         basket_hash_split = basket_hash.split("|")
         basket = basket_models.Basket.objects.get(id=basket_hash_split[0])
         return render(request, self.template_name, {'basket': basket})

class FailedTransaction(generic.TemplateView):
    template_name = 'dpaw_payments/failed_transaction.html'

    def get_context_data(self, **kwargs):
        ctx = super(FailedTransaction,self).get_context_data(**kwargs)
        if helpers.is_payment_admin(self.request.user) is True:
            system_id = self.request.GET.get('system_id','')
            ctx['oracle_systems'] = payments_models.OracleInterfaceSystem.objects.all()
            ctx['system_id'] = system_id
        else:
            self.template_name = 'dpaw_payments/forbidden.html'
        return ctx


