from django.conf.urls import url
from django.views.generic import TemplateView

from views import DashboardView

urlpatterns = [
    url('^dashboard/', DashboardView.as_view(), name='dashboard'),
    url('^dashboard-tree/', TemplateView.as_view(template_name='officers_dashboard_tree.html'), name='dashboard-tree'),
]
