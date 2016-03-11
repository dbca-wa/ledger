from django.conf.urls import url

from views import ApplicationView, ApplicationPreviewView

urlpatterns = [
    url('^application/([\w-]+)/$', ApplicationView.as_view(), name='application'),
    url('^application_preview/([\w-]+)/$', ApplicationPreviewView.as_view(), name='application_preview'),
]