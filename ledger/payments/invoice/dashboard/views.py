from __future__ import unicode_literals
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from django import http
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from ledger.payments.invoice.models import *


class InvoiceListView(generic.ListView):
    model = Invoice
    template_name = 'dpaw_payments/invoice/invoice_list.html'
    context_object_name = 'invoices'

class InvoiceDetailView(generic.DetailView):
    model = Invoice
    template_name = 'dpaw_payments/invoice/invoice.html'
    context_object_name = 'invoice'

    def get_object(self):
        order = get_object_or_404(Order, number=self.kwargs['order'])
        return self.model.objects.get(order_number=order.number)

    def get_context_data(self, **kwargs):
        ctx = super(InvoiceDetailView, self).get_context_data(**kwargs)
        ctx['bpay_allowed'] = settings.BPAY_ALLOWED
        ctx['invoice_unpaid_warning'] = settings.INVOICE_UNPAID_WARNING
        return ctx


