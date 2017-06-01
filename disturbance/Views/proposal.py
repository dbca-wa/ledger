from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView

from preserialize.serialize import serialize
from ledger.accounts.models import EmailUser
from disturbance.utils import extract_licence_fields, update_licence_fields
from disturbance.models import ProposalType


class ProposalView(TemplateView):
    template_name = 'disturbance/proposal.html'
    def post(self, request, *args, **kwargs):
        extracted_fields = extract_licence_fields(ProposalType.objects.first().schema,request.POST)
        return JsonResponse(extracted_fields,safe=False)
