from django.conf.urls import url

from wildlifelicensing.apps.returns.api import views

urlpatterns = [
    url(r'data/(?P<return_type_pk>[0-9]+)/(?P<resource_number>[0-9]+)/?', views.ReturnsDataView.as_view(),
        name='data'),
    url(r'', views.ExplorerView.as_view(), name='explorer')
]
