import os

from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404

from django_datatables_view.base_datatable_view import DatatableMixin, BaseDatatableView

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrCustomerRequiredMixin
from wildlifelicensing.apps.returns.models import ReturnType, Return
from wildlifelicensing.apps.returns.excel import load_workbook_headings
from wildlifelicensing.apps.returns.forms import UploadSpreadsheetForm

RETURNS_APP_PATH = os.path.join(os.path.dirname(__file__), 'excel_templates')


class EnterReturnView(OfficerOrCustomerRequiredMixin, TemplateView):
    template_name = 'wl/enter_return.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        filename = '%s/%s.xlsx' % (RETURNS_APP_PATH, self.args[0])
        kwargs['headings'] = load_workbook_headings(filename)
        kwargs['upload_spreadsheet_form'] = UploadSpreadsheetForm()

        return_type = get_object_or_404(ReturnType, licence_type__code=self.args[0])

        if len(self.args) > 1:
            rtrn = get_object_or_404(ReturnType, pl=self.args[1])

        return super(EnterReturnView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        form = UploadSpreadsheetForm(request.POST, request.FILES)

        if form.is_valid():
            spreadsheet_file = form.cleaned_date.get('spreadsheet_file')
            


class CurateReturnView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/curate_return.html'
    login_url = '/'
