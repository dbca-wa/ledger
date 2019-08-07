from django.conf.urls import url, include
from rest_framework import routers
from ledger.payments.api import (
                BpayTransactionViewSet,
                BpayCollectionViewSet,
                InvoiceTransactionViewSet,
                BpointTransactionViewSet,
                BpointPaymentCreateView,
                CashViewSet,
                BpayFileList,
                ReportCreateView,
                RegionViewSet,
                ReportCreateAllocatedView
                )

from ledger.payments.bpay.dashboard.app import application as bpay
from ledger.payments.invoice.dashboard.app import application as invoice_dash
from ledger.payments.bpoint.dashboard.app import application as bpoint_dash
from ledger.payments.invoice.views import InvoiceHistoryView
from ledger.payments import views
# api patterns
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'^bpay/files', BpayFileList)
router.register(r'^bpay/transactions', BpayTransactionViewSet)
router.register(r'^bpay/collections',BpayCollectionViewSet,base_name='BpayCollection')
router.register(r'^invoices', InvoiceTransactionViewSet)
router.register(r'^bpoint', BpointTransactionViewSet)
router.register(r'^cash', CashViewSet)
router.register(r'^regions', RegionViewSet)

api_patterns = [
    url(r'api/bpoint/payment$', BpointPaymentCreateView.as_view(), name='bpoint-payment'),
    url(r'api/report-allocated$', ReportCreateAllocatedView.as_view(),name='ledger-report-allocated'),
    url(r'api/report$', ReportCreateView.as_view(),name='ledger-report'),
    url(r'api/', include(router.urls)),
]

urlpatterns = [
    url(r'checkout/dashboard/payments/bpay/', include(bpay.urls)),
    url(r'checkout/dashboard/payments/invoices/', include(invoice_dash.urls)),
    url(r'checkout/dashboard/payments/', include(bpoint_dash.urls)),
    url(r'payments/', include(api_patterns)),
    url(r'payments/invoice/(?P<reference>\d+)',views.InvoiceDetailView.as_view(), name='invoice-detail'),
    url(r'payments/invoice-pdf/(?P<reference>\d+)',views.InvoicePDFView.as_view(), name='invoice-pdf'),
    #url(r'payments/invoice/payment/(?P<reference>\d+)',views.InvoicePaymentView.as_view(), name='invoice-payment'),
    url(r'payments/invoice/payment$',views.InvoicePaymentView.as_view(), name='invoice-payment'),
    url(r'payments/invoice/search$',views.InvoiceSearchView.as_view(), name='invoice-search'),
    url(r'payments/error$',views.PaymentErrorView.as_view(), name='payments-error'),
]
