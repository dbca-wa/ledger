from django.views.generic import TemplateView
from django.shortcuts import redirect
from braces.views import LoginRequiredMixin

from wildlifelicensing.apps.accounts.helpers import is_officer, is_customer


class DashBoardRoutingView(TemplateView):
    template_name = 'index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect('dashboard:quick')
        else:
            return super(DashBoardRoutingView, self).get(*args, **kwargs)


class DashboardQuickView(LoginRequiredMixin, TemplateView):
    template_name = 'dash_quick.html'


class DashboardTableView(LoginRequiredMixin, TemplateView):
    template_name = 'dash_tables.html'
