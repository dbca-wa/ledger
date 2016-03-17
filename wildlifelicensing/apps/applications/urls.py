from django.conf.urls import url

from views import ApplicationsView, ApplicationView, ApplicationPreviewView, ApplicantsView

urlpatterns = [
    url('^applications/$', ApplicationsView.as_view(), name='applications'),
    url('^application/([\w-]+)/$', ApplicationView.as_view(), name='application'),
    url('^application_preview/([\w-]+)/$', ApplicationPreviewView.as_view(), name='application_preview'),
    url('^applicants/$', ApplicantsView.as_view(), name='applicants'),
    url('^applicants/([0-9]+)/$', ApplicantsView.as_view(), name='applicants'),
]
