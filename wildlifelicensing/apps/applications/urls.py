from django.conf.urls import url

from views import ApplicationView

urlpatterns = [
    url('^application/([\w-]+)/$', ApplicationView.as_view(), name='application'),
]