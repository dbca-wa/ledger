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
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from oscar.app import application


urlpatterns = [
    url(r'^ledger/admin/', admin.site.urls),
    url(r'^ledger/', include('ledger.accounts.urls', namespace='accounts')),
    url(r'^ledger/', include('ledger.payments.urls', namespace='payments')),
    url(r'^ledger/', include('social_django.urls', namespace='social')),
    url(r'^ledger/checkout/', application.urls),
    url(r'^taxonomy/', include('ledger.taxonomy.urls')),
    url(r'^$', TemplateView.as_view(template_name='customers/base.html'), name='home'),
    url(r'^favicon.ico', RedirectView.as_view(url='{}favicon.ico'.format(settings.STATIC_URL)), name='favicon'),
]
