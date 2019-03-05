from __future__ import unicode_literals

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from collections import OrderedDict
from wildlifecompliance.components.applications.models import (
    Application,
    ApplicationSelectedActivity
)
from wildlifecompliance.components.licences.models import (
    DefaultActivity,
    WildlifeLicence,
    LicenceCategory,
    LicencePurpose
)
from wildlifecompliance.utils import SearchUtils, search_multiple_keys
from django.utils import timezone

import logging
import os
import re
import subprocess

from datetime import date

logger = logging.getLogger(__name__)


def replace_special_chars(input_str, new_char='_'):
    return re.sub('[^A-Za-z0-9]+', new_char, input_str).strip('_').lower()


def get_purposes(licence_category_short_name):
    """
        activity --> purpose

        for licence_category in DefaultActivity.objects.filter(licence_category_id=13):
            #print '{} {}'.format(licence_category.licence_category.id, licence_category.licence_category.name)
            for activity in DefaultPurpose.objects.filter(activity_id=licence_category.activity_id):
                print '    {}'.format(activity.activity.name, activity.activity.short_name)
        ____________________

        DefaultActivity.objects.filter(licence_category__short_name='Flora Other Purpose').values_list(
            'licence_category__activity__purpose__name', flat=True).distinct()
    """
    activity = DefaultActivity.objects.filter(
        licence_category__short_name=licence_category_short_name
    ).order_by('licence_category__activity__purpose__name')
    return activity.values_list('licence_category__activity__purpose__name', flat=True).distinct()


def create_app_activity_model(licence_category, app_ids=[], exclude_app_ids=[]):
    """
    from wildlifecompliance.utils.excel_utils import write_excel_model
    write_excel_model('Fauna Other Purpose')
    """

    if app_ids:
        # get a filterset with single application
        applications = Application.objects.filter(id__in=app_ids)
    else:
        # applications = Application.objects.filter(licence_category=licence_category).exclude(
        # processing_status=Application.PROCESSING_STATUS_DRAFT[0]).exclude(id__in=cur_app_ids)
        applications = Application.objects.filter(licence_category=licence_category).exclude(id__in=exclude_app_ids)

    obj_list = []
    for application in applications.order_by('id'):

        activities = get_purposes(application.licence_type_data['short_name']).values_list('activity__short_name', flat=True)
        for activity in application.licence_type_data['activity']:
            if activity['short_name'] in list(activities):
                activity_obj = LicencePurpose.get_first_record(activity['purpose'][0]['name'])
                app_activity, created = ApplicationSelectedActivity.objects.get_or_create(
                    application=application,
                    licence_activity__id=activity_obj.id
                )
                obj_list.append(app_activity)

    return obj_list


