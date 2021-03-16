from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView

class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'ledgergw/web/reports.html'

    def get_context_data(self, **kwargs):
        context = {}
        return context
