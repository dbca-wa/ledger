from __future__ import unicode_literals

from django.conf import settings
from collections import OrderedDict
from wildlifecompliance.components.applications.models import Application, ApplicationType
from wildlifecompliance.components.licences.models import DefaultActivityType, WildlifeLicenceClass
from wildlifecompliance.components.organisations.models import Organisation
from ledger.accounts.models import OrganisationAddress
from django.contrib.postgres.fields.jsonb import JSONField

import xlrd, xlwt
import os

import logging
logger = logging.getLogger(__name__)


import json
import datetime
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


class ExcelApplication(models.Model):
    application = models.ForeignKey(Application, related_name='excel_applications')
    data = JSONField(blank=True, null=True)

    @property
    def licence_class(self):
        #return self.application.licence_class
        return self.application.licence_type_short_name

    @property
    def lodgement_number(self):
        return self.application.lodgement_number

    @property
    def licence_number(self):
        return self.application.licence_number

    @property
    def applicant(self):
        return self.application.applicant

    @property
    def applicant_block(self):
        return '{}\n{}'.format(self.applicant, OrganisationAddress.objects.get(organisation__name=self.applicant.name).__str__())


class ExcelActivityType(models.Model):
    excel_app = models.ForeignKey(ExcelApplication, related_name='excel_activity_types')
    short_name = models.CharField(max_length=24, blank=True)
    data = JSONField(blank=True, null=True)
    conditions = models.TextField(blank=True, null=True)
    issue_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    issued = models.NullBooleanField(default=None)
    processed = models.NullBooleanField(default=None)

    class Meta:
        unique_together = (('excel_app','short_name'))
        app_label = 'wildlifecompliance'

#    def save(self, *args, **kwargs):
#        super(ExcelActivityType, self).save(*args, **kwargs)
#        if self.short_name == '':
#           self.short_name = self.excel_app.licence_class
#            self.save()

#   @property
#   def short_name(self):
#       return self.activity_type.short_name

def write_excel_model(ids=[125]):
    applications = Application.objects.filter(id__in=ids)

    for application in applications:
        excel_app, created = ExcelApplication.objects.get_or_create(application=application)

        activities = get_purposes(a.licence_type_data['short_name']).values_list('activity_type__short_name', flat=True)
        for activity_type in a.licence_type_data['activity_type']:
            if activity_type['short_name'] in list(activities):
                excel_activity_type, created = ExcelActivityType.objects.get_or_create(
                    excel_app=excel_app,
                    short_name=activity_type['short_name']
                )

def write_excel_model_test(ids=[125]):
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

def write_workbook(request):
    filename = 'wc_apps_{}.xls'.format(datetime.now().strftime('%Y%m%dT%H%M%S'))

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Applications')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    applications = Application.objects.filter(id__in=[125])

    for application in applications:
        s=serialize_export(application)


        columns = unique_column_names()
        names = [row['name'] for row in s]
        row_num += 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)


        keys = [row['key'] for row in s]

#activity = [row['activity'] for row in s]
#purpose = [row['purpose'] for row in s]
        labels = [row['label'] for row in s]
        for col_num in range(len(keys)):
            ws.write(row_num, col_num, keys[col_num], font_style)

        row_num += 1
        for col_num in range(len(keys)):
            ws.write(row_num, col_num, activity[col_num], font_style)

        row_num += 1
        for col_num in range(len(keys)):
            ws.write(row_num, col_num, purpose[col_num], font_style)

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

