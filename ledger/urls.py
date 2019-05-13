"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import path, re_path, include
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from oscar.app import application


urlpatterns = [
    # path('ledger/admin/', admin.site.urls),
    path('ledger/', include(('ledger.accounts.urls','accounts'), namespace='accounts')),
    path('ledger/', include(('ledger.payments.urls', 'payments'), namespace='payments')),
    path('ledger/', include('social_django.urls', namespace='social')),
    path('ledger/checkout/', application.urls),
    path('taxonomy/', include('ledger.taxonomy.urls')),
    path('', TemplateView.as_view(template_name='customers/base.html'), name='home'),
    path('favicon.ico', RedirectView.as_view(url='{}favicon.ico'.format(settings.STATIC_URL)), name='favicon'),
]