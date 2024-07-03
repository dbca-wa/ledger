from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from ledger.payments import models
import json

class HomeView(TemplateView):
    template_name = 'ledger/home.html'

    def get_context_data(self, **kwargs):        
        context = {}
        pil_array = []

        pil_cache = cache.get('models.PaymentInformationLink.objects.filter(active=True)')

        if pil_cache is None:
            payment_information_links = models.PaymentInformationLink.objects.filter(active=True)
            for pil in payment_information_links:            
                row = {}
                row['title'] = pil.title
                row['description'] = pil.description
                row['url'] = pil.url
                pil_array.append(row)
            cache.set('models.PaymentInformationLink.objects.filter(active=True)',json.dumps(pil_array), 86400)
        else:
            pil_array = json.loads(pil_cache)
        context['pil_array'] = pil_array
        return context