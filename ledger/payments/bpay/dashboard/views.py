from __future__ import unicode_literals
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.conf import settings
from django import http
from django.utils.translation import ugettext as _

from ledger.payments.bpay.models import *

class TransactionListView(generic.ListView):
    model = BpayTransaction
    template_name = 'dpaw_payments/bpay/transactions_list.html'
    context_object_name = 'transactions'

class TransactionDetailView(generic.DetailView):
    model = BpayCollection
    template_name = 'dpaw_payments/bpay/transaction_detail.html'
    context_object_name = 'collection'
    pk_url_kwarg = 'date'
    
class CollectionView(generic.ListView):
    model = BpayCollection
    template_name = 'dpaw_payments/bpay/collections.html'
    context_object_name = 'collections'
