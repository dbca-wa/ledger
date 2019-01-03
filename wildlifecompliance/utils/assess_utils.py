from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.core.files.base import ContentFile, File
from django.http import HttpResponse
from django.template.loader import render_to_string
from collections import OrderedDict
from wildlifecompliance.components.applications.models import Application, ApplicationType, ApplicationActivityType, ApplicationDocument
from wildlifecompliance.components.licences.models import DefaultActivityType, WildlifeLicence, WildlifeLicenceClass, WildlifeLicenceActivity
from wildlifecompliance.components.organisations.models import Organisation
from ledger.accounts.models import OrganisationAddress
from django.contrib.postgres.fields.jsonb import JSONField
from wildlifecompliance.utils import SearchUtils, search_multiple_keys
from wildlifecompliance.components.licences.models import DefaultActivity
from ledger.accounts.models import EmailUser
from django.utils import timezone
import subprocess

import os
import re
import shutil

import logging
logger = logging.getLogger(__name__)


import json
from datetime import datetime

def replace_special_chars(input_str, new_char='_'):
    return re.sub('[^A-Za-z0-9]+', new_char, input_str).strip('_').lower()


def get_purposes(licence_class_short_name):
    """
        activity_type --> purpose

        for licence_class in DefaultActivityType.objects.filter(licence_class_id=13):
            #print '{} {}'.format(licence_class.licence_class.id, licence_class.licence_class.name)
            for activity_type in DefaultActivity.objects.filter(activity_type_id=licence_class.activity_type_id):
                print '    {}'.format(activity_type.activity.name, activity_type.activity.short_name)
        ____________________

        DefaultActivityType.objects.filter(licence_class__short_name='Flora Other Purpose').values_list('licence_class__activity_type__activity__name', flat=True).distinct()
    """
    activity_type =  DefaultActivityType.objects.filter(licence_class__short_name=licence_class_short_name).order_by('licence_class__activity_type__activity__name')
    return activity_type.values_list('licence_class__activity_type__activity__name', flat=True).distinct()



def create_app_activity_type_model(licence_category, app_ids=[], exclude_app_ids=[]):
    """
    from wildlifecompliance.utils.excel_utils import write_excel_model
    write_excel_model('Fauna Other Purpose')
    """

    if app_ids:
        # get a filterset with single application
        applications = Application.objects.filter(id__in=app_ids)
    else:
        #applications = Application.objects.filter(licence_category=licence_category).exclude(processing_status=Application.PROCESSING_STATUS_DRAFT[0]).exclude(id__in=cur_app_ids)
        applications = Application.objects.filter(licence_category=licence_category).exclude(id__in=exclude_app_ids)

    obj_list = []
    #import ipdb; ipdb.set_trace()
    for application in applications.order_by('id'):

        activities = get_purposes(application.licence_type_data['short_name']).values_list('activity_type__short_name', flat=True)
        for activity_type in application.licence_type_data['activity_type']:
            if activity_type['short_name'] in list(activities):
                app_activity_type, created = ApplicationActivityType.objects.get_or_create(
                    application=application,
                    activity_name=activity_type['activity'][0]['name'],
                    name=activity_type['name'],
                    short_name=activity_type['short_name'],
                    code=WildlifeLicenceActivity.objects.get(name=activity_type['activity'][0]['name']).code
                )
                obj_list.append(app_activity_type)

    return obj_list

