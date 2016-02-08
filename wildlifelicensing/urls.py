from django.conf.urls import url
from django.views.generic import TemplateView

urlpattern = [
     url(r'^$', TemplateView.as_view(template_name="index.html")),
]
