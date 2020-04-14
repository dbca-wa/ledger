from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from ledgergw.admin import admin
from ledgergw import api
from ledger.urls import urlpatterns as ledger_patterns

# URL Patterns
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^ledgergw/remote/user/(?P<ledgeremail>.+)/', api.user_info), 
] + ledger_patterns 


if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
