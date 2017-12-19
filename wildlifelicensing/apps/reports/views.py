from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView, View
from openpyxl.styles import Font
from openpyxl.workbook import Workbook
from openpyxl.writer.write_only import WriteOnlyCell

from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.main import excel
from wildlifelicensing.apps.main.helpers import render_user_name
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.reports.forms import ReportForm
from wildlifelicensing.apps.returns.models import Return

from wildlifelicensing.apps.payments.forms import PaymentsReportForm


def to_string(obj):
    if isinstance(obj,unicode):
        return str(obj.encode('utf-8')) if obj else ''
    return str(obj).encode('utf-8') if obj else ''


class ReportHelper:
    COLUMN_HEADER_FONT = Font(bold=True)

    PROFILE_HEADERS = (
        'User Name',
        'Profile Name',
        'Profile Email',
        'Profile Postal Address',
        'Profile Institution',
    )

    @staticmethod
    def export_profile(profile):
        return (
            render_user_name(profile.user),
            profile.name,
            to_string(profile.email),
            to_string(profile.postal_address),
            to_string(profile.institution)
        )

    LICENCE_TYPE_HEADERS = (
        'Licence Name',
        'Licence Code',
    )

    @staticmethod
    def export_licence_type(licence_type):
        if isinstance(licence_type, WildlifeLicence):
            licence_type = licence_type.licence_type
        return (
            licence_type.display_name,
            licence_type.code
        )

    @staticmethod
    def to_workbook(sheet_name, headers, rows):
        wb = Workbook(write_only=True)
        ws = wb.create_sheet()
        ws.title = sheet_name
        header_cells = []
        for header in headers:
            cell = WriteOnlyCell(ws, value=header)
            cell.font = ReportHelper.COLUMN_HEADER_FONT
            header_cells.append(cell)
        ws.append(header_cells)
        for row in rows:
            ws.append(row)
        return wb

    def __init__(self):
        pass


class ReportsView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/reports.html'

    def get_context_data(self, **kwargs):
        kwargs['form'] = ReportForm()
        kwargs['payments_form'] = PaymentsReportForm()
        kwargs['actions'] = {
            'applications': reverse('wl_reports:applications_report'),
            'licences': reverse('wl_reports:licences_report'),
            'returns': reverse('wl_reports:returns_report'),
            'payments': reverse('wl_payments:payments_report'),
        }

        return TemplateView.get_context_data(self, **kwargs)


class ApplicationsReportView(OfficerRequiredMixin, View):
    APPLICATIONS_HEADERS = (
        'Lodgement Number',
        'Lodgement Date',
        'Processing Status',
        'Proxy Applicant',
        'Assigned Officer',
    )

    @staticmethod
    def export(application):
        return (
            application.reference,
            application.lodgement_date,
            application.processing_status,
            render_user_name(application.proxy_applicant) if application.proxy_applicant else '',
            render_user_name(application.assigned_officer) if application.proxy_applicant else '',
        )

    ALL_HEADERS = \
        ReportHelper.LICENCE_TYPE_HEADERS + \
        APPLICATIONS_HEADERS + \
        ReportHelper.PROFILE_HEADERS

    def row_generator(self, applications):
        for application in applications:
            row = \
                ReportHelper.export_licence_type(application.licence_type) + \
                self.export(application) + \
                ReportHelper.export_profile(application.applicant_profile)
            yield row

    def get(self, request, *args, **kwargs):
        form = ReportForm(request.GET)

        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            qs = Application.objects.filter(lodgement_date__range=(from_date, to_date)).exclude(
                processing_status='draft')
            wb = ReportHelper.to_workbook('Applications', self.ALL_HEADERS, self.row_generator(qs))
            filename = 'applications_{}-{}.xlsx'.format(from_date, to_date)
            return excel.WorkbookResponse(wb, filename)
        else:
            messages.error(request, form.errors)
            redirect('wl_reports:reports')


class LicencesReportView(OfficerRequiredMixin, View):
    LICENCES_HEADERS = (
        'Licence Number',
        'Issue Date',
        'Issuer',
        'Start Date',
        'End Date',
        'Regions',
        'Purpose',
        'Locations',
        'Additional Info',
        'Replaced By',
        'Lodgement Number',
        'Species',
        'Authorised Persons'
    )

    @staticmethod
    def export(licence):
        application = Application.objects.filter(licence=licence).first()
        return (
            licence.reference,
            licence.issue_date,
            render_user_name(licence.issuer),
            licence.start_date,
            licence.end_date,
            ','.join([str(r) for r in licence.regions.all()]),
            to_string(licence.purpose),
            to_string(licence.locations),
            to_string(licence.additional_information),
            licence.replaced_by.reference if licence.replaced_by else '',
            application.reference if application else '',
            ','.join(licence.search_extracted_fields('species_estimated_number')),
            ','.join(licence.search_extracted_fields('authorised_persons'))
        )

    ALL_HEADERS = \
        ReportHelper.LICENCE_TYPE_HEADERS + \
        LICENCES_HEADERS + \
        ReportHelper.PROFILE_HEADERS

    def row_generator(self, licences):
        for licence in licences:
            row = \
                ReportHelper.export_licence_type(licence.licence_type) + \
                self.export(licence) + \
                ReportHelper.export_profile(licence.profile)
            yield row

    def get(self, request, *args, **kwargs):
        form = ReportForm(request.GET)

        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            qs = WildlifeLicence.objects.filter(issue_date__range=(from_date, to_date))
            regions = form.cleaned_data.get('regions')
            if regions:
                qs = qs.filter(regions__in=regions)
            wb = ReportHelper.to_workbook('Licences', self.ALL_HEADERS, self.row_generator(qs))
            filename = 'licences_{}-{}.xlsx'.format(from_date, to_date)
            return excel.WorkbookResponse(wb, filename)
        else:
            messages.error(request, form.errors)
            redirect('wl_reports:reports')


class ReturnsReportView(OfficerRequiredMixin, View):
    RETURNS_HEADERS = (
        'Lodgement Number',
        'Lodgement Date',
        'Licence Number',
        'Licensee',
        'Status',
        'Due Date',
        'Proxy',
        'Nil Return',
        'Comments'
    )

    @staticmethod
    def export(ret):
        return (
            ret.lodgement_number,
            ret.lodgement_date,
            ret.licence.reference,
            render_user_name(ret.licence.holder),
            ret.status,
            ret.due_date,
            render_user_name(ret.proxy_customer),
            'Yes' if ret.nil_return else 'No',
            ret.comments
        )

    ALL_HEADERS = \
        ReportHelper.LICENCE_TYPE_HEADERS + \
        RETURNS_HEADERS

    def row_generator(self, returns):
        for ret in returns:
            row = \
                ReportHelper.export_licence_type(ret.licence.licence_type) + \
                self.export(ret)
            yield row

    def get(self, request, *args, **kwargs):
        form = ReportForm(request.GET)

        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            statuses = ['submitted', 'accepted', 'declined']
            qs = Return.objects.filter(lodgement_date__range=(from_date, to_date)).filter(status__in=statuses)
            wb = ReportHelper.to_workbook('Returns', self.ALL_HEADERS, self.row_generator(qs))
            filename = 'returns_{}-{}.xlsx'.format(from_date, to_date)
            return excel.WorkbookResponse(wb, filename)
        else:
            messages.error(request, form.errors)
            redirect('wl_reports:reports')
