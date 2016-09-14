from django.conf.urls import url, include
from rest_framework import routers
from parkstay import views
from parkstay.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^campsites/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^api/campsites/$', views.get_campsite_bookings, name='get_campsite_bookings') 
] + ledger_patterns

