from django.conf import settings
# from django.conf.urls import url, include
from django.urls import path, re_path, include
from django.conf.urls.static import static
# from rest_framework import routers
from ledgergw.admin import admin
from ledgergw import api
from ledgergw import views
from ledger.accounts.views import logout
from ledger.urls import urlpatterns as ledger_patterns

# URL Patterns
urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^ledgergw/public/api/get-countries',api.get_countries),
    re_path(r'^ledgergw/remote/user/(?P<ledgeremail>.+)/(?P<apikey>.+)/', api.user_info),
    re_path(r'^ledgergw/remote/user-groups/(?P<ledger_id>[0-9]+)/(?P<apikey>.+)/', api.user_group_info),
    re_path(r'^ledgergw/remote/userid/(?P<userid>[0-9]+)/(?P<apikey>.+)/', api.user_info_id),
    re_path(r'^ledgergw/remote/update-userid/(?P<userid>[0-9]+)/(?P<apikey>.+)/', api.update_user_info_id),
    re_path(r'^ledgergw/remote/user-search/(?P<apikey>.+)/', api.user_info_search),
    re_path(r'^ledgergw/remote/groups/(?P<apikey>.+)/', api.group_info),
    re_path(r'^ledgergw/remote/documents/update/(?P<apikey>.+)/', api.add_update_file_emailuser),
    re_path(r'^ledgergw/remote/documents/get/(?P<apikey>.+)/', api.get_private_document),
    re_path(r'^ledgergw/remote/create-basket-session/(?P<apikey>.+)/', api.create_basket_session),
    re_path(r'^ledgergw/remote/create-checkout-session/(?P<apikey>.+)/', api.create_checkout_session),
    re_path(r'^ledgergw/remote/get-invoice/(?P<apikey>.+)/', api.get_invoice_properties),
    re_path(r'^ledgergw/remote/get-basket-for-future-invoice/(?P<apikey>\w+)/(?P<reference>\d+)/', api.get_basket_for_future_invoice),
    re_path(r'^ledgergw/remote/get-basket-total/(?P<apikey>.+)/', api.get_basket_total),
    re_path(r'^ledgergw/remote/get_order_info/(?P<apikey>.+)/', api.get_order_info),
    re_path(r'^ledgergw/remote/get_order_lines/(?P<apikey>.+)/', api.get_order_lines),
    re_path(r'^ledgergw/remote/delete-card-token/(?P<apikey>.+)/', api.delete_card_token),
    re_path(r'^ledgergw/remote/get-card-tokens/(?P<apikey>.+)/', api.get_card_tokens_for_user),
    re_path(r'^ledgergw/remote/check-user-primary-card/(?P<apikey>.+)/', api.get_primary_card_token_for_user),
    re_path(r'^ledgergw/remote/create-store-card-token/(?P<apikey>.+)/', api.create_store_card_token),
    re_path(r'^ledgergw/remote/set-primary-card/(?P<apikey>.+)/', api.set_primary_card),
    re_path(r'^ledgergw/remote/get-primary-card/(?P<apikey>.+)/', api.get_primary_card),
    re_path(r'^ledgergw/remote/process_refund/(?P<apikey>.+)/', api.process_refund),
    re_path(r'^ledgergw/remote/process_zero/(?P<apikey>.+)/', api.process_zero),
    re_path(r'^ledgergw/remote/process_no/(?P<apikey>.+)/', api.process_no),
    re_path(r'^ledgergw/remote/process_create_future_invoice/(?P<apikey>.+)/', api.process_create_future_invoice),
    re_path(r'^ledgergw/remote/process-api-refund/(?P<apikey>.+)/', api.process_api_refund),
    re_path(r'^ledgergw/remote/oracle-interface-system/(?P<apikey>.+)/', api.oracle_interface_system),
    re_path(r'^ledgergw/remote/get_failed_refund_totals/(?P<apikey>.+)/(?P<system_id>\d+)/', api.get_failed_refund_totals),
    re_path(r'^ledgergw/remote/get_organisation/(?P<apikey>.+)/', api.get_organisation),
    re_path(r'^ledgergw/remote/get_all_organisation/(?P<apikey>.+)/', api.get_all_organisation),
    re_path(r'^ledgergw/remote/get_search_organisation/(?P<apikey>.+)/', api.get_search_organisation),
    re_path(r'^ledgergw/remote/create_organisation/(?P<apikey>.+)/', api.create_organisation),
    re_path(r'^ledgergw/remote/update_ledger_oracle_invoice/(?P<apikey>.+)/', api.update_ledger_oracle_invoice),
    re_path(r'^ledgergw/remote/check-oracle-code/(?P<apikey>.+)/', api.check_oracle_code),
    re_path(r'^ledgergw/remote/update_organisation/(?P<apikey>.+)/', api.update_organisation),
    re_path(r'^ledgergw/remote/create_get_emailuser/(?P<apikey>.+)/', api.create_get_emailuser),
    re_path(r'^ledgergw/remote/cancel-invoice/(?P<apikey>.+)/', api.cancel_invoice),
    re_path(r'^ledgergw/remote/change-user-invoice-ownership/(?P<apikey>.+)/', api.change_user_invoice_ownership),    
    re_path(r'^ledgergw/invoice-pdf/(?P<api_key>\w+)/(?P<reference>\d+)',views.InvoicePDFView.as_view(), name='invoice-pdf'),
    re_path(r'^api/reports/refunds$', api.RefundsReportView.as_view(), name='refunds-report'),
    re_path(r'^api/reports/settlements$', api.SettlementReportView.as_view(), name='settlements-report'),     
    re_path(r'^api/reports/itemised-transactions$', api.ItemisedTransactionReportView.as_view(), name='itemised-transaction-report'),
    re_path(r'^api/oracle_job$', api.OracleJob.as_view(), name='get-oracle'),
    re_path(r'^api/queue-report-job$', api.QueuePayemntAuditReportJob, name='queue-report-job'),
    re_path(r'^ledgergw/ip-check/', api.ip_check),
    re_path(r'^reports/$', views.ReportsView.as_view(), name='reports'),   
    re_path(r'^logout/$', logout, name='logout'),
] + ledger_patterns 

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
