from __future__ import unicode_literals

from django.conf import settings
from collections import OrderedDict
from wildlifecompliance.components.applications.models import Application, ApplicationType, ExcelApplication, ExcelActivityType
from wildlifecompliance.components.licences.models import DefaultActivityType, WildlifeLicenceClass, WildlifeLicenceActivity
from wildlifecompliance.components.organisations.models import Organisation
from ledger.accounts.models import OrganisationAddress
from django.contrib.postgres.fields.jsonb import JSONField

import xlrd, xlwt
import os

import logging
logger = logging.getLogger(__name__)


import json
from datetime import datetime
from django.db import models



def test(ids=[125]):
    a=Application.objects.get(id__in=ids)
    applicant = '{}\n{}'.format(a.applicant, OrganisationAddress.objects.get(organisation__name=a.applicant).__str__())
    licence_class = a.licence_type_data['short_name']

    purposes = get_purposes(licence_class)

    #d2 = OrderedDict([(purpose.short_name, d)])

    applicantion_details = OrderedDict([('Application',a.lodgement_number), ('ID',a.id), ('Licence',a.licence), ('Applicant',applicant)])

    d2 = OrderedDict([])
    d2.update([('application_details', applicant_details)])
    for purpose in purposes:
        #import ipdb; ipdb.set_trace()
        d = OrderedDict([('Application',a.lodgement_number), ('ID',a.id), ('Licence',a.licence), ('Applicant',applicant), ('sys_field1','sys_field1'), ('sys_field2','sys_field2'), ('short_name','TA'), ('conditions','c1'), ('issue_date','01-01-2019')])
        d2.update([(purpose.activity_type.short_name, d)])

    return d2


#def write_excel_model(ids=[145]):
def write_excel_model(licence_category):
    applications = Application.objects.filter(licence_category=licence_category)
    #applications = Application.objects.filter(id__in=id)

    for application in applications:
        excel_app, created = ExcelApplication.objects.get_or_create(application=application)
        #excel_app.application.licence_type_data['short_name']

        activities = get_purposes(application.licence_type_data['short_name']).values_list('activity_type__short_name', flat=True)
        for activity_type in application.licence_type_data['activity_type']:
            if activity_type['short_name'] in list(activities):
                excel_activity_type, created = ExcelActivityType.objects.get_or_create(
                    excel_app=excel_app,
                    activity_name=activity_type['activity'][0]['name'],
                    name=activity_type['name'],
                    short_name=activity_type['short_name']
                )

def create_activity_type_fields(activity_name):
    """
    from wildlifecompliance.utils.excel_utils import create_activity_type_fields
    create_activity_type_fields('Importing Fauna (Non-Commercial)')
    {u'Species1-1_0': u'species', u'Species1-2_0': u'number_of_animals'}
    """
    fields = WildlifeLicenceActivity.objects.get(name=activity_name).fields

    ordered_dict=OrderedDict([])
    if isinstance(fields, dict):
        for k,v in fields.iteritems():
            ordered_dict.update(OrderedDict([(k,v)]))

    return ordered_dict
    

def write_excel_model_test(ids=[145]):
    applications = Application.objects.filter(id__in=ids)

    for application in applications:
        #excel_app, created = ExcelApplication.objects.get_or_create(application=application)

        activities = get_purposes(application.licence_type_data['short_name']).values_list('activity_type__short_name', flat=True)
        for activity_type in application.licence_type_data['activity_type']:
            if activity_type['short_name'] in list(activities):
                #excel_activity_type, created = ExcelActivityType.objects.get_or_create(
                #   excel_app=excel_app,
                #   short_name=activity_type['short_name']
                #)
                print application.licence_type_short_name, activity_type['short_name']



class ApplicationDetails():
    def __init__(self, application):
        self.licence_class = application.licence_class
        self.applicant = '{}\n{}'.format(application.applicant, OrganisationAddress.objects.get(organisation__name=application.applicant).__str__())
        self.lodgement_number = aplication.lodgement_number #rderedDict([('Application',a.lodgement_number), ('ID',a.id), ('Licence',a.licence), ('Applicant',applicant)])
        self.application_id = aplication.id
        self.licence_number = aplication.licence_number

    def __str__(self):
        return '{} - {}: {}'.format(self.lodgment_number, self.licence_class, self.applicant)

class ActivityType():
    conditions = None
    issue_date = None
    start_date = None
    expiry_date = None
    issued = None
    processed = None
    system_field1 = None
    system_field2 = None

    def __init__(self, short_name, code):
        #self.name = purpose.activity_type.short_name
        #self.code = purpose.activity_type.code
        self.name = short_name
        self.code = code

    def __str__(self):
        return '{} - {}'.format(self.name, self.code)

class Activity():

    def __init__(self, licence_type_data):
        """ licence_type_data --> application.licence_type_data['activity_type'] """

        self.licence_type_data = licence_type_data['activity_type']
        self.licence_class = licence_type_data['short_name']
        self.activity_types = OrderedDict([])

    def activity_types(self):
        """ Set the actvity type OrderedDict, including null placeholders for Activity Types not used """

        activities = get_purposes(a.licence_type_data['short_name']).values_list('activity_type__short_name', flat=True)
        for i in a.licence_type_data['activity_type']:
            if i['short_name'] in list(activities):
                activity_type = ActivityType(short_name, code)
                print i
            else:
                # create dummy place holder Activity
                pass


    def __str__(self):
        return '{}'.format(self.licence_class)



class ApplicationDetails():
    def __init__(application):
        self.applicant = '{}\n{}'.format(application.applicant, OrganisationAddress.objects.get(organisation__name=application.applicant).__str__())