def create_licence(application, activity, new_app):
    """ activity_name='Importing Fauna (Non-Commercial)'
        licence_category ='Flora Other Purpose'
    """
    licence = None
    activity = LicencePurpose.get_first_record(activity.activity_name)
    licence_category = LicenceCategory.objects.get(short_name=application.licence_category)
    if application.applicant_type == Application.APPLICANT_TYPE_ORGANISATION:
        qs_licence = WildlifeLicence.objects.filter(org_applicant_id=application.applicant_id, licence_category=licence_category)
        if qs_licence.exists():
            # licence_sequence = qs_licence.last().licence_sequence + 1 if qs_licence.filter(
            # licence_type=activity).exists() else qs_licence.last().licence_sequence
            licence_sequence = qs_licence.last().licence_sequence + 1 if new_app else qs_licence.last().licence_sequence
            # use existing licence, just increment sequence_number
            licence = WildlifeLicence.objects.create(
                licence_number=qs_licence.last().licence_number,
                # licence_sequence=qs_licence.last().licence_sequence + 1,
                licence_sequence=licence_sequence,
                current_application=application,
                org_applicant_id=application.applicant_id,
                submitter=application.submitter,
                licence_type=activity,
                licence_category=licence_category,
                expiry_date=activity.expiry_date,
                issue_date=activity.issue_date,
                start_date=activity.start_date
            )
        else:
            licence = WildlifeLicence.objects.create(
                current_application=application,
                org_applicant_id=application.applicant_id,
                submitter=application.submitter,
                licence_type=activity,
                licence_category=licence_category,
                expiry_date=activity.expiry_date,
                issue_date=activity.issue_date,
                start_date=activity.start_date
            )

    elif application.applicant_type == Application.APPLICANT_TYPE_PROXY:
        qs_licence = WildlifeLicence.objects.filter(proxy_applicant_id=application.applicant_id, licence_category=licence_category)
        if qs_licence.exists():
            # licence_sequence = qs_licence.last().licence_sequence + 1 if qs_licence.filter(
            # licence_type=activity).exists() else qs_licence.last().licence_sequence
            licence_sequence = qs_licence.last().licence_sequence + 1 if new_app else qs_licence.last().licence_sequence
            # use existing licence, just increment sequence_number
            licence = WildlifeLicence.objects.create(
                licence_number=qs_licence.last().licence_number,
                # licence_sequence=qs_licence.last().licence_sequence + 1,
                licence_sequence=licence_sequence,
                current_application=application,
                proxy_applicant_id=application.applicant_id,
                submitter=application.submitter,
                licence_type=activity,
                licence_category=licence_category,
                expiry_date=activity.expiry_date,
                issue_date=activity.issue_date,
                start_date=activity.start_date
            )
        else:
            licence = WildlifeLicence.objects.create(
                current_application=application,
                proxy_applicant_id=application.applicant_id,
                submitter=application.submitter,
                licence_type=activity,
                licence_category=licence_category,
                expiry_date=activity.expiry_date,
                issue_date=activity.issue_date,
                start_date=activity.start_date
            )

    # elif application.applicant_type == Application.APPLICANT_TYPE_SUBMITTER:
    else:  # assume applicant is the submitter
        qs_licence = WildlifeLicence.objects.filter(submitter_id=application.applicant_id, org_applicant__isnull=True,
                                                    proxy_applicant__isnull=True, licence_category=licence_category)
        if qs_licence.exists():
            # licence_sequence = qs_licence.last().licence_sequence + 1 if qs_licence.filter(
            # licence_type=activity).exists() else qs_licence.last().licence_sequence
            licence_sequence = qs_licence.last().licence_sequence + 1 if new_app else qs_licence.last().licence_sequence
            # use existing licence, just increment sequence_number
            licence = WildlifeLicence.objects.create(
                licence_number=qs_licence.last().licence_number,
                # licence_sequence=qs_licence.last().licence_sequence + 1,
                licence_sequence=licence_sequence,
                current_application=application,
                submitter_id=application.applicant_id,
                licence_type=activity,
                licence_category=licence_category,
                expiry_date=activity.expiry_date,
                issue_date=activity.issue_date,
                start_date=activity.start_date
            )
        else:
            licence = WildlifeLicence.objects.create(
                current_application=application,
                submitter_id=application.applicant_id,
                licence_type=activity,
                licence_category=licence_category,
                expiry_date=activity.expiry_date,
                issue_date=activity.issue_date,
                start_date=activity.start_date
            )

    return licence


def all_related_licences(application):
    licence_number = application.licences.all().last().licence_number
    return WildlifeLicence.objects.filter(licence_number=licence_number, expiry_date__gte=date.today()).order_by('id')


def all_related_applications(application):
    app_ids = WildlifeLicence.objects.filter(licence_number=application.licences.all().last().licence_number).values_list(
        'current_application_id', flat=True
    ).distinct()
    return Application.objects.filter(id__in=app_ids).order_by('id')


