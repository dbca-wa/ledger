import json
from datetime import date
from django.views import generic
from django.shortcuts import render
from django.shortcuts import get_object_or_404
#
from models import Invoice

class InvoiceDetailView(generic.DetailView):
    model = Invoice
    template_name = 'dpaw_payments/invoice/invoice.html'
    context_object_name = 'invoice'

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice

class PaymentErrorView(generic.TemplateView):
    template_name = 'dpaw_payments/payment_error.html'

class InvoiceSearchView(generic.TemplateView):

    template_name = 'dpaw_payments/invoice/invoice_search.html'

class InvoicePaymentView(generic.DetailView):
    template_name = 'dpaw_payments/invoice/payment.html'
    num_years = 10
    context_object_name = 'invoice'

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice

    def month_choices(self):
        return ["%.2d" %x for x in range(1,13)]

    def year_choices(self):
        return [x for x in range(
            date.today().year,
            date.today().year + self.num_years
        )]

    def get_context_data(self, **kwargs):
        ctx = super(InvoicePaymentView, self).get_context_data(**kwargs)
        ctx['months'] = self.month_choices
        ctx['years'] = self.year_choices
        if self.request.GET.get('amountProvided') == 'true':
            ctx['amountProvided'] = True

        return ctx