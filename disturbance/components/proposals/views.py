from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from disturbance.utils import create_data_from_form
import json,traceback

class ProposalView(TemplateView):
    template_name = 'disturbance/proposal.html'

    def post(self, request, *args, **kwargs):
        extracted_fields = []
        try:
            schema = json.loads(request.POST.pop('schema')[0])
            extracted_fields = create_data_from_form(schema,request.POST, request.FILES)
        except:
            traceback.print_exc
        return JsonResponse(extracted_fields,safe=False)
