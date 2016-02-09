from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'rollcall.views.home'),
    url(r'^email-sent/', 'rollcall.views.validation_sent'),
    url(r'^login/$', 'rollcall.views.home'),
    url(r'^logout/$', 'rollcall.views.logout'),
    url(r'^done/$', 'rollcall.views.done', name='done'),
    url(r'^email/$', 'rollcall.views.require_email', name='require_email'),
)
