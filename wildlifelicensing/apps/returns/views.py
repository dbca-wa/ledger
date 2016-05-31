import os
import shutil
import tempfile

from django.views.generic.base import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django_datatables_view.base_datatable_view import DatatableMixin, BaseDatatableView
from jsontableschema.model import SchemaModel

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrCustomerRequiredMixin
from wildlifelicensing.apps.returns.models import Return, ReturnTable, ReturnRow
from wildlifelicensing.apps.returns import excel
from wildlifelicensing.apps.returns.forms import UploadSpreadsheetForm

RETURNS_APP_PATH = os.path.join(os.path.dirname(__file__), 'excel_templates')


class EnterReturnView(OfficerOrCustomerRequiredMixin, TemplateView):
    template_name = 'wl/enter_return.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        ret = get_object_or_404(Return, pk=self.args[0])

        kwargs['return'] = ret

        kwargs['tables'] = []

        for schema_name in ret.return_type.get_schema_names():
            schema = SchemaModel(ret.return_type.get_schema(schema_name))
            kwargs['tables'].append({'name': schema_name, 'headers': schema.headers})

        kwargs['upload_spreadsheet_form'] = UploadSpreadsheetForm()

        return super(EnterReturnView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()

        if 'upload' in request.POST:
            form = UploadSpreadsheetForm(request.POST, request.FILES)

            if form.is_valid():
                temp_file_dir = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)
                try:
                    data = form.cleaned_data.get('spreadsheet_file')
                    path = default_storage.save(os.path.join(temp_file_dir, str(data)), ContentFile(data.read()))

                    workbook = excel.load_workbook_content(path)

                    for table in context['tables']:
                        worksheet = excel.get_sheet(workbook, table.get('name'))

                        if worksheet is not None:
                            table_data = excel.TableData(worksheet)
                            table['data'] = list(table_data.rows_by_col_header_it())
                finally:
                    shutil.rmtree(temp_file_dir)
        elif 'submit' in request.POST:
            ret = context['return']

            for table in context['tables']:
                table_namespace = table.get('name') + '::'

                table_data = dict([(key.replace(table_namespace, ''), request.POST.getlist(key)) for key in request.POST.keys() if key.startswith(table_namespace)])

                return_table, created = ReturnTable.objects.get_or_create(name=table.get('name'), ret=ret)

                # delete any existing rows as they will all be recreated
                return_table.returnrow_set.all().delete()

                num_rows = len(table_data.values()[0])

                return_rows = []
                for row_num in range(num_rows):
                    row_data = {}
                    for key, value in table_data.items():
                        row_data[key] = value[row_num]

                    return_rows.append(ReturnRow(return_table=return_table, data=row_data))

                ReturnRow.objects.bulk_create(return_rows)

            ret.status = 'submitted'
            ret.save()

            messages.success(request, 'Return successfully created.')

            return redirect('home')

        return render(request, self.template_name, context)


class CurateReturnView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/curate_return.html'
    login_url = '/'
