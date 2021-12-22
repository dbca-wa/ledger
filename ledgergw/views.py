from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from ledger.payments import models as payments_models

class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'ledgergw/web/reports.html'

    def get_context_data(self, **kwargs):
        system_id = self.request.GET.get('system_id',None)
        context = {'system_id': system_id, 'system_id_exists': False}

        if payments_models.OracleInterfaceSystem.objects.filter(system_id=system_id).count() > 0:
             context['system_id_exists'] = True
             

        return context
