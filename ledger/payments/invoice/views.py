from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.conf import settings
from oscar.core.loading import (
    get_class)
from oscar.views.generic import PostActionMixin
from ledger.payments.invoice.models import Invoice
from ledger.payments.invoice.forms import InvoiceSearchForm

PageTitleMixin = get_class(
    'customer.mixins','PageTitleMixin'
)

class InvoiceHistoryView(PageTitleMixin, generic.ListView):
    """
    Customer invoice history
    """
    context_object_name = "invoices"
    template_name = 'dpaw_payments/invoice/invoice_hist_list.html'
    paginate_by = settings.OSCAR_ORDERS_PER_PAGE
    model = Invoice
    form_class = InvoiceSearchForm
    page_title = _('Invoice History')
    active_tab = 'invoices'

    def get(self, request, *args, **kwargs):
        
        return super(InvoiceHistoryView, self).get(request, *args, **kwargs)
