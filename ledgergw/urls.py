from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from ledgergw.admin import admin
from ledgergw import api
from ledgergw import views
from ledger.accounts.views import logout
from ledger.urls import urlpatterns as ledger_patterns

# URL Patterns
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^ledgergw/remote/user/(?P<ledgeremail>.+)/(?P<apikey>.+)/', api.user_info),
    url(r'^ledgergw/remote/user-groups/(?P<ledger_id>[0-9]+)/(?P<apikey>.+)/', api.user_group_info),
    url(r'^ledgergw/remote/userid/(?P<userid>[0-9]+)/(?P<apikey>.+)/', api.user_info_id),
    url(r'^ledgergw/remote/user-search/(?P<apikey>.+)/', api.user_info_search),
    url(r'^ledgergw/remote/groups/(?P<apikey>.+)/', api.group_info),
    url(r'^ledgergw/remote/documents/update/(?P<apikey>.+)/', api.add_update_file_emailuser),
    url(r'^ledgergw/remote/documents/get/(?P<apikey>.+)/', api.get_private_document),
    url(r'^ledgergw/remote/create-basket-session/(?P<apikey>.+)/', api.create_basket_session),
    url(r'^ledgergw/remote/create-checkout-session/(?P<apikey>.+)/', api.create_checkout_session),
    url(r'^ledgergw/remote/get-invoice/(?P<apikey>.+)/', api.get_invoice_properties),
    url(r'^ledgergw/remote/get-basket-total/(?P<apikey>.+)/', api.get_basket_total),
    url(r'^ledgergw/remote/get_order_info/(?P<apikey>.+)/', api.get_order_info),
    url(r'^ledgergw/remote/delete-card-token/(?P<apikey>.+)/', api.delete_card_token),
    url(r'^ledgergw/remote/get-card-tokens/(?P<apikey>.+)/', api.get_card_tokens_for_user),
    url(r'^ledgergw/remote/process_refund/(?P<apikey>.+)/', api.process_refund),
    url(r'^ledgergw/remote/process_zero/(?P<apikey>.+)/', api.process_zero),
    url(r'^ledgergw/remote/process-api-refund/(?P<apikey>.+)/', api.process_api_refund),
    url(r'^ledgergw/ip-check/', api.ip_check),
    url(r'^reports/$', views.ReportsView.as_view(), name='reports'),
    url(r'^logout/$', logout, name='logout' ),
] + ledger_patterns 


if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
