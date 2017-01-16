from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application

from . import views

class BPOINTApplicationDash(Application):
    name = None
    list_view = views.BPOINTListView
    detail_view = views.BPOINTDetailView
    
    def get_urls(self):
        url_patterns = [
            url(r'^bpoint/transactions$', self.list_view.as_view(), name='bpoint-dash-list'),
            url(r'^bpoint/transaction/(?P<txn_number>\d+)/$', self.detail_view.as_view(), name='bpoint-dash-detail'),
        ]
        return self.post_process_urls(url_patterns)
    
    def get_url_decorator(self, url_name):
        return staff_member_required
    
application = BPOINTApplicationDash()
    
