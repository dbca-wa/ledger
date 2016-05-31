from django.conf.urls import url

from views import EnterReturnView, CurateReturnView


urlpatterns = [
    url('^enter-return/([0-9]+)/$', EnterReturnView.as_view(), name='enter_return'),
    url('^curate-return/([0-9]+)/$', CurateReturnView.as_view(), name='curate_return'),
]
