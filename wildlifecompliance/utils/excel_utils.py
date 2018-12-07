from __future__ import unicode_literals

from django.conf import settings
from collections import OrderedDict
from wildlifecompliance.components.applications.models import Application, ApplicationType, ExcelApplication, ExcelActivityType
from wildlifecompliance.components.licences.models import DefaultActivityType, WildlifeLicenceClass, WildlifeLicenceActivity
from wildlifecompliance.components.organisations.models import Organisation
from ledger.accounts.models import OrganisationAddress
from django.contrib.postgres.fields.jsonb import JSONField
from wildlifecompliance.utils import SearchUtils
from wildlifecompliance.components.licences.models import DefaultActivity

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell, xl_cell_to_rowcol, xl_col_to_name
import xlrd#, xlwt
import os
import re

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
    """
    from wildlifecompliance.utils.excel_utils import write_excel_model
    write_excel_model('Fauna Other Purpose')
    """

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

#def create_activity_type_fields(activity_type):
#    """
#    from wildlifecompliance.utils.excel_utils import create_activity_type_fields
#    create_activity_type_fields('Importing Fauna (Non-Commercial)')
#    --> OrderedDict([(u'species', u'species a details'), (u'number_of_animals', u'1')])
#    """
#    ordered_dict=OrderedDict([])
#
#    try:
#        fields = WildlifeLicenceActivity.objects.get(name=activity_type.activity_name).fields
#        if isinstance(fields, dict):
#            for k,v in fields.iteritems():
#                # k - section name
#                # v - question
#                s = SearchUtils(activity_type.application)
#                answer = s.search_value(k)
#                ordered_dict.update(OrderedDict([(v,answer)]))
#    except AttributeError:
#        pass
#
#    return ordered_dict

def create_activity_type_fields(qs_activity_type, activity_name):
    """
    from wildlifecompliance.utils.excel_utils import create_activity_type_fields
    create_activity_type_fields('Importing Fauna (Non-Commercial)')
    --> OrderedDict([(u'species', u'species a details'), (u'number_of_animals', u'1')])

    ________________________________

	c=WildlifeLicenceClass.objects.get(short_name='Fauna Other Purpose')

	In [4]: c.short_name
	Out[4]: u'Fauna Other Purpose'


	for i in DefaultActivityType.objects.filter(licence_class__name=c.name):  	--> Maps licence class to activity_type
		...:     print i.activity_type_id, i

	16 Fauna (Other Purposes) Licence - Fauna Other - Taking
	17 Fauna (Other Purposes) Licence - Fauna Other - Disturbing
	18 Fauna (Other Purposes) Licence - Fauna Other - Possessing
	19 Fauna (Other Purposes) Licence - Fauna Other - Importing
	20 Fauna (Other Purposes) Licence - Fauna Other - Exporting

	{'activity_type_id': 20,
	 'id': 21,
	 'licence_class_id': 2}

	____________________________________


	DefaultActivity.objects.get(activity_type_id=19).__dict__
	Out[117]:
	{'_state': <django.db.models.base.ModelState at 0x7f0c4f66c090>,
	 'activity_id': 27,
	 'activity_type_id': 19,
	 'id': 28}

	In [112]: WildlifeLicenceActivity.objects.get(id=27)
	Out[112]: <WildlifeLicenceActivity: Importing Fauna (Non-Commercial)>

	WildlifeLicenceActivity.objects.get(id=27).fields
	Out[120]: {u'Species1-1_0': u'species', u'Species1-2_0': u'number_of_animals'}

    """
    ordered_dict=OrderedDict([])

    try:
        fields = WildlifeLicenceActivity.objects.get(name=activity_name).fields
        if isinstance(fields, dict):
            for k,v in fields.iteritems():
                # k - section name
                # v - question
                if qs_activity_type:
                    #if activity_name == 'Importing Fauna (Non-Commercial)':
                    #    import ipdb; ipdb.set_trace()
                    s = SearchUtils(qs_activity_type[0].application)
                    answer = s.search_value(k)
                    ordered_dict.update(OrderedDict([(v,answer)]))
                else:
                    # this part for the Excel column  headers
                    ordered_dict.update(OrderedDict([(v,None)]))

    except AttributeError:
        pass

    return ordered_dict

