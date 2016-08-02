from django.views.generic.base import TemplateView, View
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect

from openpyxl.workbook import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.styles import Font

from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main import excel
from wildlifelicensing.apps.returns.models import Return

from wildlifelicensing.apps.reports.forms import ReportForm


APPLICATIONS_HEADER_FIELDS = ('Licence Type', 'Lodgement Number', 'Lodgement Date', 'Applicant', 'Applicant Profile', 'Processing Status')
LICENCES_HEADER_FIELDS = ('Licence Type', 'Licence Code', 'Licence Number', 'Licensee', 'Issue Date', 'Issuer', 'Start Date', 'End Date')
RETURNS_HEADER_FIELDS = ('Licence Type', 'Lodgement Number', 'Lodgement Date', 'Licensee', 'Due Date', 'Status')

COLUMN_HEADER_FONT = Font(bold=True)


class ReportsView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/reports.html'

    def get_context_data(self, **kwargs):
        kwargs['form'] = ReportForm()

        return TemplateView.get_context_data(self, **kwargs)


class ApplicationsReportView(View):
    def get(self, request, *args, **kwargs):
        form = ReportForm(request.GET)

        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')

            wb = Workbook()

            # get default sheet and rename
            ws = excel.get_or_create_sheet(wb, 'Sheet')
            ws.title = 'Applications'

            excel.write_values(ws, 1, 1, APPLICATIONS_HEADER_FIELDS, direction='right', font=COLUMN_HEADER_FONT)

            row = 2
            for application in Application.objects.filter(lodgement_date__range=(from_date, to_date)).exclude(processing_status='draft'):
                row_values = (application.licence_type.name,
                              '{}-{}'.format(application.lodgement_number, application.lodgement_sequence),
                              application.lodgement_date, application.applicant_profile.user.get_full_name(),
                              application.applicant_profile.name)
                excel.write_values(ws, row, 1, row_values, direction='right', font=None)
                row += 1

            filename = 'applications_{}-{}.xlsx'.format(from_date, to_date)
            return excel.WorkbookResponse(wb, filename)
        else:
            messages.error(request, form.errors)
            redirect('wl_reports:reports')


class LicencesReportView(View):
    def get(self, request, *args, **kwargs):
        form = ReportForm(request.GET)

        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')

            wb = Workbook()

            # get default sheet and rename
            ws = excel.get_or_create_sheet(wb, 'Sheet')
            ws.title = 'Licences'

            excel.write_values(ws, 1, 1, LICENCES_HEADER_FIELDS, direction='right', font=COLUMN_HEADER_FONT)

            row = 2
            for licence in WildlifeLicence.objects.filter(issue_date__range=(from_date, to_date)):
                row_values = (licence.licence_type.name, licence.licence_type.code,
                              '{}-{}'.format(licence.licence_number, licence.sequence_number),
                              licence.holder.get_full_name(), licence.issue_date, licence.issuer.get_full_name(),
                              licence.start_date, licence.end_date)
                excel.write_values(ws, row, 1, row_values, direction='right', font=None)
                row += 1

            filename = 'licences_{}-{}.xlsx'.format(from_date, to_date)
            return excel.WorkbookResponse(wb, filename)
        else:
            messages.error(request, form.errors)
            redirect('wl_reports:reports')


class ReturnsReportView(View):
    def get(self, request, *args, **kwargs):
        form = ReportForm(request.GET)

        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')

            wb = Workbook()

            # get default sheet and rename
            ws = excel.get_or_create_sheet(wb, 'Sheet')
            ws.title = 'Returns'

            excel.write_values(ws, 1, 1, RETURNS_HEADER_FIELDS, direction='right', font=COLUMN_HEADER_FONT)

            row = 2
            for ret in Return.objects.filter(lodgement_date__range=(from_date, to_date)):
                row_values = (ret.licence.licence_type.name, ret.lodgement_number, ret.lodgement_date,
                              ret.licence.holder.get_full_name(), ret.due_date, ret.status)
                excel.write_values(ws, row, 1, row_values, direction='right', font=None)
                row += 1

            filename = 'returns_{}-{}.xlsx'.format(from_date, to_date)
            return excel.WorkbookResponse(wb, filename)
        else:
            messages.error(request, form.errors)
            redirect('wl_reports:reports')
