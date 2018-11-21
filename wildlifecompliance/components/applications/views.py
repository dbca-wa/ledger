from django.http import HttpResponse,JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from wildlifecompliance.components.applications.utils import create_data_from_form
from wildlifecompliance.components.applications.models import Application
from wildlifecompliance.components.applications.email import send_application_invoice_email_notification
from wildlifecompliance.components.main.utils import get_session_application, delete_session_application, bind_application_to_invoice
import json,traceback
from wildlifecompliance.exceptions import BindApplicationException
import xlwt
from wildlifecompliance.utils import serialize_export
from datetime import datetime

class ApplicationView(TemplateView):
    template_name = 'wildlifecompliance/application.html'

    def post(self, request, *args, **kwargs):
        extracted_fields = []
        try:
            print(' ---- applications views.py ---- ')
            application_id = request.POST.pop('application_id')
            application = Application.objects.get(application_id)
            schema = json.loads(request.POST.pop('schema')[0])
            extracted_fields = create_data_from_form(schema,request.POST, request.FILES)
            application.schema = schema;
            application.data = extracted_fields
            print(application_id)
            print(application)
            application.save()
            return redirect(reverse('external'))
        except:
            traceback.print_exc
            return JsonResponse({error:"something went wrong"},safe=False,status=400)


class ApplicationSuccessView(TemplateView):
    template_name = 'wildlifecompliance/application_success.html'

    def get(self, request, *args, **kwargs):
        print('application success view')
        try:
            print(get_session_application(request.session))
            application = get_session_application(request.session)
            invoice_ref = request.GET.get('invoice')
            try:
                bind_application_to_invoice(request, application, invoice_ref)
                invoice_url = request.build_absolute_uri(reverse('payments:invoice-pdf', kwargs={'reference': invoice_ref}))
                if (application.payment_status == 'paid'):
                    send_application_invoice_email_notification(application, invoice_ref, request)
                else:
                    #TODO: check if this ever occurs from the above code and provide error screen for user
                    # console.log('Invoice remains unpaid')
                    delete_session_application(request.session)
                    return redirect(reverse('external'))
            except BindApplicationException as e:
                print(e)
                traceback.print_exc
                delete_session_application(request.session)
                return redirect(reverse('external'))
        except Exception as e:
            print(e)
            traceback.print_exc
            delete_session_application(request.session)
            return redirect(reverse('external'))

        context = {
            'application': application,
            'invoice_ref': invoice_ref,
            'invoice_url': invoice_url
        }
        delete_session_application(request.session)
        return render(request, self.template_name, context)


def export_applications(request):
    filename = 'wildlife_compliance_applications_{}.xls'.format(datetime.now().strftime('%Y%m%dT%H%M%S'))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Applications')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    a=Application.objects.filter(id=140)
    s=serialize_export(a[0])

    keys = [row['key'] for row in s]
    names = [row['name'] for row in s]
    licence_activity = [row['licence_activity'] for row in s]
    labels = [row['label'] for row in s]
    for col_num in range(len(keys)):
        ws.write(row_num, col_num, keys[col_num], font_style)

    row_num += 1
    for col_num in range(len(keys)):
        ws.write(row_num, col_num, names[col_num], font_style)

    row_num += 1
    for col_num in range(len(keys)):
        ws.write(row_num, col_num, licence_activity[col_num], font_style)

    row_num += 1
    for col_num in range(len(keys)):
        ws.write(row_num, col_num, labels[col_num], font_style)
    row_num += 1

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = [row['key'] for row in s]
    for row in a:
        row_num += 1
        col_items = [item['value'] for item in s]
        for col_num in range(len(col_items)):
            ws.write(row_num, col_num, col_items[col_num], font_style)

    wb.save(response)
    return response

