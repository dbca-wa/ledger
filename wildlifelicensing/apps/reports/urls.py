from django.conf.urls import url

from wildlifelicensing.apps.reports.views import ReportsView, ApplicationsReportView, LicencesReportView, \
    ReturnsReportView

urlpatterns = [
    url('^$', ReportsView.as_view(), name='reports'),
    url('applications_report/$', ApplicationsReportView.as_view(), name='applications_report'),
    url('licences_report/$', LicencesReportView.as_view(), name='licences_report'),
    url('returns_report/$', ReturnsReportView.as_view(), name='returns_report')
    # for payment reports see main.urls
]