def write_excel_model_test(ids=[145]):
    applications = Application.objects.filter(id__in=ids)

    for application in applications:
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

def _get_purposes(licence_class_short_name):
    """ Return the purposes mapped to a given category/licence class short_name """
    licence_class =  WildlifeLicenceClass.objects.get(short_name=licence_class_short_name)
    return DefaultActivityType.objects.filter(licence_class=licence_class).order_by('id')

def replace_special_chars(input_str, new_char='_'):
    return re.sub('[^A-Za-z0-9]+', new_char, input_str)

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

def _read_workbook(input_filename):
    """
    Read the contents of input_filename and return
    :param logger:         The logger
    :param input_filename: Filepath of the spreadsheet to read
    :return:  Dict of response sets
    """
    wb_response_sets = {}
    if os.path.isfile(input_filename):
        wb = xlrd.open_workbook(input_filename)
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

def read_workbook(input_filename):
    """
    Read the contents of input_filename and return
    :param logger:         The logger
    :param input_filename: Filepath of the spreadsheet to read
    :return:  Dict of response sets
    """
    wb_response_sets = {}
    meta = {}
    if os.path.isfile(input_filename):
        wb = xlrd.open_workbook(input_filename)
        sh = wb.sheet_by_name('Applications')
        sh_meta = wb.sheet_by_name('Meta')

        # Read Meta
        number_of_rows = sh_meta.nrows
        hdr = sh_meta.row_values(0)
        for row in range(1, number_of_rows):
            row_values = sh_meta.row_values(row)
            purpose = row_values[0]
            meta[purpose] = {}
            for i in zip(hdr, row_values)[1:]:
                meta[purpose].update( {i[0]: i[1]} )

    return meta
#        for row in range(0, number_of_rows):
#            if sheet.cell(row, 0).value != "":
#                label_object = {
#                    'label': sheet.cell(row, 0).value,
#                }
#                wb_response_sets[name].append(label_object)
#
#
#        for sheet in wb.sheets():
#            name = sheet.name
#            wb_response_sets[name] = []
#
#            number_of_rows = sheet.nrows
#            for row in range(1, number_of_rows):
#                if sheet.cell(row, 0).value != "":
#                    label_object = {
#                        'label': sheet.cell(row, 0).value,
#                    #}
#                    wb_response_sets[name].append(label_object)
#        return wb_response_sets
#    else:
#        logger.error('{0} does not appear to be a valid file'.format(input_filename))


def cols_common(qs_activity_type, activity_name):
    code = activity_name[:2].lower()
    ordered_dict = OrderedDict([
        ('{}_cover_processed'.format(code), None),
        ('{}_cover_processed_date'.format(code), None),
        ('{}_cover_processed_by'.format(code), None),
        ('{}_conditions'.format(code), qs_activity_type[0].conditions if qs_activity_type else None),
        ('{}_issue_date'.format(code), qs_activity_type[0].issue_date if qs_activity_type else None),
        ('{}_start_date'.format(code), qs_activity_type[0].start_date if qs_activity_type else None),
        ('{}_expiry_date'.format(code), qs_activity_type[0].expiry_date if qs_activity_type else None),
        ('{}_issued'.format(code), qs_activity_type[0].issued if qs_activity_type else None),
        ('{}_processed'.format(code), qs_activity_type[0].processed if qs_activity_type else None),
    ])
    return ordered_dict

def cols_output(qs_activity_type, activity_name):
    """
    excel_app = ExcelApplication.objects.all().last()
    activity_type = excel_app.excel_activity_types.filter(activity_name='Importing Fauna (Non-Commercial)')[0]
    cols_output(activity_type, 'Importing', 'Importing Fauna (Non-Commercial)')
    """
    #if short_name=='Importing':
    #    import ipdb; ipdb.set_trace()
    ordered_dict = OrderedDict([
        ('{}'.format(activity_name), None),
    ])
    ordered_dict.update(create_activity_type_fields(qs_activity_type, activity_name))
    ordered_dict.update(cols_common(qs_activity_type, activity_name))
    return ordered_dict