def get_activity_sys_questions(activity_name):
    """
    Looks up the activity schema and return all questions (marked isEditable) that need to be added to the Excel WB.
    Allows us to know the block size for each activity in the WB (start_col, end_col)
    """
    ordered_dict = OrderedDict([])

    schema = LicencePurpose.get_first_record(activity_name).schema
    res = search_multiple_keys(schema, 'isEditable', ['name', 'label', 'type', 'headers'])
    for i in res:
        if 'headers' in i:
            ordered_dict.update([(i['name'], {'type': i['type'], 'label':i['label'], 'headers':i['headers']})])
        else:
            ordered_dict.update([(i['name'], {'type': i['type'], 'label':i['label']})])

    return ordered_dict


def get_tab_index(activity):
    application = activity.application
    activity_name = activity.name  # 'Fauna Other - Importing'
    return application.data[0][activity_name][0].keys()[0].split('_')[1]


def get_activity_sys_answers(activity):
    """
    Looks up the activity return all answers for question marked isEditable that need to be added to the Excel WB.

    get_activity_sys_answers(ApplicationSelectedActivity.objects.get(id=50))
    """
    ordered_dict = OrderedDict([])
    if activity:
        questions = get_activity_sys_questions(activity.activity_name)
        for k, v in questions.iteritems():
            # k - section name
            # v - question

            # must append tab index to 'section name'
            k = k + '_' + get_tab_index(activity)
            s = SearchUtils(activity.application)
            answer = s.search_value(k)
            v.update({'answer': answer})
            ordered_dict.update(OrderedDict([(k, v)]))

    return ordered_dict


def pdflatex(request, application):

    now = timezone.localtime(timezone.now())
    report_date = now

    template = "wildlife_licence"
    response = HttpResponse(content_type='application/pdf')
    texname = template + ".tex"
    filename = template + ".pdf"
    # timestamp = now.isoformat().rsplit(
    #    ".")[0].replace(":", "")
    if template == "wildlife_licence":
        downloadname = "wildlife_licence_" + report_date.strftime('%Y-%m-%d') + ".pdf"
    else:
        downloadname = "wildlife_licence_" + template + "_" + report_date.strftime('%Y-%m-%d') + ".pdf"
    error_response = HttpResponse(content_type='text/html')
    errortxt = downloadname.replace(".pdf", ".errors.txt.html")
    error_response['Content-Disposition'] = (
        '{0}; filename="{1}"'.format("inline", errortxt)
    )

    subtitles = {
        "cover_page": "Cover Page",
        "licence": "Licence",
    }
    embed = False if request.GET.get("embed") == "false" else True

    context = {
        'user': request.user.get_full_name(),
        'report_date': report_date.strftime('%e %B %Y').strip(),
        'time': report_date.strftime('%H:%M'),
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
    response['Content-Disposition'] = (
        '{0}; filename="{1}"'.format(
            disposition, downloadname))

    url = os.path.join('applications' + os.sep + str(application.id) + os.sep + 'wildlife_licence' + os.sep)
    directory = os.path.join(
        settings.MEDIA_ROOT + os.sep + 'applications' + os.sep + str(
            application.id) + os.sep + 'wildlife_licence' + os.sep
    )
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

        error_response.write(err_msg + "\n\n{0}\n\n{1}".format(e, traceback.format_exc()))
        return error_response

    with open(directory + texname, "w") as f:
        f.write(output.encode('utf-8'))
        logger.debug("Writing to {}".format(directory + texname))

    logger.debug("Starting PDF rendering process ...")
    cmd = ['latexmk', '-cd', '-f', '-silent', '-pdf', directory + texname]
    # cmd = ['latexmk', '-cd', '-f', '-pdf', directory + texname]
    logger.debug("Running: {0}".format(" ".join(cmd)))
    subprocess.call(cmd)

    logger.debug("Cleaning up ...")
    cmd = ['latexmk', '-cd', '-c', directory + texname]
    logger.debug("Running: {0}".format(" ".join(cmd)))
    subprocess.call(cmd)

    application.pdf_licence.name = url + filename
    application.pdf_licence._file = url + filename
    application.save()

    logger.debug("Reading PDF output from {}".format(filename))
    # response.write(open(directory + filename).read())
    # logger.debug("Finally: returning PDF response.")
    # return response
