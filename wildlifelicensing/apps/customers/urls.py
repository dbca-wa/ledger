from django.conf.urls import url

from views import DashboardView

urlpatterns = [
    url('^dashboard/', DashboardView.as_view(), name='dashboard'),
]