def create_licence(application, activity_name, new_app):
    """ activity_name='Importing Fauna (Non-Commercial)'
        licence_category ='Flora Other Purpose'
    """
    licence = None
    activity=WildlifeLicenceActivity.objects.get(name=activity_name)
    licence_class = WildlifeLicenceClass.objects.get(short_name=application.licence_category)
    #import ipdb; ipdb.set_trace()
    if application.applicant_type == Application.APPLICANT_TYPE_ORGANISATION:
        qs_licence = WildlifeLicence.objects.filter(org_applicant_id=application.applicant_id, licence_class=licence_class)
        if qs_licence.exists():
            #licence_sequence = qs_licence.last().licence_sequence + 1 if qs_licence.filter(licence_type=activity).exists() else qs_licence.last().licence_sequence
            licence_sequence = qs_licence.last().licence_sequence + 1 if new_app else qs_licence.last().licence_sequence
            # use existing licence, just increment sequence_number
            licence = WildlifeLicence.objects.create(
                licence_number=qs_licence.last().licence_number,
                #licence_sequence=qs_licence.last().licence_sequence + 1,
                licence_sequence=licence_sequence,
                current_application=application,
                org_applicant_id=application.applicant_id,
                submitter=application.submitter,
                licence_type=activity,
                licence_class=licence_class
            )
        else:
            licence = WildlifeLicence.objects.create(current_application=application,org_applicant_id=application.applicant_id,submitter=application.submitter,
                          licence_type=activity,licence_class=licence_class)

    elif application.applicant_type == Application.APPLICANT_TYPE_PROXY:
        qs_licence = WildlifeLicence.objects.filter(proxy_applicant_id=application.applicant_id, licence_class=licence_class)
        if qs_licence.exists():
            #licence_sequence = qs_licence.last().licence_sequence + 1 if qs_licence.filter(licence_type=activity).exists() else qs_licence.last().licence_sequence
            licence_sequence = qs_licence.last().licence_sequence + 1 if new_app else qs_licence.last().licence_sequence
            # use existing licence, just increment sequence_number
            licence = WildlifeLicence.objects.create(
                licence_number=qs_licence.last().licence_number,
                #licence_sequence=qs_licence.last().licence_sequence + 1,
                licence_sequence=licence_sequence,
                current_application=application,
                proxy_applicant_id=application.applicant_id,
                submitter=application.submitter,
                licence_type=activity,
                licence_class=licence_class
            )
        else:
            licence = WildlifeLicence.objects.create(current_application=application, proxy_applicant_id=applicant_id, submitter=application.submitter,
                          licence_type=activity, licence_class=licence_class)

    #elif application.applicant_type == Application.APPLICANT_TYPE_SUBMITTER:
    else: # assume applicant is the submitter
        qs_licence = WildlifeLicence.objects.filter(submitter_id=application.applicant_id, org_applicant__isnull=True, proxy_applicant__isnull=True, licence_class=licence_class)
        if qs_licence.exists():
            #licence_sequence = qs_licence.last().licence_sequence + 1 if qs_licence.filter(licence_type=activity).exists() else qs_licence.last().licence_sequence
            licence_sequence = qs_licence.last().licence_sequence + 1 if new_app else qs_licence.last().licence_sequence
            # use existing licence, just increment sequence_number
            licence = WildlifeLicence.objects.create(
                licence_number=qs_licence.last().licence_number,
                #licence_sequence=qs_licence.last().licence_sequence + 1,
                licence_sequence=licence_sequence,
                current_application=application,
                submitter_id=application.applicant_id,
                licence_type=activity,
                 licence_class=licence_class
            )
        else:
            licence = WildlifeLicence.objects.create(current_application=application, submitter_id=application.applicant_id, licence_type=activity, licence_class=licence_class)

    return licence

def all_related_licences(application):
    licence_number = application.licences.all().last().licence_number
    return WildlifeLicence.objects.filter(licence_number=licence_number).order_by('id')

def all_related_applications(application):
    app_ids = WildlifeLicence.objects.filter(licence_number=application.licences.all().last().licence_number).values_list('current_application_id', flat=True).distinct()
    return Application.objects.filter(id__in=app_ids).order_by('id')

def pdflatex(request, application):

    now = timezone.localtime(timezone.now())
    report_date = now

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
        "cover_page": "Cover Page",
        "licence": "Licence",
    }
    embed = False if request.GET.get("embed") == "false" else True

    context = {
        'user': request.user.get_full_name(),
        'report_date': report_date.strftime('%e %B %Y').strip(),
        'time': report_date.strftime('%H:%M'),
#        'form': form_data,
        'application': application,
        'licences': all_related_licences(application),
        'embed': embed,
        'headers': request.GET.get("headers", True),
        'title': request.GET.get("title", "Wildlife Licensing System"),
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
    directory = os.path.join(settings.MEDIA_ROOT, 'wildlife_compliance_licence' + os.sep + str(application.id) + os.sep)
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


    #licence_pdf = ApplicationDocument.objects.create(application=application, _file='licence_pdf', can_delete=False)
#    licence_pdf = ApplicationDocument.objects.create(application=application can_delete=False)
    #licence_pdf.save(new_name, File(f))
#    licence_pdf.save(filename, File( open(directory + filename).read() ))
    #licence_pdf.save(filename, ContentFile( open(directory + filename).read() ))
    logger.debug("Reading PDF output from {}".format(filename))
    #response.write(open(directory + filename).read())
    #logger.debug("Finally: returning PDF response.")
    #return response


