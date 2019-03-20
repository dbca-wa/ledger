from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.conf import settings
from django.template.loader import render_to_string
from wildlifecompliance.components.applications.utils import SchemaParser
from wildlifecompliance.components.applications.models import Application
from wildlifecompliance.components.applications.email import send_application_invoice_email_notification
from wildlifecompliance.components.main.utils import get_session_application, delete_session_application, bind_application_to_invoice
import json
from wildlifecompliance.exceptions import BindApplicationException
import xlwt
from wildlifecompliance.utils import serialize_export, unique_column_names
from datetime import datetime
from django.utils import timezone
import os
import subprocess
import traceback

import logging
logger = logging.getLogger(__name__)

class ApplicationView(TemplateView):
    template_name = 'wildlifecompliance/application.html'

    def post(self, request, *args, **kwargs):
        extracted_fields = []
        try:
            print(' ---- applications views.py ---- ')
            application_id = request.POST.pop('application_id')
            application = Application.objects.get(application_id)
            schema = json.loads(request.POST.pop('schema')[0])
            parser = SchemaParser()
            extracted_fields = parser.create_data_from_form(
                schema, request.POST, request.FILES)
            application.schema = schema
            application.data = extracted_fields
            print(application_id)
            print(application)
            application.save()
            return redirect(reverse('external'))
        except BaseException:
            traceback.print_exc
            return JsonResponse(
                {error: "something went wrong"}, safe=False, status=400)


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
                invoice_url = request.build_absolute_uri(
                    reverse('payments:invoice-pdf', kwargs={'reference': invoice_ref}))
                if (application.payment_status == 'paid'):
                    send_application_invoice_email_notification(
                        application, invoice_ref, request)
                else:
                    # TODO: check if this ever occurs from the above code and provide error screen for user
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


def pdflatex(request):

    now = timezone.localtime(timezone.now())
    #report_date = now.strptime(request.GET.get('date'), '%Y-%m-%d').date()
    report_date = now

    #template = request.GET.get("template", "pfp")
    template = "wildlife_compliance_licence"
    response = HttpResponse(content_type='application/pdf')
    #texname = template + ".tex"
    #filename = template + ".pdf"
    #texname = template + "_" + request.user.username + ".tex"
    #filename = template + "_" + request.user.username + ".pdf"
    texname = template + ".tex"
    filename = template + ".pdf"
    timestamp = now.isoformat().rsplit(
        ".")[0].replace(":", "")
    if template == "wildlife_compliance_licence":
        downloadname = "wildlife_compliance_licence_" + report_date.strftime('%Y-%m-%d') + ".pdf"
    else:
        downloadname = "wildlife_compliance_licence_" + template + "_" + report_date.strftime('%Y-%m-%d') + ".pdf"
    error_response = HttpResponse(content_type='text/html')
    errortxt = downloadname.replace(".pdf", ".errors.txt.html")
    error_response['Content-Disposition'] = (
        '{0}; filename="{1}"'.format(
        "inline", errortxt))

    subtitles = {
        #"ministerial_report": "Ministerial Report",
        "cover_page": "Cover Page",
        "licence": "Licence",
        #"form268a": "268a - Planned Burns",
    }
    embed = False if request.GET.get("embed") == "false" else True

    context = {
        'user': request.user.get_full_name(),
        'report_date': report_date.strftime('%e %B %Y').strip(),
        'time': report_date.strftime('%H:%M'),
#        'current_finyear': current_finyear(),
#        'rpt_map': self.rpt_map,
#        'item_map': self.item_map,
#        'form': form_data,
        'embed': embed,
        'headers': request.GET.get("headers", True),
        'title': request.GET.get("title", "Bushfire Reporting System"),
        'subtitle': subtitles.get(template, ""),
        'timestamp': now,
        'downloadname': downloadname,
        'settings': settings,
        'baseurl': request.build_absolute_uri("/")[:-1]
    }
    disposition = "attachment"
    #disposition = "inline"
    response['Content-Disposition'] = (
        '{0}; filename="{1}"'.format(
            disposition, downloadname))

    #import ipdb; ipdb.set_trace()
    directory = os.path.join(settings.MEDIA_ROOT, 'wildlife_compliance_licence' + os.sep)
    if not os.path.exists(directory):
        logger.debug("Making a new directory: {}".format(directory))
        os.makedirs(directory)

    logger.debug('Starting  render_to_string step')
    err_msg = None
    try:
        output = render_to_string("latex/" + template + ".tex", context, request=request)
    except Exception as e:
        import traceback
        err_msg = u"PDF tex template render failed (might be missing attachments):"
        logger.debug(err_msg + "\n{}".format(e))

        error_response.write(err_msg + "\n\n{0}\n\n{1}".format(e,traceback.format_exc()))
        return error_response

    with open(directory + texname, "w") as f:
        f.write(output.encode('utf-8'))
        logger.debug("Writing to {}".format(directory + texname))

    #import ipdb; ipdb.set_trace()
    logger.debug("Starting PDF rendering process ...")
    cmd = ['latexmk', '-cd', '-f', '-silent', '-pdf', directory + texname]
    #cmd = ['latexmk', '-cd', '-f', '-pdf', directory + texname]
    logger.debug("Running: {0}".format(" ".join(cmd)))
    subprocess.call(cmd)

    logger.debug("Cleaning up ...")
    cmd = ['latexmk', '-cd', '-c', directory + texname]
    logger.debug("Running: {0}".format(" ".join(cmd)))
    subprocess.call(cmd)

    logger.debug("Reading PDF output from {}".format(filename))
    response.write(open(directory + filename).read())
    logger.debug("Finally: returning PDF response.")
    return response


