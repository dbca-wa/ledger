from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from ledger.payments import models as payments_models
from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger.payments.mixins import InvoiceOwnerMixin
from django.shortcuts import get_object_or_404
from ledger.payments.invoice import models as invoice_models
from ledger.api import models as ledgerapi_models
from ledger.api import utils as ledgerapi_utils


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'ledgergw/web/reports.html'

    def get_context_data(self, **kwargs):
        system_id = self.request.GET.get('system_id',None)
        context = {'system_id': system_id, 'system_id_exists': False}

        if payments_models.OracleInterfaceSystem.objects.filter(system_id=system_id).count() > 0:
             context['system_id_exists'] = True
        return context

class InvoicePDFView(View):

    def get(self, request, *args, **kwargs):
        apikey = self.kwargs['api_key']
        if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
                if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
                      invoice = get_object_or_404(invoice_models.Invoice, reference=self.kwargs['reference'])
                      response = HttpResponse(content_type='application/pdf')
                      response.write(create_invoice_pdf_bytes('invoice.pdf',invoice))
                      return response
        response = HttpResponse("<b>Forbidden</b>",content_type='text/html')

        return response

    def get_object(self):
        invoice = get_object_or_404(invoice_models.Invoice, reference=self.kwargs['reference'])
        return invoice


