from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^verification/(?P<token>[^/]+)/$', views.VerificationView.as_view(), name='verification'),
]
