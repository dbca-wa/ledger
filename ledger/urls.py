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
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from oscar.app import application
from ledger import views
from ledger import uploads

urlpatterns = [
    #url(r'^ledger/admin/', admin.site.urls, name='ledger_admin'),
    url(r'^ledger/', include('ledger.accounts.urls', namespace='accounts')),
    url(r'^ledger/', include('ledger.payments.urls', namespace='payments')),
    url(r'^ledger/', include('social_django.urls', namespace='social')),
    url(r'^ledger/checkout/', application.urls),
    url(r'^ledger-uploads/$', uploads.PrivateMediaUploads, name='private_media_uploads'),
    url(r'^private-media/view/(?P<file_id>\d+)-(\w+).(?P<extension>\w\w\w)$', views.getAppFile, name='view_private_ledger_file'),
    url(r'^private-media/view/(?P<file_id>\d+)-(\w+).(?P<extension>\w\w\w\w)$', views.getAppFile, name='view_private_ledger_file2'),    
    url(r'^taxonomy/', include('ledger.taxonomy.urls')),
    url(r'^$', views.HomeView.as_view(), name='home'),  
    # url(r'^$', TemplateView.as_view(template_name='customers/base.html'), name='home')    
]
