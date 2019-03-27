import os
from io import BytesIO
from datetime import date

from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, ListFlowable, \
    KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

from django.core.files import File
from django.conf import settings

from wildlifecompliance.components.licences.models import LicenceDocument

BW_DPAW_HEADER_LOGO = os.path.join(
    settings.BASE_DIR,
    'wildlifelicensing',
    'static',
    'wl',
    'img',
    'bw_dpaw_header_logo.png')

COLOUR_DPAW_HEADER_LOGO = os.path.join(
    settings.BASE_DIR,
    'wildlifelicensing',
    'static',
    'wl',
    'img',
    'colour_dpaw_header_logo.png')

LICENCE_HEADER_IMAGE_WIDTH = 170
LICENCE_HEADER_IMAGE_HEIGHT = 42

PAGE_WIDTH, PAGE_HEIGHT = A4

DEFAULT_FONTNAME = 'Helvetica'
BOLD_FONTNAME = 'Helvetica-Bold'
ITALIC_FONTNAME = 'Helvetica-Oblique'
BOLD_ITALIC_FONTNAME = 'Helvetica-BoldOblique'

VERY_LARGE_FONTSIZE = 14
LARGE_FONTSIZE = 12
MEDIUM_FONTSIZE = 10
SMALL_FONTSIZE = 8

PARAGRAPH_BOTTOM_MARGIN = 5

SECTION_BUFFER_HEIGHT = 10

DATE_FORMAT = '%d/%m/%Y'

HEADER_MARGIN = 10
HEADER_SMALL_BUFFER = 3

PAGE_MARGIN = 20
PAGE_TOP_MARGIN = 200

LETTER_HEADER_MARGIN = 30
LETTER_PAGE_MARGIN = 60
LETTER_IMAGE_WIDTH = 242
LETTER_IMAGE_HEIGHT = 55
LETTER_HEADER_RIGHT_LABEL_OFFSET = 400
LETTER_HEADER_RIGHT_INFO_OFFSET = 450
LETTER_HEADER_SMALL_BUFFER = 5
LETTER_ADDRESS_BUFFER_HEIGHT = 40
LETTER_BLUE_FONT = 0x045690

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name='InfoTitleLargeCenter',
        fontName=BOLD_FONTNAME,
        fontSize=LARGE_FONTSIZE,
        spaceAfter=PARAGRAPH_BOTTOM_MARGIN,
        alignment=enums.TA_CENTER))
styles.add(
    ParagraphStyle(
        name='InfoTitleVeryLargeCenter',
        fontName=BOLD_FONTNAME,
        fontSize=VERY_LARGE_FONTSIZE,
        spaceAfter=PARAGRAPH_BOTTOM_MARGIN * 2,
        alignment=enums.TA_CENTER))
styles.add(
    ParagraphStyle(
        name='InfoTitleLargeLeft',
        fontName=BOLD_FONTNAME,
        fontSize=LARGE_FONTSIZE,
        spaceAfter=PARAGRAPH_BOTTOM_MARGIN,
        alignment=enums.TA_LEFT,
        leftIndent=PAGE_WIDTH / 10,
        rightIndent=PAGE_WIDTH / 10))
styles.add(
    ParagraphStyle(
        name='InfoTitleLargeRight',
        fontName=BOLD_FONTNAME,
        fontSize=LARGE_FONTSIZE,
        spaceAfter=PARAGRAPH_BOTTOM_MARGIN,
        alignment=enums.TA_RIGHT,
        rightIndent=PAGE_WIDTH / 10))
styles.add(
    ParagraphStyle(
        name='BoldLeft',
        fontName=BOLD_FONTNAME,
        fontSize=MEDIUM_FONTSIZE,
        alignment=enums.TA_LEFT))
styles.add(
    ParagraphStyle(
        name='BoldRight',
        fontName=BOLD_FONTNAME,
        fontSize=MEDIUM_FONTSIZE,
        alignment=enums.TA_RIGHT))
styles.add(
    ParagraphStyle(
        name='ItalicLeft',
        fontName=ITALIC_FONTNAME,
        fontSize=MEDIUM_FONTSIZE,
        alignment=enums.TA_LEFT))
