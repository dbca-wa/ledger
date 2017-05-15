from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from disturbance import views, api
from disturbance.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

# API patterns
router = routers.DefaultRouter()
#router.register(r'maxStayReasons',api.MaximumStayReasonViewSet)

api_patterns = [
    url(r'api/',include(router.urls))
]

# URL Patterns
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include(api_patterns)),
    url(r'^$', views.DisturbanceRoutingView.as_view(), name='ds_home'),
    url(r'^dashboard/$', views.DashboardView.as_view(), name='dash'),
] + ledger_patterns

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
