from __future__ import unicode_literals
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from django import http
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from ledger.payments.bpoint.models import *


class BPOINTListView(generic.ListView):
    model = BpointTransaction
    template_name = 'dpaw_payments/bpoint/bpoint_list.html'
    context_object_name = 'txns'

class BPOINTDetailView(generic.DetailView):
    model = BpointTransaction
    template_name = 'dpaw_payments/bpoint/bpoint_detail.html'
    context_object_name = 'txn'
    
    def get_object(self):
        return self.model.objects.get(txn_number=self.kwargs['txn_number'])
    
    def get_context_data(self, **kwargs):
        ctx = super(BPOINTDetailView, self).get_context_data(**kwargs)
        # Add more context here
        return ctx
    

