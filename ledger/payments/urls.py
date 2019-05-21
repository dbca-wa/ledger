from django.urls import path, re_path, include
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
                RegionViewSet
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
    path('api/bpoint/payment', BpointPaymentCreateView.as_view(), name='bpoint-payment'),
    path('api/report', ReportCreateView.as_view(),name='ledger-report'),
    path('api/', include(router.urls)),
]

urlpatterns = [
    path('checkout/dashboard/payments/bpay/', bpay.urls),
    path('checkout/dashboard/payments/invoices/', invoice_dash.urls),
    path('checkout/dashboard/payments/', bpoint_dash.urls),
    path('payments/', include(api_patterns)),
    re_path(r'payments/invoice/(?P<reference>\d+)',views.InvoiceDetailView.as_view(), name='invoice-detail'),
    re_path(r'payments/invoice-pdf/(?P<reference>\d+)',views.InvoicePDFView.as_view(), name='invoice-pdf'),
    path('payments/invoice/payment',views.InvoicePaymentView.as_view(), name='invoice-payment'),
    path('payments/invoice/search',views.InvoiceSearchView.as_view(), name='invoice-search'),
    path('payments/error',views.PaymentErrorView.as_view(), name='payments-error'),
]
