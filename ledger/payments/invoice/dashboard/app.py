from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application

from . import views

class InvoiceApplication(Application):
    name = None
    list_view = views.InvoiceListView
    detail_view = views.InvoiceDetailView
    
    def get_urls(self):
        url_patterns = [
            url(r'^invoices/$', self.list_view.as_view(), name='invoices-list'),
            url(r'^invoice/(?P<order>\d+)/$', self.detail_view.as_view(), name='invoices-detail'),
        ]
        return self.post_process_urls(url_patterns)
    
    def get_url_decorator(self, url_name):
        return staff_member_required
    
application = InvoiceApplication()
    
