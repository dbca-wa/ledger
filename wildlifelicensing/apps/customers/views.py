from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = 'customers_dashboard.html'
