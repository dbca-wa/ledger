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
                ReportCreateAllocatedView,
                LedgerPayments,
                CheckOracleCodeView,
                RefundOracleView,
                FailedTransactions,
                FailedTransactionCompleted,
                PaymentTotals
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
    url(r'api/ledger/payments-info$', LedgerPayments, name='ledger-payment-information'),
    url(r'api/ledger/oracle-codes-lookup$', CheckOracleCodeView, name='ledger-oracle-codes'),
    url(r'api/ledger/oracle-payment-transfer$', RefundOracleView, name='ledger-oracle-refunds'),
    url(r'api/ledger/failed-transactions$', FailedTransactions, name='failed-transactions'),
    url(r'api/ledger/payment-totals$', PaymentTotals, name='payment-totals'),
    url(r'api/ledger/failed-transaction-complete/(?P<rfid>\d+)/$', FailedTransactionCompleted, name='failed-transaction-completed'),
    url(r'api/report-allocated$', ReportCreateAllocatedView.as_view(),name='ledger-report-allocated'),
    url(r'api/report$', ReportCreateView.as_view(),name='ledger-report'),
    url(r'api/', include(router.urls)),
]

urlpatterns = [
    url(r'checkout/dashboard/payments/bpay/', include(bpay.urls)),
    url(r'checkout/dashboard/payments/invoices/', include(invoice_dash.urls)),
    url(r'checkout/dashboard/payments/', include(bpoint_dash.urls)),
    url(r'checkout/checkout/payment-refund/', views.RefundPaymentView.as_view(),name='ledger-payment-refund'), 
    url(r'checkout/checkout/payment-zero/', views.ZeroPaymentView.as_view(), name='ledger-payment-refund'),
    url(r'checkout/checkout/payment-no/',views.NoPaymentView.as_view(), name='ledger-payment-no'),
    url(r'payments/', include(api_patterns)),
    url(r'payments/invoice/(?P<reference>\d+)',views.InvoiceDetailView.as_view(), name='invoice-detail'),
    url(r'payments/invoice-pdf/(?P<reference>\d+)',views.InvoicePDFView.as_view(), name='invoice-pdf'),
    #url(r'payments/invoice/payment/(?P<reference>\d+)',views.InvoicePaymentView.as_view(), name='invoice-payment'),
    url(r'payments/invoice/payment$',views.InvoicePaymentView.as_view(), name='invoice-payment'),
    url(r'payments/invoice/search$',views.InvoiceSearchView.as_view(), name='invoice-search'),
    url(r'payments/oracle/payments/linked-invoice-issues/(?P<linked_invoice_group_id>\d+)/$', views.LinkedInvoiceIssue.as_view(), name='linked-invoice-issues'),
    url(r'payments/oracle/payments/linked-payment-issues/(?P<linked_invoice_group_id>\d+)/$', views.LinkedPaymentIssue.as_view(), name='linked-payment-issues'),
    url(r'payments/oracle/payments$', views.OraclePayments.as_view(), name='oracle-payments'),
    
    url(r'payments/error$',views.PaymentErrorView.as_view(), name='payments-error'),
    url(r'payments/oracle/failed-transactions$', views.FailedTransaction.as_view(), name='failed-transactions'),
    url(r'payments/oracle/payment-totals$', views.PaymentTotals.as_view(), name='failed-transactions')
]
