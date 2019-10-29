import  xlrd, xlwt
import os

import logging
logger = logging.getLogger(__name__)

def read_workbook(input_filename):
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

def write_workbook():
    filename = 'wildlife_compliance_applications_{}.xls'.format(datetime.now().strftime('%Y%m%dT%H%M%S'))

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Applications')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    applications = Application.objects.filter(id__in=[145])

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

