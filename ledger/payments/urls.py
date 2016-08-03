from django.conf.urls import url, include
from rest_framework import routers
from api import BpayTransactionViewSet, BpayCollectionViewSet, InvoiceTransactionViewSet, BpointTransactionViewSet, BpointPaymentCreateView, CashViewSet, BpayFileList, ReportCreateView

from bpay.dashboard.app import application as bpay
from invoice.dashboard.app import application as invoice_dash
from bpoint.dashboard.app import application as bpoint_dash
from invoice.views import InvoiceHistoryView
import views
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
    url(r'api/report$', ReportCreateView.as_view(),name='ledger-report'),
    url(r'api/', include(router.urls)),
]

urlpatterns = [
    url(r'checkout/dashboard/payments/bpay/', include(bpay.urls)),
    url(r'checkout/dashboard/payments/invoices/', include(invoice_dash.urls)),
    url(r'checkout/dashboard/payments/', include(bpoint_dash.urls)),
    url(r'payments/', include(api_patterns)),
    url(r'payments/invoice/(?P<reference>\d+)',views.InvoiceDetailView.as_view(), name='invoice-detail'),
    url(r'payments/invoice/payment/(?P<reference>\d+)',views.InvoicePaymentView.as_view(), name='invoice-payment'),
    url(r'payments/invoice/search$',views.InvoiceSearchView.as_view(), name='invoice-search'),
    url(r'payments/error$',views.PaymentErrorView.as_view(), name='payments-error'),
]