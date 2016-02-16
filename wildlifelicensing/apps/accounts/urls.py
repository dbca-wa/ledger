from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url('^login/', views.LoginView.as_view(), name='login'),

    url('^logout/', auth_views.logout, {'next_page': 'home'}, name='logout'),

    url(r'create/?$', views.UserCreateView.as_view(), name='user_create'),
]
