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
from ledger.payments.models import Invoice
from ledger.payments.mixins import InvoiceOwnerMixin
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
