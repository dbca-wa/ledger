from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^validation-sent/$', views.ValidationSentView.as_view(), name='validation_sent'),

    url(r'^verification/(?P<token>[^/]+)/$', views.VerificationView.as_view(), name='verification'),

    url(r'create/?$', views.CustomerCreateView.as_view(), name='customer_create'),

]
