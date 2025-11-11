# from django.conf.urls import url
from django.urls import path, re_path, include
from django.contrib.auth.decorators import login_required

from oscar.core.application import Application
from oscar.core.loading import get_class


class BasketApplication(Application):
    name = 'basket'
    summary_view = get_class('basket.views', 'BasketView')
    saved_view = get_class('basket.views', 'SavedView')
    add_view = get_class('basket.views', 'BasketAddView')
    add_voucher_view = get_class('basket.views', 'VoucherAddView')
    remove_voucher_view = get_class('basket.views', 'VoucherRemoveView')

    def get_urls(self):
        urls = [
            re_path(r'^$', self.summary_view.as_view(), name='summary'),
            re_path(r'^add/(?P<pk>\d+)/$', self.add_view.as_view(), name='add'),
            re_path(r'^vouchers/add/$', self.add_voucher_view.as_view(),
                name='vouchers-add'),
            re_path(r'^vouchers/(?P<pk>\d+)/remove/$',
                self.remove_voucher_view.as_view(), name='vouchers-remove'),
            re_path(r'^saved/$', login_required(self.saved_view.as_view()),
                name='saved'),
        ]
        return self.post_process_urls(urls)


application = BasketApplication()