#def update_workbooks(request):
#    writer = ExcelWriter()
#    writer.update_workbooks()
#
# def export_applications(request):
#    filename = 'wildlife_compliance_applications_{}.xls'.format(datetime.now().strftime('%Y%m%dT%H%M%S'))
#    response = HttpResponse(content_type='application/ms-excel')
#    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
#
#    wb = xlwt.Workbook(encoding='utf-8')
#    ws = wb.add_sheet('Applications')
#
#    # Sheet header, first row
#    row_num = 0
#
#    font_style = xlwt.XFStyle()
#    font_style.font.bold = True
#
#    applications = Application.objects.filter(id__in=[121, 122, 123])
#
#    for application in applications:
#        s=serialize_export(application)
#
#
#        columns = unique_column_names()
#        names = [row['name'] for row in s]
#        row_num += 1
#        for col_num in range(len(columns)):
#            ws.write(row_num, col_num, columns[col_num], font_style)
#
#
#        keys = [row['key'] for row in s]
#
##activity = [row['activity'] for row in s]
##purpose = [row['purpose'] for row in s]
#        labels = [row['label'] for row in s]
#        for col_num in range(len(keys)):
#            ws.write(row_num, col_num, keys[col_num], font_style)
#
#        row_num += 1
#        for col_num in range(len(keys)):
#            ws.write(row_num, col_num, activity[col_num], font_style)
#
#        row_num += 1
#        for col_num in range(len(keys)):
#            ws.write(row_num, col_num, purpose[col_num], font_style)
#
#        row_num += 1
#        for col_num in range(len(keys)):
#            ws.write(row_num, col_num, labels[col_num], font_style)
#        row_num += 1
#
# Sheet body, remaining rows
#        font_style = xlwt.XFStyle()
#
#        rows = [row['key'] for row in s]
#        for row in a:
#            row_num += 1
#            col_items = [item['value'] for item in s]
#            for col_num in range(len(col_items)):
#                ws.write(row_num, col_num, col_items[col_num], font_style)
#
#    wb.save(response)
#    return response
