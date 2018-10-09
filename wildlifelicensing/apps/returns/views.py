import os
import shutil
import tempfile
import datetime

from django.views.generic.base import TemplateView, View
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from preserialize.serialize import serialize

from ledger.accounts.models import Document
from wildlifelicensing.apps.returns.models import Return, ReturnTable, ReturnRow, ReturnLogEntry, ReturnType, \
    ReturnAmendmentRequest
from wildlifelicensing.apps.main import excel
from wildlifelicensing.apps.returns.forms import UploadSpreadsheetForm, NilReturnForm, ReturnsLogEntryForm,\
    ReturnAmendmentRequestForm
from wildlifelicensing.apps.returns.utils_schema import Schema, create_return_template_workbook
from wildlifelicensing.apps.returns.utils import format_return
from wildlifelicensing.apps.returns.signals import return_submitted
from wildlifelicensing.apps.main.helpers import is_officer
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder
from wildlifelicensing.apps.main.utils import format_communications_log_entry
from wildlifelicensing.apps.returns.mixins import UserCanEditReturnMixin, UserCanViewReturnMixin, \
    UserCanCurateReturnMixin
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.returns.emails import send_amendment_requested_email

LICENCE_TYPE_NUM_CHARS = 2
LODGEMENT_NUMBER_NUM_CHARS = 6

RETURNS_APP_PATH = os.path.join(os.path.dirname(__file__), 'excel_templates')

DATE_FORMAT = '%d/%m/%Y'


def _is_post_data_valid(ret, tables_info, post_data):
    for table in tables_info:
        table_rows = _get_table_rows_from_post(table.get('name'), post_data)
        if len(table_rows) == 0:
            return False
        schema = Schema(ret.return_type.get_schema_by_name(table.get('name')))
        if not schema.is_all_valid(table_rows):
            return False
    return True


def _get_validated_rows_from_post(ret, table_name, post_data):
    rows = _get_table_rows_from_post(table_name, post_data)
    schema = Schema(ret.return_type.get_schema_by_name(table_name))
    return list(schema.rows_validator(rows))


def _get_table_rows_from_post(table_name, post_data):
    table_namespace = table_name + '::'
    by_column = dict([(key.replace(table_namespace, ''), post_data.getlist(key)) for key in post_data.keys() if
                      key.startswith(table_namespace)])
    # by_column is of format {'col_header':[row1_val, row2_val,...],...}
    num_rows = len(list(by_column.values())[0]) if len(by_column.values()) > 0 else 0
    rows = []
    for row_num in range(num_rows):
        row_data = {}
        for key, value in by_column.items():
            row_data[key] = value[row_num]
        # filter empty rows.
        is_empty = True
        for value in row_data.values():
            if len(value.strip()) > 0:
                is_empty = False
                break
        if not is_empty:
            rows.append(row_data)
    return rows


def _create_return_data_from_post_data(ret, tables_info, post_data):
    for table in tables_info:
        rows = _get_table_rows_from_post(table.get('name'), post_data)
        if rows:
            return_table = ReturnTable.objects.get_or_create(name=table.get('name'), ret=ret)[0]
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [ReturnRow(return_table=return_table, data=row) for row in rows]
            ReturnRow.objects.bulk_create(return_rows)


