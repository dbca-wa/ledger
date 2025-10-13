from __future__ import unicode_literals
from django.urls import path, re_path
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application

from . import views

class BpayApplication(Application):
    name = None
    list_view = views.CollectionView
    detail_view = views.TransactionDetailView
    app_name = 'ledger.payments.bpay.dashboard.app'
    def get_urls(self):
        url_patterns = [
            re_path(r'^collections/$', self.list_view.as_view(), name='bpay-collection-list'),
            # re_path(r'^collections/(?P<date>[^/.]+)$', self.detail_view.as_view(), name='bpay-detail')
        ]
        return self.post_process_urls(url_patterns)
    
    def get_url_decorator(self, url_name):
        return staff_member_required
    
application = BpayApplication()

    
