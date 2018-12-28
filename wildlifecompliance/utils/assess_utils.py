from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from collections import OrderedDict
from wildlifecompliance.components.applications.models import Application, ApplicationType, ApplicationActivityType
from wildlifecompliance.components.licences.models import DefaultActivityType, WildlifeLicence, WildlifeLicenceClass, WildlifeLicenceActivity
from wildlifecompliance.components.organisations.models import Organisation
from ledger.accounts.models import OrganisationAddress
from django.contrib.postgres.fields.jsonb import JSONField
from wildlifecompliance.utils import SearchUtils, search_multiple_keys
from wildlifecompliance.components.licences.models import DefaultActivity
from ledger.accounts.models import EmailUser

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
    import ipdb; ipdb.set_trace()
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