class EnterReturnView(UserCanEditReturnMixin, TemplateView):
    template_name = 'wl/enter_return.html'
    login_url = '/'

    def _set_submitted(self, ret):
        ret.lodgement_number = '%s-%s' % (str(ret.licence.licence_type.pk).zfill(LICENCE_TYPE_NUM_CHARS),
                                          str(ret.pk).zfill(LODGEMENT_NUMBER_NUM_CHARS))

        ret.lodgement_date = datetime.date.today()

        if is_officer(self.request.user):
            ret.proxy_customer = self.request.user

        # assume that all the amendment requests has been solved.
        pending_amendments = ret.pending_amendments_qs
        if pending_amendments:
            pending_amendments.update(status='amended')
            ret.status = 'amended'
        else:
            ret.status = 'submitted'
        ret.save()

        message = 'Return successfully submitted.'

        # update next return in line's status to become the new current return
        next_ret = Return.objects.filter(licence=ret.licence, status='future').order_by('due_date').first()

        if next_ret is not None:
            next_ret.status = 'current'
            next_ret.save()

            message += ' The next return for this licence can now be entered and is due on {}.'. \
                format(next_ret.due_date.strftime(DATE_FORMAT))

        return_submitted.send(sender=self.__class__, ret=ret)

        messages.success(self.request, message)

    def get_context_data(self, **kwargs):
        ret = get_object_or_404(Return, pk=self.args[0])

        kwargs['return'] = ret

        kwargs['tables'] = []

        for resource in ret.return_type.resources:
            resource_name = resource.get('name')
            schema = Schema(resource.get('schema'))
            headers = []
            for f in schema.fields:
                header = {
                    "title": f.name,
                    "required": f.required
                }
                if f.is_species:
                    header["species"] = f.species_type
                headers.append(header)
            table = {
                'name': resource_name,
                'title': resource.get('title', resource.get('name')),
                'headers': headers
            }
            try:
                return_table = ret.returntable_set.get(name=resource_name)
                rows = [return_row.data for return_row in return_table.returnrow_set.all()]
                validated_rows = list(schema.rows_validator(rows))
                table['data'] = validated_rows
            except ReturnTable.DoesNotExist:
                pass

            kwargs['tables'].append(table)

        if 'upload_spreadsheet_form' not in kwargs:
            kwargs['upload_spreadsheet_form'] = UploadSpreadsheetForm()
        kwargs['nil_return_form'] = NilReturnForm()

        pending_amendments = ret.pending_amendments_qs
        if pending_amendments:
            kwargs['amendments'] = pending_amendments

        return super(EnterReturnView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        ret = context['return']

        if 'upload' in request.POST:
            form = UploadSpreadsheetForm(request.POST, request.FILES)

            if form.is_valid():
                temp_file_dir = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)
                try:
                    data = form.cleaned_data.get('spreadsheet_file')
                    path = default_storage.save(os.path.join(temp_file_dir, str(data)), ContentFile(data.read()))

                    workbook = excel.load_workbook_content(path)

                    for table in context['tables']:
                        worksheet = excel.get_sheet(workbook, table.get('title')) \
                            or excel.get_sheet(workbook, table.get('name'))
                        if worksheet is not None:
                            table_data = excel.TableData(worksheet)
                            schema = Schema(ret.return_type.get_schema_by_name(table.get('name')))
                            excel_rows = list(table_data.rows_by_col_header_it())
                            has_errors = not schema.is_all_valid(excel_rows)
                            if has_errors:
                                messages.error(request, "Your return contains some errors. See below.")
                            validated_rows = list(schema.rows_validator(excel_rows))
                            # We want to stringify the datetime/date that might have been created by the excel parser
                            for vr in validated_rows:
                                for col, validation in vr.items():
                                    value = validation.get('value')
                                    if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                                        validation['value'] = value.strftime(DATE_FORMAT)
                            table['data'] = validated_rows
                        else:
                            messages.warning(request, 'Missing worksheet ' + table.get('name'))
                finally:
                    shutil.rmtree(temp_file_dir)
            else:
                context['upload_spreadsheet_form'] = form

        elif 'draft' in request.POST or 'draft_continue' in request.POST:
            _create_return_data_from_post_data(ret, context['tables'], request.POST)

            if is_officer(request.user):
                ret.proxy_customer = request.user

            ret.status = 'draft'
            ret.save()

            messages.warning(request, 'Return saved as draft.')

            # redirect or reshow page depending on whether save or save/continue was clicked
            if 'draft' in request.POST:
                return redirect('home')
            else:
                for table in context['tables']:
                    table['data'] = _get_validated_rows_from_post(ret, table.get('name'), request.POST)
        elif 'lodge' in request.POST:
            if _is_post_data_valid(ret, context['tables'], request.POST):

                _create_return_data_from_post_data(ret, context['tables'], request.POST)

                self._set_submitted(ret)
                return redirect('home')
            else:
                for table in context['tables']:
                    table['data'] = _get_validated_rows_from_post(ret, table.get('name'), request.POST)
                    if len(table['data']) == 0:
                        messages.warning(request,
                                         "You must enter data for {} or submit a Nil Return".format(table.get('name')))
                    else:
                        messages.error(request,
                                       "Your return contains some errors. See below.")

        elif 'nil' in request.POST:
            form = NilReturnForm(request.POST)
            if form.is_valid():
                ret.nil_return = True
                ret.comments = form.cleaned_data['comments']
                self._set_submitted(ret)
                return redirect('home')

        return render(request, self.template_name, context)


