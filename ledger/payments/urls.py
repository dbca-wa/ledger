
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
                RegionViewSet,
                ReportCreateAllocatedView,
                LedgerPayments,
                CheckOracleCodeView,
                RefundOracleView,
                FailedTransactions,
                FailedTransactionCompleted,
                PaymentTotals,
                UnpaidInvoices,
                CancelInvoice
                )

from ledger.payments.bpay.dashboard.app import application as bpay
from ledger.payments.invoice.dashboard.app import application as invoice_dash
from ledger.payments.bpoint.dashboard.app import application as bpoint_dash
from ledger.payments.invoice.views import InvoiceHistoryView
from ledger.payments import views

app_name = 'ledger.payments'
# api patterns
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'^bpay/files', BpayFileList)
router.register(r'^bpay/transactions', BpayTransactionViewSet)
router.register(r'^bpay/collections',BpayCollectionViewSet,basename='BpayCollection')
router.register(r'^invoices', InvoiceTransactionViewSet)
router.register(r'^bpoint', BpointTransactionViewSet)
router.register(r'^cash', CashViewSet)
router.register(r'^regions', RegionViewSet)

api_patterns = [
    re_path(r'api/bpoint/payment$', BpointPaymentCreateView.as_view(), name='bpoint-payment'),
    re_path(r'api/ledger/payments-info$', LedgerPayments, name='ledger-payment-information'),
    re_path(r'api/ledger/oracle-codes-lookup$', CheckOracleCodeView, name='ledger-oracle-codes'),
    re_path(r'api/ledger/oracle-payment-transfer$', RefundOracleView, name='ledger-oracle-refunds'),
    re_path(r'api/ledger/failed-transactions$', FailedTransactions, name='failed-transactions'),
    re_path(r'api/ledger/payment-totals$', PaymentTotals, name='payment-totals'),
    re_path(r'api/ledger/unpaid-invoices$', UnpaidInvoices, name='unpaid-invoices'),
    re_path(r'api/ledger/failed-transaction-complete/(?P<rfid>\d+)/$', FailedTransactionCompleted, name='failed-transaction-completed'),
    re_path(r'api/ledger/cancel-invoice$', CancelInvoice, name='cancel-invoice'),
    re_path(r'api/report-allocated$', ReportCreateAllocatedView.as_view(),name='ledger-report-allocated'),
    re_path(r'api/report$', ReportCreateView.as_view(),name='ledger-report'),
    re_path(r'api/', include(router.urls)),
]

urlpatterns = [
    # re_path(r'checkout/dashboard/payments/bpay/', include(bpay.urls)),
    # re_path(r'checkout/dashboard/payments/invoices/', include(invoice_dash.urls)),
    # re_path(r'checkout/dashboard/payments/', include(bpoint_dash.urls)),
    re_path(r'checkout/checkout/payment-refund/', views.RefundPaymentView.as_view(),name='ledger-payment-refund'), 
    re_path(r'checkout/checkout/payment-zero/', views.ZeroPaymentView.as_view(), name='ledger-payment-refund'),
    re_path(r'checkout/checkout/payment-no/',views.NoPaymentView.as_view(), name='ledger-payment-no'),
    re_path(r'payments/', include(api_patterns)),
    re_path(r'payments/invoice/(?P<reference>\d+)',views.InvoiceDetailView.as_view(), name='invoice-detail'),
    re_path(r'payments/invoice-pdf/(?P<reference>\d+)',views.InvoicePDFView.as_view(), name='invoice-pdf'),
    #re_path(r'payments/invoice/payment/(?P<reference>\d+)',views.InvoicePaymentView.as_view(), name='invoice-payment'),
    re_path(r'payments/invoice/payment$',views.InvoicePaymentView.as_view(), name='invoice-payment'),
    re_path(r'payments/invoice/search$',views.InvoiceSearchView.as_view(), name='invoice-search'),
    re_path(r'payments/oracle/payments/linked-invoice-issues/(?P<linked_invoice_group_id>\d+)/$', views.LinkedInvoiceIssue.as_view(), name='linked-invoice-issues'),
    re_path(r'payments/oracle/payments/linked-payment-issues/(?P<linked_invoice_group_id>\d+)/$', views.LinkedPaymentIssue.as_view(), name='linked-payment-issues'),
    re_path(r'payments/oracle/payments$', views.OraclePayments.as_view(), name='oracle-payments'),
    
    re_path(r'payments/error$',views.PaymentErrorView.as_view(), name='payments-error'),
    re_path(r'payments/oracle/failed-transactions$', views.FailedTransaction.as_view(), name='failed-transactions'),
    re_path(r'payments/oracle/payment-totals$', views.PaymentTotals.as_view(), name='payment-totals'),
    re_path(r'payments/oracle/unpaid-invoices$', views.UnpaidInvoice.as_view(), name='unpaid-invoices')
    
]