styles.add(
    ParagraphStyle(
        name='ItalifRight',
        fontName=ITALIC_FONTNAME,
        fontSize=MEDIUM_FONTSIZE,
        alignment=enums.TA_RIGHT))
styles.add(ParagraphStyle(name='Center', alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='Left', alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='Right', alignment=enums.TA_RIGHT))
styles.add(
    ParagraphStyle(
        name='LetterLeft',
        fontSize=LARGE_FONTSIZE,
        alignment=enums.TA_LEFT))
styles.add(
    ParagraphStyle(
        name='LetterBoldLeft',
        fontName=BOLD_FONTNAME,
        fontSize=LARGE_FONTSIZE,
        alignment=enums.TA_LEFT))


def _create_licence_header(canvas, doc, draw_page_number=True):
    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y = PAGE_HEIGHT - HEADER_MARGIN

    canvas.drawCentredString(
        PAGE_WIDTH / 2,
        current_y - LARGE_FONTSIZE,
        '{}'.format(
            settings.DEP_NAME.upper()))

    current_y -= 30

    dpaw_header_logo = ImageReader(BW_DPAW_HEADER_LOGO)
    canvas.drawImage(
        dpaw_header_logo,
        HEADER_MARGIN,
        current_y - 40,
        width=LICENCE_HEADER_IMAGE_WIDTH,
        height=LICENCE_HEADER_IMAGE_HEIGHT)

    current_x = HEADER_MARGIN + LICENCE_HEADER_IMAGE_WIDTH + 5

    canvas.setFont(DEFAULT_FONTNAME, SMALL_FONTSIZE)

    canvas.drawString(current_x, current_y -
                      (SMALL_FONTSIZE + HEADER_SMALL_BUFFER), 'Enquiries:')
    canvas.drawString(current_x, current_y -
                      (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'Telephone:')
    canvas.drawString(current_x, current_y -
                      (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, 'Facsimile:')
    canvas.drawString(current_x, current_y -
                      (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, 'Web Site:')
    canvas.drawString(current_x,
                      current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5,
                      'Correspondence:')

    current_x += 80

    canvas.drawString(current_x,
                      current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER),
                      '17 DICK PERRY AVE, KENSINGTON, WESTERN AUSTRALIA')
    canvas.drawString(current_x,
                      current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2,
                      '08 9219 9000')
    canvas.drawString(current_x,
                      current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3,
                      '08 9219 8242')
    canvas.drawString(current_x, current_y -
                      (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, doc.site_url)

    canvas.setFont(BOLD_FONTNAME, SMALL_FONTSIZE)
    canvas.drawString(current_x,
                      current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5,
                      'Locked Bag 30')
    canvas.drawString(current_x,
                      current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 6,
                      'Bentley Delivery Centre WA 6983')

    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y -= 36
    current_x += 200

    if draw_page_number:
        canvas.drawString(current_x, current_y -
                          (LARGE_FONTSIZE + HEADER_SMALL_BUFFER), 'PAGE')

    if hasattr(doc, 'licence'):
        canvas.drawString(current_x, current_y -
                          (LARGE_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'NO.')

    canvas.setFont(DEFAULT_FONTNAME, LARGE_FONTSIZE)

    current_x += 50

    if draw_page_number:
        canvas.drawString(current_x,
                          current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER),
                          str(canvas.getPageNumber()))

    if hasattr(doc, 'licence'):
        canvas.drawString(current_x,
                          current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER) * 2,
                          '{}'.format(doc.licence.id))


def _create_licence(licence_buffer, licence, application):
    site_url = settings.SITE_URL
    every_page_frame = Frame(
        PAGE_MARGIN,
        PAGE_MARGIN,
        PAGE_WIDTH - 2 * PAGE_MARGIN,
        PAGE_HEIGHT - 160,
        id='EveryPagesFrame')
    every_page_template = PageTemplate(
        id='EveryPages',
        frames=[every_page_frame],
        onPage=_create_licence_header)

    doc = BaseDocTemplate(
        licence_buffer,
        pageTemplates=[every_page_template],
        pagesize=A4)

    # this is the only way to get data into the onPage callback function
    doc.licence = licence
    doc.site_url = site_url

    licence_table_style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])

    elements = []

    elements.append(Paragraph('Licence Summary', styles['InfoTitleVeryLargeCenter']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('Activities', styles['BoldLeft']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    conditionList = ListFlowable(
        [Paragraph("{name}: {start_date} - {expiry_date}".format(
            name=selected_activity.licence_activity.name,
            start_date=selected_activity.start_date.strftime(DATE_FORMAT),
            expiry_date=selected_activity.expiry_date.strftime(DATE_FORMAT)
        ), styles['Left'],) for selected_activity in licence.current_activities],
        bulletFontName=BOLD_FONTNAME, bulletFontSize=MEDIUM_FONTSIZE)
    elements.append(conditionList)
    elements.append(PageBreak())

    for selected_activity in licence.current_activities:
        elements.append(Paragraph(selected_activity.licence_activity.name, styles['InfoTitleVeryLargeCenter']))

        # application conditions
        activity_conditions = application.conditions.filter(
            licence_activity_id=selected_activity.licence_activity_id)
        if activity_conditions.exists():
            elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
            elements.append(Paragraph('Conditions', styles['BoldLeft']))
            elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

            conditionList = ListFlowable(
                [Paragraph(a.condition, styles['Left']) for a in activity_conditions.order_by('order')],
                bulletFontName=BOLD_FONTNAME, bulletFontSize=MEDIUM_FONTSIZE)
            elements.append(conditionList)

        elements += _layout_extracted_fields(licence.extracted_fields)

        # additional information
        '''if licence.additional_information:
            elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
            elements.append(Paragraph('Additional Information', styles['BoldLeft']))
            elements += _layout_paragraphs(licence.additional_information)'''

        # delegation holds the dates, licencee and issuer details.
        delegation = []

        # dates and licensing officer
        dates_licensing_officer_table_style = TableStyle(
            [('VALIGN', (0, 0), (-2, -1), 'TOP'), ('VALIGN', (0, 0), (-1, -1), 'BOTTOM')])

        delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        date_headings = [
            Paragraph(
                'Date of Issue', styles['BoldLeft']), Paragraph(
                'Valid From', styles['BoldLeft']), Paragraph(
                    'Date of Expiry', styles['BoldLeft'])]
        date_values = [
            Paragraph(
                selected_activity.issue_date.strftime(DATE_FORMAT), styles['Left']), Paragraph(
                selected_activity.start_date.strftime(DATE_FORMAT), styles['Left']), Paragraph(
                    selected_activity.expiry_date.strftime(DATE_FORMAT), styles['Left'])]

        if selected_activity.original_issue_date is not None:
            date_headings.insert(
                0,
                Paragraph(
                    'Original Date of Issue',
                    styles['BoldLeft']))
            date_values.insert(
                0,
                Paragraph(
                    selected_activity.original_issue_date.strftime(DATE_FORMAT),
                    styles['Left']))

        delegation.append(Table([[date_headings, date_values]],
                                colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                                style=dates_licensing_officer_table_style))

        # applicant details
        delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        if application.applicant_type == application.APPLICANT_TYPE_ORGANISATION:
            address = application.org_applicant.address
            pass
        elif application.applicant_type == application.APPLICANT_TYPE_PROXY:
            address = application.proxy_applicant.residential_address
            pass
        else:  # application.applicant_type == application.APPLICANT_TYPE_SUBMITTER
            address = application.submitter.residential_address

        address_paragraphs = [
            Paragraph(
                address.line1, styles['Left']), Paragraph(
                address.line2, styles['Left']), Paragraph(
                    address.line3, styles['Left']), Paragraph(
                        '%s %s %s' %
                        (address.locality, address.state, address.postcode), styles['Left']), Paragraph(
                            address.country.name, styles['Left'])]
        delegation.append(Table([[[Paragraph('Licensee:',
                                            styles['BoldLeft']),
                                Paragraph('Address',
                                            styles['BoldLeft'])],
                                [Paragraph(licence.current_application.applicant,
                                            styles['Left'])] + address_paragraphs]],
                                colWidths=(120,
                                        PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                                style=licence_table_style))

        delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        delegation.append(
            Paragraph(
                'Issued by a Wildlife Licensing Officer of the {} '
                'under delegation from the Minister for Environment pursuant to section 133(1) '
                'of the Conservation and Land Management Act 1984.'.format(
                    settings.DEP_NAME), styles['Left']))

        elements.append(KeepTogether(delegation))
        elements.append(PageBreak())

    doc.build(elements)

    return licence_buffer


def _layout_extracted_fields(extracted_fields):
    elements = []

    def __children_have_data(field):
        for group in field.get('children', []):
            for child_field in group:
                if child_field.get('data'):
                    return True

        return False

    # information extracted from application
    if extracted_fields:
        for field in extracted_fields:
            if 'children' not in field:
                if 'data' in field and field['data']:
                    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
                    elements.append(
                        Paragraph(
                            field['label'],
                            styles['BoldLeft']))

                    if field['help_text']:
                        elements.append(
                            Paragraph(
                                field['help_text'],
                                styles['ItalicLeft']))

                    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

                    if field['type'] in ['text', 'text_area']:
                        elements += _layout_paragraphs(field['data'])
                    elif field['type'] in ['radiobuttons', 'select']:
                        elements.append(Paragraph(dict([i.values() for i in field['options']]). get(
                            field['data'], 'Not Specified'), styles['Left']))
                    else:
                        elements.append(
                            Paragraph(
                                field['data'],
                                styles['Left']))

                elif field['type'] == 'label':
                    if any([option.get('data', 'off') ==
                            'on' for option in field['options']]):
                        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
                        elements.append(
                            Paragraph(
                                field['label'],
                                styles['BoldLeft']))

                        if field['help_text']:
                            elements.append(
                                Paragraph(
                                    field['help_text'],
                                    styles['ItalicLeft']))

                        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

                        elements.append(
                            Paragraph(
                                ', '.join(
                                    [
                                        option['label'] for option in field['options'] if option.get(
                                            'data',
                                            'off') == 'on']),
                                styles['Left']))
            else:
                if not __children_have_data(field):
                    continue

                elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
                elements.append(Paragraph(field['label'], styles['BoldLeft']))

                if field['help_text']:
                    elements.append(
                        Paragraph(
                            field['help_text'],
                            styles['ItalicLeft']))

                table_data = []
                for index, group in enumerate(field['children']):
                    if index == 0:
                        heading_row = []
                        for child_field in group:
                            heading_row.append(
                                Paragraph(
                                    child_field['label'],
                                    styles['BoldLeft']))
                        if heading_row:
                            table_data.append(heading_row)

                    row = []
                    for child_field in group:
                        if child_field['type'] in ['radiobuttons', 'select']:
                            row.append(Paragraph(dict([i.values() for i in child_field['options']]). get(
                                child_field['data'], 'Not Specified'), styles['Left']))
                        elif child_field['type'] == 'label':
                            if any([option.get('data', 'off') ==
                                    'on' for option in child_field['options']]):
                                row.append(
                                    Paragraph(
                                        ', '.join(
                                            [
                                                option['label'] for option in child_field['options'] if option.get(
                                                    'data',
                                                    'off') == 'on']),
                                        styles['Left']))
                            else:
                                row.append(
                                    Paragraph(
                                        'Not Specified',
                                        styles['Left']))
                        else:
                            row.append(
                                Paragraph(
                                    child_field['data'],
                                    styles['Left']))

                    if row:
                        table_data.append(row)

                if table_data:
                    elements.append(Table(table_data, style=TableStyle(
                        [('VALIGN', (0, 0), (-1, -1), 'TOP')])))

    return elements


def create_licence_doc(licence, application):
    licence_buffer = BytesIO()

    _create_licence(licence_buffer, licence, application)
    filename = 'licence-{}.pdf'.format(licence.id)
    document = LicenceDocument.objects.create(licence=licence, name=filename)
    document._file.save(filename, File(licence_buffer), save=True)

    licence_buffer.close()

    return document


def create_licence_pdf_bytes(
        licence,
        application,
        site_url,
        original_issue_date):
    licence_buffer = BytesIO()

    _create_licence(licence_buffer, licence, application)

    # Get the value of the BytesIO buffer
    value = licence_buffer.getvalue()
    licence_buffer.close()

    return value
