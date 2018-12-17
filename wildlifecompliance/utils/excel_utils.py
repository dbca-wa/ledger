from __future__ import unicode_literals

from django.conf import settings
from collections import OrderedDict
from wildlifecompliance.components.applications.models import Application, ApplicationType, ExcelApplication, ExcelActivityType
from wildlifecompliance.components.licences.models import DefaultActivityType, WildlifeLicence, WildlifeLicenceClass, WildlifeLicenceActivity
from wildlifecompliance.components.organisations.models import Organisation
from ledger.accounts.models import OrganisationAddress
from django.contrib.postgres.fields.jsonb import JSONField
from wildlifecompliance.utils import SearchUtils, search_multiple_keys
from wildlifecompliance.components.licences.models import DefaultActivity
from ledger.accounts.models import EmailUser

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell, xl_cell_to_rowcol, xl_col_to_name
import xlrd#, xlwt
import openpyxl
import os
import re

import logging
logger = logging.getLogger(__name__)


import json
from datetime import datetime
from django.db import models


def test1(app_id=129):
    u=EmailUser.objects.get(email__icontains='jawaid.mushtaq')
    from wildlifecompliance.utils.excel_utils import create_activity_type_fields, cols_output, write_workbook, read_workbook, get_licence_type, get_applicant, get_applicant_details, get_applicant_org
    a=Application.objects.get(id=app_id)
    activity=WildlifeLicenceActivity.objects.get(name='Importing Fauna (Non-Commercial)')
    l=WildlifeLicence.objects.create(current_application=a, activity='', region='', tenure='', title='', org_applicant=a.org_applicant, submitter=u, licence_type=activity)
    return l

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

    applications = Application.objects.filter(licence_category=licence_category).exclude(processing_status=Application.PROCESSING_STATUS_DRAFT[0])
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


    for i in DefaultActivityType.objects.filter(licence_class__name=c.name):    --> Maps licence class to activity_type
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


APP_SHEET_NAME = 'Applications'
META_SHEET_NAME = 'Meta'
PATH = '/tmp'

