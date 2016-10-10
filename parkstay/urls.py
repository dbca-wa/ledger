from django.conf.urls import url, include
from rest_framework import routers
from parkstay import views
from parkstay.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^campsites/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^campsite_classes/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^ical/campground/(?P<ground_id>[0-9]+)/$', views.CampgroundFeed(), name='campground_calendar'),
    url(r'^api/campsites/$', views.get_campsite_bookings, name='get_campsite_bookings'),
    url(r'^api/campsite_classes/$', views.get_campsite_class_bookings, name='get_campsite_class_bookings') 

] + ledger_patterns

