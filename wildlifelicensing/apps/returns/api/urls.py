from django.conf.urls import url, include

from wildlifelicensing.apps.returns.api import views

urlpatterns = [
    url(r'data/(?P<return_type_pk>[0-9])/(?P<resource_number>[0-9]?)/?', views.ReturnsData.as_view(),
        name='data'),
    url(r'/?', views.ReturnListView.as_view(), name='home')
]