class CurateReturnView(UserCanCurateReturnMixin, EnterReturnView):
    template_name = 'wl/curate_return.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        ctx = super(CurateReturnView, self).get_context_data(**kwargs)
        ret = ctx['return']
        ctx['return'] = serialize(ret, posthook=format_return, exclude=['application','applicationrequest_ptr','licence'])

        if ret.proxy_customer is None:
            to = ret.licence.holder
        else:
            to = ret.proxy_customer

        ctx['log_entry_form'] = ReturnsLogEntryForm(
            to=to.get_full_name(),
            fromm=self.request.user.get_full_name(),
        )

        ctx['amendment_request_form'] = ReturnAmendmentRequestForm(
            ret=ret,
            officer=self.request.user
        )

        amendment_requests = ReturnAmendmentRequest.objects.filter(ret=ret)
        ctx['amendment_requests'] = serialize(amendment_requests, fields=['status', 'reason'])
        return ctx

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        ret = get_object_or_404(Return, pk=self.args[0])

        if 'accept' in request.POST:
            if _is_post_data_valid(ret, context['tables'], request.POST):
                _create_return_data_from_post_data(ret, context['tables'], request.POST)

                ret.status = 'accepted'
                ret.save()

                messages.success(request, 'Return was accepted.')
                return redirect('home')
            elif ret.nil_return:
                ret.status = 'accepted'
                ret.save()

                messages.success(request, 'Nil return was accepted.')
                return redirect('home')
            else:
                for table in context['tables']:
                    table['data'] = _get_validated_rows_from_post(ret, table.get('name'), request.POST)
                    if len(table['data']) == 0:
                        messages.warning(request, "You must enter data for {}".format(table.get('name')))

                return render(request, self.template_name, context)
        else:
            ret.status = 'declined'
            ret.save()

            messages.warning(request, 'Return was declined.')
            return redirect('home')


class ViewReturnReadonlyView(UserCanViewReturnMixin, TemplateView):
    template_name = 'wl/view_return_read_only.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        ret = get_object_or_404(Return, pk=self.args[0])

        kwargs['return'] = ret

        kwargs['tables'] = []

        for resource in ret.return_type.resources:
            resource_name = resource.get('name')
            schema = Schema(resource.get('schema'))
            table = {'name': resource_name, 'title': resource.get('title', resource.get('name')),
                     'headers': schema.headers}
            try:
                return_table = ret.returntable_set.get(name=resource_name)
                table['data'] = [return_row.data for return_row in return_table.returnrow_set.all()]
            except ReturnTable.DoesNotExist:
                pass

            kwargs['tables'].append(table)

        return super(ViewReturnReadonlyView, self).get_context_data(**kwargs)


class ReturnLogListView(UserCanCurateReturnMixin, View):
    def get(self, request, *args, **kwargs):
        ret = get_object_or_404(Return, pk=args[0])
        data = serialize(ReturnLogEntry.objects.filter(ret=ret),
                         posthook=format_communications_log_entry,
                         exclude=['ret', 'communicationslogentry_ptr', 'customer', 'officer']),

        return JsonResponse({'data': data[0]}, safe=False, encoder=WildlifeLicensingJSONEncoder)


class AddReturnLogEntryView(UserCanCurateReturnMixin, View):
    def post(self, request, *args, **kwargs):
        form = ReturnsLogEntryForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            ret = get_object_or_404(Return, pk=args[0])

            customer = ret.licence.holder

            staff = request.user

            kwargs = {
                'staff': staff,
                'customer': customer,
                'ret': ret,
                'type': form.cleaned_data['type'],
                'text': form.cleaned_data['text'],
                'subject': form.cleaned_data['subject'],
                'to': form.cleaned_data['to'],
                'fromm': form.cleaned_data['fromm']
            }
            entry = ReturnLogEntry.objects.create(**kwargs)
            if request.FILES and 'attachment' in request.FILES:
                document = Document.objects.create(file=request.FILES['attachment'])
                entry.documents.add(document)

            return JsonResponse('ok', safe=False, encoder=WildlifeLicensingJSONEncoder)
        else:
            return JsonResponse(
                {
                    "errors": [
                        {
                            'status': "422",
                            'title': 'Data not valid',
                            'detail': form.errors
                        }
                    ]
                },
                safe=False, encoder=WildlifeLicensingJSONEncoder, status=422)


class DownloadReturnTemplate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return_type = get_object_or_404(ReturnType, pk=args[0])
        filename = 'Return_{}_template.xlsx'.format(return_type.licence_type.code)

        wb = create_return_template_workbook(return_type)

        return excel.WorkbookResponse(wb, filename)


class AmendmentRequestView(UserCanCurateReturnMixin, View):
    def post(self, request, *args, **kwargs):
        amendment_request_form = ReturnAmendmentRequestForm(request.POST)
        if amendment_request_form.is_valid():
            amendment_request = amendment_request_form.save()
            ret = amendment_request.ret
            ret.status = 'amendment_required'
            ret.save()
            application = get_object_or_404(Application, licence=ret.licence)
            send_amendment_requested_email(amendment_request, request, application)
            response = {
                'amendment_request': serialize(amendment_request, fields=['status', 'reason'])
            }
            return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)
        else:
            return JsonResponse(amendment_request_form.errors,
                                safe=False,
                                encoder=WildlifeLicensingJSONEncoder,
                                status=422)