def write_workbook(licence_category='Flora Industry'):
    """
    from wildlifecompliance.utils.excel_utils import write_workbook, write_excel_model
    write_excel_model('Fauna Other Purpose')
    write_workbook('Fauna Other Purpose')
    """
    #filename = '/tmp/wc_apps_{}.xls'.format(datetime.now().strftime('%Y%m%dT%H%M%S'))
    excel_apps = ExcelApplication.objects.filter(application__licence_category=licence_category).order_by('application_id') #filter(id__in=ids)

    filename = '/tmp/wc_apps_{}.xlsx'.format(licence_category.lower().replace(' ','_'))
    sheet_name = 'Applications'

    wb = xlsxwriter.Workbook(filename)
    ws = wb.add_worksheet(sheet_name)
    ws_meta = wb.add_worksheet('Meta')

    bold = wb.add_format({'bold': True})
    unlocked = wb.add_format({'locked': 0})
    locked = wb.add_format({'locked': 1})
    wrap = wb.add_format({'text_wrap': True})
    unlocked_wrap = wb.add_format({'text_wrap': True, 'locked': False})
    integer = wb.add_format({'num_format': '0', 'align': 'center'})

    #ws.set_column('E:DW', None, unlocked)
    ws.set_column('A:XDF', None, unlocked)
    ws.protect()

    # Sheet header, first row
    row_num = 0

    # Header
    excel_app = excel_apps.last()
    licence_class = excel_app.application.licence_type_data['short_name']
    #short_name_list = get_purposes(licence_class).values_list('activity_type__short_name', flat=True)
    activity_name_list = get_purposes(licence_class)#[:2]
    col_num = 0
    for k,v in excel_app.cols_output.iteritems():
        #ws.write(row_num, col_num, k, font_style)
        ws.write(row_num, col_num, k, bold)
        col_num += 1

    for activity_name in activity_name_list:
        #activity_type = excel_app.excel_activity_types.filter(activity_name=activity_name)
        #import ipdb; ipdb.set_trace()
        activity_type_cols = cols_output(None, activity_name).keys()

        ws.write(row_num, col_num, '', bold); col_num += 1
        #ws.write(row_num, col_num, short_name, bold); col_num += 1

        for col_name in activity_type_cols:
            ws.write(row_num, col_num, col_name, bold)
            col_num += 1

    # Application data
    cell_dict = {}
    row_start = row_num + 1
    for excel_app in excel_apps:
        row_num += 1
        col_num = 0
        cell_start = xl_rowcol_to_cell(row_start, col_num, row_abs=True, col_abs=True)
        for k,v in excel_app.cols_output.iteritems():
            ws.write(row_num, col_num, v, locked)
            col_num += 1

        cell_end = xl_rowcol_to_cell(row_num, col_num-1, row_abs=True, col_abs=True)
        cell_dict.update({'System': [cell_start, cell_end]})

        for activity_name in activity_name_list:
            #import ipdb; ipdb.set_trace()

            ws.write(row_num, col_num, ''); col_num += 1

            cell_start = xl_rowcol_to_cell(row_start, col_num, row_abs=True, col_abs=True)
            activity_type = excel_app.excel_activity_types.filter(activity_name=activity_name)
            activity_type_cols = cols_output(activity_type, activity_name)

            col_start = col_num
            if activity_type.exists():
                #import ipdb; ipdb.set_trace()
                for k,v in activity_type_cols.iteritems():
                    #ws.write('B1', 'Here is\nsome long text\nthat\nwe wrap',      wrap)
                    ws.write(row_num, col_num, v, unlocked_wrap)
                    col_num += 1
            else:
                # create a blank activity_type bilock
                for _ in activity_type_cols.keys():
                    ws.write(row_num, col_num, '', unlocked)
                    col_num += 1

            cell_end = xl_rowcol_to_cell(row_num, col_num-1, row_abs=True, col_abs=True)
            cell_dict.update({activity_name: [cell_start, cell_end]})

    #ws.write('F2:O3', '=Taking')
    #wb.define_name('Application', '=Sheet1!$F$2:$O$14')

    # Write the named ranges and Meta data
    row_num = 0
    col_num = 0
    wb.define_name('{0}!{1}'.format(sheet_name, 'System'), '={0}!{1}:{2}'.format(sheet_name, cell_dict['System'][0], cell_dict['System'][1]))
    # Hdr
    ws_meta.write(row_num, col_num, 'Purpose')
    ws_meta.write(row_num, col_num+1, 'Start Cell')
    ws_meta.write(row_num, col_num+2, 'End Cell')
    ws_meta.write(row_num, col_num+3, 'First Row')
    ws_meta.write(row_num, col_num+4, 'Last Row')
    ws_meta.write(row_num, col_num+5, 'First Col')
    ws_meta.write(row_num, col_num+6, 'Last Col')

    # System
    ws_meta.write(row_num+1, col_num, 'System')
    ws_meta.write(row_num+1, col_num+1, cell_dict['System'][0])
    ws_meta.write(row_num+1, col_num+2, cell_dict['System'][1])
    ws_meta.write(row_num+1, col_num+3, xl_cell_to_rowcol(cell_dict['System'][0])[0])
    ws_meta.write(row_num+1, col_num+4, xl_cell_to_rowcol(cell_dict['System'][1])[0])
    ws_meta.write(row_num+1, col_num+5, xl_cell_to_rowcol(cell_dict['System'][0])[1])
    ws_meta.write(row_num+1, col_num+6, xl_cell_to_rowcol(cell_dict['System'][1])[1])
    #import ipdb; ipdb.set_trace()

    # Purposes
    width = 20
    for row_num, activity_name in enumerate(activity_name_list, start=2):
        #wb.define_name('Applications!Taking', '=Applications!$F$2:$O$3')
        #activity_name2 = replace_special_chars(activity_name)
        wb.define_name('{0}!{1}'.format(sheet_name, replace_special_chars(activity_name)), '={0}!{1}:{2}'.format(sheet_name, cell_dict[activity_name][0], cell_dict[activity_name][1]))
        ws_meta.write(row_num, col_num, activity_name)
        ws_meta.write(row_num, col_num+1, cell_dict[activity_name][0])
        ws_meta.write(row_num, col_num+2, cell_dict[activity_name][1])
        ws_meta.write(row_num, col_num+3, xl_cell_to_rowcol(cell_dict[activity_name][0])[0])
        ws_meta.write(row_num, col_num+4, xl_cell_to_rowcol(cell_dict[activity_name][1])[0])
        ws_meta.write(row_num, col_num+5, xl_cell_to_rowcol(cell_dict[activity_name][0])[1])
        ws_meta.write(row_num, col_num+6, xl_cell_to_rowcol(cell_dict[activity_name][1])[1])
        width = len(activity_name) if len(activity_name) > width else width

    import ipdb; ipdb.set_trace()
    #  lock the System App Data section only
    #ws.protect()
    #ws.set_column('{}:{}'.format(xl_col_to_name(0), xl_col_to_name(xl_cell_to_rowcol(cell_dict['System'][1])[1])), None, locked)
    #ws.set_column('{}:AMJ'.format(xl_col_to_name(xl_cell_to_rowcol(cell_dict['System'][1])[1] + 1)), None, unlocked)
    #ws.set_column('E:DW', None, unlocked)


    #  lock  the Meta Sheet (mostly)
    ws_meta.set_column('D:G', 13, integer )
    ws_meta.set_column('A:Z', None, locked)
    ws_meta.protect()
    ws_meta.set_column(0, 0, width)


    wb.close()
    #return wb
    return cell_dict

