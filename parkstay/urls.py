from django.conf.urls import url, include
from rest_framework import routers
from parkstay import views
from parkstay.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
] + ledger_patterns