class ExcelWriter():
    def __init__(self):
        pass

    def update_workooks(self):
        for licence_category in WildlifeLicenceClass.objects.all():
            #print i.short_name
            filename = '{}.xlsx'.format(self.replace_special_chars(licence_category.short_name))
            self.read_workbook(PATH + '/' + filename)

    def set_formats(self, workbook):
        self.bold = workbook.add_format({'bold': True})
        self.bold_unlocked = workbook.add_format({'bold': True, 'locked': False})
        self.unlocked = workbook.add_format({'locked': False})
        self.locked = workbook.add_format({'locked': True})
        self.wrap = workbook.add_format({'text_wrap': True})
        self.unlocked_wrap = workbook.add_format({'text_wrap': True, 'locked': False})
        self.integer = workbook.add_format({'num_format': '0', 'align': 'center'})

    def replace_special_chars(self, input_str, new_char='_'):
        return re.sub('[^A-Za-z0-9]+', new_char, input_str).strip('_').lower()

    def get_purposes(self, licence_class_short_name):
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

    def get_licence_type(self, activity_type_name):
        """
        activity_type name -- purpose name--> 'Importing Fauna (Non-Commercial)'
        """
        return DefaultActivityType.objects.filter(licence_class__activity_type__activity__name=activity_type_name).distinct('licence_class')[0].licence_class.name

    def get_applicant_org(self, applicant_name):
        """
        input:
            applicant_name = Application.objects.get(id=129).applicant --> 'Org1'
        """
        try:
            return Organisation.objects.get(organisation__name=applicant_name).organisation
        except:
            return None


    def get_applicant(self, applicant_name):
        """
        input:
            applicant_name = Application.objects.get(id=129).applicant --> 'Org1'
        """
        return self.get_applicant_org(applicant_name).name

    def get_applicant_details(self, applicant_name):
        """
        input:
            applicant_name = Application.objects.get(id=129).applicant --> 'Org1'
        """
        org = self.get_applicant_org(applicant_name)
        return '{} \n{}'.format(org.name, org.postal_address)

    def get_index(self, values_list, name):
        indices = [i for i, s in enumerate(values_list) if name in s]
        return indices[0] if indices else None

    def _create_activity_type_fields(self, qs_activity_type, activity_name):
        """
        from wildlifecompliance.utils.excel_utils import create_activity_type_fields
        create_activity_type_fields('Importing Fauna (Non-Commercial)')
        --> OrderedDict([(u'species', u'species a details'), (u'number_of_animals', u'1')])

        ________________________________

        c=WildlifeLicenceClass.objects.get(short_name='Fauna Other Purpose')

        In [4]: c.short_name
        Out[4]: u'Fauna Other Purpose'


        for i in DefaultActivityType.objects.filter(licence_class__name=c.name):    --> Maps licence class to activity_type
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
            import ipdb; ipdb.set_trace()
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

    def get_activity_type_sys_questions(self, activity_name):
        """
        Looks up the activity type schema and return all questions (marked isEditable) that need to be added to the Excel WB.
        Allows us to know the block size for each activity type in the WB (start_col, end_col)
        """
        ordered_dict=OrderedDict([])

        #import ipdb; ipdb.set_trace()
        schema = WildlifeLicenceActivity.objects.get(name=activity_name).schema
        res = search_multiple_keys(schema, 'isEditable', ['name', 'label'])

        #sys_fields = [ordered_dict.update([(i['name'],i['label'] + ' (' + i['name'] + ')')]) for i in res]
        #sys_fields = [ordered_dict.update([(i['label'] + ' (' + i['name'] + ')', None)]) for i in res]
        [ordered_dict.update([(i['name'],i['label'])]) for i in res]

        return ordered_dict

    def get_tab_index(self, qs_activity_type):
        application = qs_activity_type[0].application
        activity_name = qs_activity_type[0].name # 'Fauna Other - Importing'
        return application.data[0][activity_name][0].keys()[0].split('_')[1]

    def get_activity_type_sys_answers(self, qs_activity_type, activity_name):
        """
        Looks up the activity type return all answers for question marked isEditable that need to be added to the Excel WB.
        """
        ordered_dict=OrderedDict([])
        questions = self.get_activity_type_sys_questions(activity_name)
        for k,v in questions.iteritems():
            # k - section name
            # v - question

            if qs_activity_type:
                #import ipdb; ipdb.set_trace()
                # must append tab index to 'section name'
                k = k + '_' + self.get_tab_index(qs_activity_type) #, activity_name)
                s = SearchUtils(qs_activity_type[0].application)
                answer = s.search_value(k)
                ordered_dict.update(OrderedDict([(v,answer)]))
            else:
                # this part for the Excel column  headers
                ordered_dict.update(OrderedDict([(v,None)]))

        return ordered_dict



    def create_excel_model(self, licence_category, cur_app_ids):
        """
        from wildlifecompliance.utils.excel_utils import write_excel_model
        write_excel_model('Fauna Other Purpose')
        """

        applications = Application.objects.filter(licence_category=licence_category).exclude(processing_status=Application.PROCESSING_STATUS_DRAFT[0]).exclude(id__in=cur_app_ids)
        #applications = Application.objects.filter(id__in=id)

        #new_app_ids = []
        new_excel_apps = []
        for application in applications.order_by('id'):
            excel_app, created = ExcelApplication.objects.get_or_create(application=application)
            new_excel_apps.append(excel_app)

            activities = self.get_purposes(application.licence_type_data['short_name']).values_list('activity_type__short_name', flat=True)
            for activity_type in application.licence_type_data['activity_type']:
                if activity_type['short_name'] in list(activities):
                    excel_activity_type, created = ExcelActivityType.objects.get_or_create(
                        excel_app=excel_app,
                        activity_name=activity_type['activity'][0]['name'],
                        name=activity_type['name'],
                        short_name=activity_type['short_name']
                    )

        return new_excel_apps


    def create_workbook_template(self, filename, licence_category='Fauna Other Purpose'):
        """
        Creates a blank template with purposes and column headings only
        """
        meta = OrderedDict()
        if os.path.isfile(filename):
            logger.warn('File already exists {}'.format(filename))
            return None

        wb = xlsxwriter.Workbook(filename)
        ws = wb.add_worksheet(APP_SHEET_NAME)
        self.set_formats(wb)

        row_num = 0
        col_num = 0
        cell_dict = {}
        cell_start = xl_rowcol_to_cell(row_num, col_num, row_abs=True, col_abs=True)
        sys_cols = self.cols_system(None, 'System').keys()
        for col_name in sys_cols:
            ws.write(row_num, col_num, col_name, self.bold_unlocked)
            col_num += 1
        cell_end = xl_rowcol_to_cell(row_num, col_num-1, row_abs=True, col_abs=True)
        cell_dict.update({'System': [cell_start, cell_end]})

        activity_name_list = self.get_purposes(licence_category)
        for activity_name in activity_name_list:
            #cols = self.cols_output(None, 'Importing Fauna (Non-Commercial)')
            activity_type_cols = self.cols_output(None, activity_name).keys()
            ws.write(row_num, col_num, '', self.bold); col_num += 1
            cell_start = xl_rowcol_to_cell(row_num, col_num, row_abs=True, col_abs=True)
            for col_name in activity_type_cols:
                ws.write(row_num, col_num, col_name, self.bold_unlocked)
                col_num += 1
            cell_end = xl_rowcol_to_cell(row_num, col_num-1, row_abs=True, col_abs=True)
            cell_dict.update({activity_name: [cell_start, cell_end]})

        self.write_sheet_meta(wb, cell_dict, activity_name_list)
        wb.close()

    def read_workbook(self, input_filename, licence_category='Fauna Other Purpose'):
        """
        Read the contents of input_filename and return
        :param logger:         The logger
        :param input_filename: Filepath of the spreadsheet to read
        :return:  Dict of response sets

        for meta:
            schema = WildlifeLicenceActivity.objects.get(name='Importing Fauna (Non-Commercial)').schema
            In [30]: [{i['name'],i['label']} for i in search_multiple_keys(schema, 'isEditable', ['name', 'label'])]
            Out[30]: [{u'Species', u'Species1-1'}, {u'Number of animals', u'Species1-2'}]
        """
        import ipdb; ipdb.set_trace()
        meta = OrderedDict()
        if not os.path.isfile(input_filename):
            logger.warn('Cannot find file {}. Creating ...'.format(input_filename))
            self.create_workbook_template(input_filename, licence_category)

        wb = xlrd.open_workbook(input_filename)
        sh = wb.sheet_by_name(APP_SHEET_NAME)
        sh_meta = wb.sheet_by_name(META_SHEET_NAME)

        # Read Meta
        number_of_rows = sh_meta.nrows
        hdr = sh_meta.row_values(0)
        for row in range(1, number_of_rows):
            row_values = sh_meta.row_values(row)
            purpose = row_values[0]
            meta.update([(purpose, {})])
            for i in zip(hdr, row_values)[1:]:
                meta[purpose].update( {i[0]: i[1]} )

        # Read Application Data
        excel_data = {}
        number_of_rows = sh.nrows
        hdr = sh.row_values(0)
        for row in range(1, number_of_rows):
            #import ipdb; ipdb.set_trace()
            row_values = sh.row_values(row)
            lodgement_number = row_values[hdr.index('lodgement_number')]
            application_id = int(row_values[hdr.index('application_id')])
            licence_number = row_values[hdr.index('licence_number')]
            applicant = row_values[hdr.index('applicant')]
            applicant_type = row_values[hdr.index('applicant_type')]
            applicant_id = int(row_values[hdr.index('applicant_id')])
            application = Application.objects.get(lodgement_number=lodgement_number)

            for purpose in meta.keys():
                if purpose != "System":
                    try:
                        idx_start = int(meta[purpose]['First Col'])
                        idx_end = int(meta[purpose]['Last Col'])
                        purpose_row = row_values[idx_start:idx_end]
                        hdr_row = hdr[idx_start:idx_end]


                        idx_to_be_issued = self.get_index(hdr_row, 'to_be_issued')
                        to_be_issued = purpose_row[idx_to_be_issued]
                        if to_be_issued in ['y', 'Y'] and not licence_number:
                            # create licence, if not already created
                            #if not licence_exists(purpose, lodgement_number):

                            # check if user already has a licence. if so, re-use licence_number and update the licence_sequence
                            #licence_number = self.create_licence(application, purpose).reference
                            licence_number = self.create_licence(application, purpose, applicant_type, applicant_id).reference
                            #purpose_row[idx_start:idx_start]
                            row_values[hdr.index('licence_number')] = licence_number
                    except ValueError, e:
                        logger.error('Cannot find activity_type {} in Excel header./n{}'.format(activity_type, e))

            excel_data.update({lodgement_number: row_values})

        #wb.release_resources()
        #del wb

        # Re-output Application Data with licence_numbers
        #out_filename = '/tmp/wc_apps_out_{}.xlsx'.format(licence_category.lower().replace(' ','_'))
        #wb_out = xlsxwriter.Workbook(out_filename)
        import ipdb; ipdb.set_trace()
        wb = xlsxwriter.Workbook(input_filename)
        #self.set_formats(wb_out)
        #ws_out = wb_out.add_worksheet(APP_SHEET_NAME)

        ws = wb.get_worksheet_by_name(APP_SHEET_NAME)
        #sh_meta = wb.sheet_by_name(META_SHEET_NAME)

        wb = openpyxl.load_workbook(input_filename)
        ws = wb.get_sheet_by_name(APP_SHEET_NAME)

        row_num = 0
        col_num = 0
        #ws.write_row(row_num, col_num, hdr, self.bold); row_num += 1
        self.write_row(row_num, col_num, hdr, ws); row_num += 1
        for k,v in excel_data.iteritems():
            #import ipdb; ipdb.set_trace()
            #ws.write_row(row_num, col_num, v)
            self.write_row(row_num, col_num, v, ws)
            row_num += 1

        # Append new applications to output
        #import ipdb; ipdb.set_trace()
        #cur_app_ids = [int(v[1]) for k,v in excel_data.iteritems()] # existing app id's
        #new_app_ids = Application.objects.exclude(processing_status='draft').exclude(id__in=cur_app_ids)
        self.write_new_app_data(excel_data, meta, licence_category, ws, row_num)

        #wb_out.close()
        wb.save(input_filename)

    def write_row(self, row_num, col_num, values, worksheet):
        """ writes values as a row of datai. If values is a single value, writes to a single cell """
        if not isinstance(values, list):
            #import ipdb; ipdb.set_trace()
            values = [values] if values else ['']

        for col, val in enumerate(values, start=col_num):
            worksheet.cell(row=row_num+1, column=col+1, value=val) # openpyxl count rows and cols from 1
        
    def write_new_app_data(self, excel_data, meta, licence_category, worksheet, next_row):
        cur_app_ids = [int(v[1]) for k,v in excel_data.iteritems()] # existing app id's
        new_excel_apps = self.create_excel_model(licence_category, cur_app_ids)

        row_num = next_row
        for excel_app in new_excel_apps:

            # System data
            col_num = int(meta['System']['First Col'])
            for k,v in excel_app.cols_output.iteritems():
                #worksheet.write(row_num, col_num, v, self.locked)
                self.write_row(row_num, col_num, v, worksheet)
                col_num += 1


            # Application data
            #import ipdb; ipdb.set_trace()
            for purpose in meta.keys():
                #import ipdb; ipdb.set_trace()

                if purpose != "System":
                    activity_type = excel_app.excel_activity_types.filter(activity_name=purpose)
                    activity_type_cols = self.cols_output(activity_type, purpose)

                    col_num = int(meta[purpose]['First Col'])# + 1
                    if activity_type.exists():
                        for k,v in activity_type_cols.iteritems():
                            #ws.write('B1', 'Here is\nsome long text\nthat\nwe wrap',      wrap)
                            #worksheet.write(row_num, col_num, v, self.unlocked_wrap)
                            self.write_row(row_num, col_num, v, worksheet)
                            col_num += 1
                    else:
                        # create a blank activity_type bilock
                        for _ in activity_type_cols.keys():
                            #worksheet.write(row_num, col_num, '', self.unlocked)
                            self.write_row(row_num, col_num, '', worksheet)
                            col_num += 1

            row_num += 1


    def cols_system(self, qs_activity_type, activity_name):
        """ qs_excel_app --> ExcelApplication """
        return OrderedDict([
            ('lodgement_number', qs_activity_type[0].excel_app.lodgement_number if qs_activity_type else None),
            ('application_id', qs_activity_type[0].excel_app.application.id if qs_activity_type else None),
            ('licence_number', qs_activity_type[0].excel_app.licence_number if qs_activity_type else None),
            ('applicant', qs_activity_type[0].excel_app.applicant_details if qs_activity_type else None),
            ('applicant_type', qs_activity_type[0].excel_app.applicant_type if qs_activity_type else None),
            ('applicant_id', qs_activity_type[0].excel_app.applicant_id if qs_activity_type else None),
        ])


    def cols_common(self, qs_activity_type, activity_name):
        code = activity_name[:2].lower()
        ordered_dict = OrderedDict([
            ('{}_cover_processed'.format(code), None),
            ('{}_cover_processed_date'.format(code), None),
            ('{}_cover_processed_by'.format(code), None),
            ('{}_conditions'.format(code), qs_activity_type[0].conditions if qs_activity_type else None),
            ('{}_issue_date'.format(code), qs_activity_type[0].issue_date if qs_activity_type else None),
            ('{}_start_date'.format(code), qs_activity_type[0].start_date if qs_activity_type else None),
            ('{}_expiry_date'.format(code), qs_activity_type[0].expiry_date if qs_activity_type else None),
            ('{}_to_be_issued'.format(code), qs_activity_type[0].issued if qs_activity_type else None),
            ('{}_processed'.format(code), qs_activity_type[0].processed if qs_activity_type else None),
        ])
        return ordered_dict

    def cols_output(self, qs_activity_type, activity_name):
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
        ordered_dict.update(self.get_activity_type_sys_answers(qs_activity_type, activity_name))
        ordered_dict.update(self.cols_common(qs_activity_type, activity_name))
        return ordered_dict


    def create_licence(self, application, activity_name, applicant_type, applicant_id):
        """ activity_name='Importing Fauna (Non-Commercial)' """
        import ipdb; ipdb.set_trace()
        licence = None
        activity=WildlifeLicenceActivity.objects.get(name=activity_name)
        if applicant_type == "ORG": # Applicant is an Organisation
            qs_licence = WildlifeLicence.objects.filter(org_applicant_id=applicant_id)
            if qs_licence.exists():
                # use existing licence, just increment sequence_number
                licence = WildlifeLicence.objects.create(
                    licence_number=qs_licence.last().licence_number,
                    licence_sequence=qs_licence.last().licence_sequence + 1,
                    current_application=application,
                    org_applicant_id=applicant_id,
                    submitter=application.submitter,
                    licence_type=activity
                )
            else:
                licence = WildlifeLicence.objects.create(
                    current_application=application,
                    org_applicant_id=applicant_id,
                    submitter=application.submitter,
                    licence_type=activity
                )

        elif applicant_type == "PRX": # Applicant is a proxy_applicant
            qs_licence = WildlifeLicence.objects.filter(proxy_applicant_id=applicant_id)
            if not qs_licence.exists():
                # use existing licence, just increment sequence_number
                licence = WildlifeLicence.objects.create(
                    licence_number=qs_licence.last().licence_number,
                    licence_sequence=qs_licence.last().licence_sequence + 1,
                    current_application=application,
                    proxy_applicant_id=applicant_id,
                    submitter=application.submitter,
                    licence_type=activity
                )
            else:
                licence = WildlifeLicence.objects.create(
                    current_application=application,
                    proxy_applicant_id=applicant_id,
                    submitter=application.submitter,
                    licence_type=activity
                )


        elif applicant_type == "SUB": # Applicant is the submitter
            qs_licence = WildlifeLicence.objects.filter(submitter_id=applicant_id)
            if not qs_licence.exists():
                # use existing licence, just increment sequence_number
                licence = WildlifeLicence.objects.create(
                    licence_number=qs_licence.last().licence_number,
                    licence_sequence=qs_licence.last().licence_sequence + 1,
                    current_application=application,
                    #proxy_applicant_id=applicant_id,
                    submitter_id=applicant_id,
                    licence_type=activity
                )
            else:
                licence = WildlifeLicence.objects.create(
                    current_application=application,
                    #org_applicant_id=applicant_id,
                    submitter_id=applicant_id,
                    licence_type=activity
                )

        return licence

    def write_workbook(self, licence_category='Flora Industry'):
        """
        from wildlifecompliance.utils.excel_utils import write_workbook, write_excel_model
        write_excel_model('Fauna Other Purpose')
        write_workbook('Fauna Other Purpose')
        """
        #filename = '/tmp/wc_apps_{}.xls'.format(datetime.now().strftime('%Y%m%dT%H%M%S'))
        excel_apps = ExcelApplication.objects.filter(application__licence_category=licence_category).order_by('application_id') #filter(id__in=ids)

        filename = '/tmp/wc_apps_{}.xlsx'.format(licence_category.lower().replace(' ','_'))
        #sheet_name = 'Applications'

        wb = xlsxwriter.Workbook(filename)
        ws = wb.add_worksheet(APP_SHEET_NAME)
        self.set_formats(wb)

        #ws.set_column('E:DW', None, unlocked)
        ws.set_column('A:XDF', None, self.unlocked)
        ws.protect()

        # Sheet header, first row
        row_num = 0

        # Header
        excel_app = excel_apps.last()
        licence_class = excel_app.application.licence_type_data['short_name']
        #short_name_list = get_purposes(licence_class).values_list('activity_type__short_name', flat=True)
        activity_name_list = self.get_purposes(licence_class)#[:2]
        col_num = 0
        i#import ipdb; ipdb.set_trace()
        for k,v in excel_app.cols_output.iteritems():
            #ws.write(row_num, col_num, k, font_style)
            ws.write(row_num, col_num, k, self.bold)
            col_num += 1

        for activity_name in activity_name_list:
            #activity_type = excel_app.excel_activity_types.filter(activity_name=activity_name)
            #import ipdb; ipdb.set_trace()
            activity_type_cols = self.cols_output(None, activity_name).keys()

            ws.write(row_num, col_num, '', self.bold); col_num += 1
            #ws.write(row_num, col_num, short_name, bold); col_num += 1

            for col_name in activity_type_cols:
                ws.write(row_num, col_num, col_name, self.bold_unlocked)
                col_num += 1

        # Application data
        cell_dict = {}
        row_start = row_num + 1
        for excel_app in excel_apps:
            row_num += 1
            col_num = 0
            cell_start = xl_rowcol_to_cell(row_start, col_num, row_abs=True, col_abs=True)
            for k,v in excel_app.cols_output.iteritems():
                ws.write(row_num, col_num, v, self.locked)
                col_num += 1

            cell_end = xl_rowcol_to_cell(row_num, col_num-1, row_abs=True, col_abs=True)
            cell_dict.update({'System': [cell_start, cell_end]})

            for activity_name in activity_name_list:
                #import ipdb; ipdb.set_trace()

                ws.write(row_num, col_num, ''); col_num += 1

                cell_start = xl_rowcol_to_cell(row_start, col_num, row_abs=True, col_abs=True)
                activity_type = excel_app.excel_activity_types.filter(activity_name=activity_name)
                activity_type_cols = self.cols_output(activity_type, activity_name)

                col_start = col_num
                if activity_type.exists():
                    #import ipdb; ipdb.set_trace()
                    for k,v in activity_type_cols.iteritems():
                        #ws.write('B1', 'Here is\nsome long text\nthat\nwe wrap',      wrap)
                        ws.write(row_num, col_num, v, self.unlocked_wrap)
                        col_num += 1
                else:
                    # create a blank activity_type bilock
                    for _ in activity_type_cols.keys():
                        ws.write(row_num, col_num, '', self.unlocked)
                        col_num += 1

                cell_end = xl_rowcol_to_cell(row_num, col_num-1, row_abs=True, col_abs=True)
                cell_dict.update({activity_name: [cell_start, cell_end]})

        #ws.write('F2:O3', '=Taking')
        #wb.define_name('Application', '=Sheet1!$F$2:$O$14')

        # Write the named ranges and Meta data
        self.write_sheet_meta(wb, cell_dict, activity_name_list)

        wb.close()
        #return wb
        return cell_dict


    def write_sheet_meta(self, workbook, cell_dict, activity_name_list):
        ws_meta = workbook.add_worksheet(META_SHEET_NAME)
        #ws_meta = workbook.sheet_by_name('Meta')

        row_num = 0
        col_num = 0
        workbook.define_name('{0}!{1}'.format(APP_SHEET_NAME, 'System'), '={0}!{1}:{2}'.format(APP_SHEET_NAME, cell_dict['System'][0], cell_dict['System'][1]))
        # Hdr
        ws_meta.write(row_num, col_num, 'Purpose')
        ws_meta.write(row_num, col_num+1, 'First Col')
        ws_meta.write(row_num, col_num+2, 'Last Col')

        # System
        ws_meta.write(row_num+1, col_num, 'System')                                         # Purpose
        ws_meta.write(row_num+1, col_num+1, xl_cell_to_rowcol(cell_dict['System'][0])[1])   # First Col
        ws_meta.write(row_num+1, col_num+2, xl_cell_to_rowcol(cell_dict['System'][1])[1])   # Last Col
        #import ipdb; ipdb.set_trace()

        # Purposes
        width = 20
        for row_num, activity_name in enumerate(activity_name_list, start=2):
            #wb.define_name('Applications!Taking', '=Applications!$F$2:$O$3')
            #activity_name2 = replace_special_chars(activity_name)
            workbook.define_name('{0}!{1}'.format(APP_SHEET_NAME, self.replace_special_chars(activity_name)), '={0}!{1}:{2}'.format(APP_SHEET_NAME, cell_dict[activity_name][0], cell_dict[activity_name][1]))
            ws_meta.write(row_num, col_num, activity_name)                                          # Purpose
            ws_meta.write(row_num, col_num+1, xl_cell_to_rowcol(cell_dict[activity_name][0])[1])    # First Col
            ws_meta.write(row_num, col_num+2, xl_cell_to_rowcol(cell_dict[activity_name][1])[1])    # Last Col
            width = len(activity_name) if len(activity_name) > width else width

        #import ipdb; ipdb.set_trace()
        #  lock the System App Data section only
        #ws.protect()
        #ws.set_column('{}:{}'.format(xl_col_to_name(0), xl_col_to_name(xl_cell_to_rowcol(cell_dict['System'][1])[1])), None, locked)
        #ws.set_column('{}:AMJ'.format(xl_col_to_name(xl_cell_to_rowcol(cell_dict['System'][1])[1] + 1)), None, unlocked)
        #ws.set_column('E:DW', None, unlocked)


        #  lock  the Meta Sheet (mostly)
        ws_meta.set_column('D:G', 13, self.integer )
        ws_meta.set_column('A:Z', None, self.locked)
        ws_meta.protect()
        ws_meta.set_column(0, 0, width)


