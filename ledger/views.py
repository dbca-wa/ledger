from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from ledger.payments import models
from ledger.accounts import models as account_models
from ledger.accounts import helpers as account_helpers
import json
import os
import mimetypes

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
    

def getAppFile(request,file_id,extension):
    allow_access = False
    #if request.user.is_superuser:
    file_record = account_models.PrivateDocument.objects.get(id=file_id)
    app_id = file_record.file_group_ref_id 
    app_group = file_record.file_group

    if (file_record.file_group == 1 ):
        if account_helpers.is_account_admin(request.user) is True or request.user.is_superuser:
            allow_access = True     
        
      
    if allow_access == True:
        file_record = account_models.PrivateDocument.objects.get(id=file_id)
        file_name_path = file_record.upload.path
        
        if os.path.isfile(file_name_path) is True:
                the_file = open(file_name_path, 'rb')                
                the_data = the_file.read()
                the_file.close()

                if extension == 'msg': 
                    return HttpResponse(the_data, content_type="application/vnd.ms-outlook")
                if extension == 'eml':
                    return HttpResponse(the_data, content_type="application/vnd.ms-outlook")


                return HttpResponse(the_data, content_type=mimetypes.types_map['.'+str(extension)])
    else:
                return HttpResponse("Error loading attachment", content_type="plain/html")
                return