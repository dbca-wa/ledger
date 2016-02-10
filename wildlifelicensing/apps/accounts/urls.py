from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url('^login/', views.LoginView.as_view(), name='login'),
    url('^logout/', auth_views.logout, {'next_page': 'home'}, name='logout'),

    url(r'create/?$', views.UserCreateView.as_view(), name='user_create'),

    url(r'^password_reset/done/$',
        auth_views.password_reset_done,
        {'template_name': 'password_reset_done.html'},
        name='password_reset_done'),

    url(r'^password_reset/$',
        auth_views.password_reset,
        {'template_name': 'password_reset_form.html',
         'email_template_name': 'password_reset_email.html'},
        name='password_reset'),


    url(r'^password_reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'template_name': 'password_reset_confirm.html',
         'post_reset_redirect': 'password_reset_complete'},
        name='password_reset_confirm'),

    url(r'^password_reset/complete/$',
        auth_views.password_reset_complete,
        {'template_name': 'password_reset_complete.html'},
        name='password_reset_complete'),

]