def set_licence_category():
    for i in Application.objects.all():
        i.licence_category = i.licence_type_name.split(' - ')[0] if i.licence_type_name else None                                                                
        i.save()

def get_purposes(licence_class_short_name):
    """ Return the purposes mapped to a given category/licence class short_name """
    licence_class =  WildlifeLicenceClass.objects.get(short_name=licence_class_short_name)
    return DefaultActivityType.objects.filter(licence_class=licence_class).order_by('id')

def read_workbook(input_filename):
    """
    Read the contents of input_filename and return
    :param logger:         The logger
    :param input_filename: Filepath of the spreadsheet to read
    :return:  Dict of response sets
    """
    wb_response_sets = {}
    if os.path.isfile(input_filename):
        wb = open_workbook(input_filename)
        for sheet in wb.sheets():
            name = sheet.name
            wb_response_sets[name] = []

            number_of_rows = sheet.nrows
            for row in range(1, number_of_rows):
                if sheet.cell(row, 0).value != "":
                    label_object = {
                        'label': sheet.cell(row, 0).value,
                    }
                    wb_response_sets[name].append(label_object)
        return wb_response_sets
    else:
        logger.error('{0} does not appear to be a valid file'.format(input_filename))

def cols_fields(activity_type, short_name):
    #if short_name == 
    pass
    

def _cols_output(activity_type, short_name):
    code = short_name[:2].lower()
    ordered_dict = OrderedDict([
        ('{}'.format(short_name), None),
        ('{}_conditions'.format(code), activity_type[0].conditions if activity_type else None),
        ('{}_issue_date'.format(code), activity_type[0].issue_date if activity_type else None),
        ('{}_start_date'.format(code), activity_type[0].start_date if activity_type else None),
        ('{}_expiry_date'.format(code), activity_type[0].expiry_date if activity_type else None),
        ('{}_issued'.format(code), activity_type[0].issued if activity_type else None),
        ('{}_processed'.format(code), activity_type[0].processed if activity_type else None),
    ])
    return ordered_dict

def cols_common(activity_type, short_name):
    code = short_name[:2].lower()
    ordered_dict = OrderedDict([
        ('{}_cover_processed'.format(code), None),
        ('{}_cover_processed_date'.format(code), None),
        ('{}_cover_processed_by'.format(code), None),
        ('{}_conditions'.format(code), activity_type.conditions if activity_type else None),
        ('{}_issue_date'.format(code), activity_type.issue_date if activity_type else None),
        ('{}_start_date'.format(code), activity_type.start_date if activity_type else None),
        ('{}_expiry_date'.format(code), activity_type.expiry_date if activity_type else None),
        ('{}_issued'.format(code), activity_type.issued if activity_type else None),
        ('{}_processed'.format(code), activity_type.processed if activity_type else None),
    ])
    return ordered_dict


def cols_output(activity_type, short_name, activity_name):
    """
    excel_app = ExcelApplication.objects.all().last()
    activity_type = excel_app.excel_activity_types.filter(short_name='Exporting')[0]
    cols_output(activity_type, 'Importing', 'Importing Fauna (Non-Commercial)')
    """
    ordered_dict = OrderedDict([
        ('{}'.format(short_name), None),
    ])
    ordered_dict.update(create_activity_type_fields(activity_name))
    ordered_dict.update(cols_common(activity_type, short_name))
    return ordered_dict


def write_workbook(licence_category='Flora Industry'):
    #filename = '/tmp/wc_apps_{}.xls'.format(datetime.now().strftime('%Y%m%dT%H%M%S'))


    excel_apps = ExcelApplication.objects.filter(application__licence_category=licence_category).order_by('application_id') #filter(id__in=ids)
    filename = '/tmp/wc_apps_{}.xls'.format(licence_category.lower().replace(' ','_'))

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Applications')


    # Sheet header, first row
    row_num = 0

    # Header
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    excel_app = excel_apps.last()
    licence_class = excel_app.application.licence_type_data['short_name']
    short_name_list = get_purposes(licence_class).values_list('activity_type__short_name', flat=True)
    col_num = 0
    for k,v in excel_app.cols_output.iteritems():
        ws.write(row_num, col_num, k, font_style)
        col_num += 1

    #for activity_type in excel_app.excel_activity_types.all():
    for short_name in short_name_list:
        activity_type = excel_app.excel_activity_types.filter(short_name=short_name)
        activity_type_cols = cols_output(None, short_name).keys()

        ws.write(row_num, col_num, '', font_style); col_num += 1
        #ws.write(row_num, col_num, short_name, font_style); col_num += 1

        #for k,v in activity_type.cols_output.iteritems():
        for col_name in activity_type_cols:
            ws.write(row_num, col_num, col_name, font_style)
            col_num += 1

    # Application data
    font_style = xlwt.XFStyle()
    for excel_app in excel_apps:
        row_num += 1
        col_num = 0
        for k,v in excel_app.cols_output.iteritems():
            ws.write(row_num, col_num, v, font_style)
            col_num += 1

        for short_name in short_name_list:

            activity_type = excel_app.excel_activity_types.filter(short_name=short_name)
            activity_type_cols = cols_output(activity_type, short_name).keys()

            ws.write(row_num, col_num, '', font_style); col_num += 1
            #ws.write(row_num, col_num, short_name, font_style); col_num += 1
            if activity_type.exists():
                for k,v in activity_type[0].cols_output.iteritems():
                    #import ipdb; ipdb.set_trace()
                    ws.write(row_num, col_num, v, font_style)
                    col_num += 1
            else:
                # create a blank activity_type bilock
                for _ in activity_type_cols:
                    ws.write(row_num, col_num, '', font_style)
                    col_num += 1


    wb.save(filename)
    return wb

