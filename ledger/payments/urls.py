from django.conf.urls import url, include
from rest_framework import routers
from api import BpayTransactionViewSet, BpayCollectionViewSet, InvoiceTransactionViewSet, BpointTransactionViewSet, BpointPaymentCreateView, CashViewSet, BpayFileList

from bpay.dashboard.app import application as bpay
from invoice.dashboard.app import application as invoice_dash
from bpoint.dashboard.app import application as bpoint_dash
from invoice.views import InvoiceHistoryView

# api patterns
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'^bpay/files', BpayFileList)
router.register(r'^bpay/transactions', BpayTransactionViewSet)
router.register(r'^bpay/collections',BpayCollectionViewSet,base_name='BpayCollection')
router.register(r'^invoices', InvoiceTransactionViewSet)
router.register(r'^bpoint', BpointTransactionViewSet)
router.register(r'^cash', CashViewSet)

api_patterns = [
    url(r'api/bpoint/payment$', BpointPaymentCreateView.as_view(), name='bpoint-payment'),
    url(r'api/', include(router.urls)),
]

urlpatterns = [
    url(r'^dashboard/dpaw_payments/bpay/', include(bpay.urls)),
    url(r'^dashboard/dpaw_payments/invoices/', include(invoice_dash.urls)),
    url(r'^dashboard/dpaw_payments/', include(bpoint_dash.urls)),
    url(r'^dpaw_payments/', include(api_patterns)),
    url(r'^accounts/invoices/',InvoiceHistoryView.as_view(), name='invoice-history-list'),
    url(r'^accounts/invoice/(?P<order>\d+)/$',invoice_dash.detail_view.as_view(), name='invoice-history-detail'),
]