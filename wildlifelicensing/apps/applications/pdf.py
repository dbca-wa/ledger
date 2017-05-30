import os
import json
from io import BytesIO
from datetime import date

from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, ListFlowable, \
    KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from wildlifelicensing.apps.main.pdf import MEDIUM_FONTSIZE


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

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='InfoTitleLargeCenter', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE,
                          spaceAfter=PARAGRAPH_BOTTOM_MARGIN, alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='InfoTitleVeryLargeCenter', fontName=BOLD_FONTNAME, fontSize=VERY_LARGE_FONTSIZE,
                          spaceAfter=PARAGRAPH_BOTTOM_MARGIN * 2, alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='InfoTitleLargeLeft', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE,
                          spaceAfter=PARAGRAPH_BOTTOM_MARGIN, alignment=enums.TA_LEFT,
                          leftIndent=PAGE_WIDTH / 10, rightIndent=PAGE_WIDTH / 10))
styles.add(ParagraphStyle(name='InfoTitleLargeRight', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE,
                          spaceAfter=PARAGRAPH_BOTTOM_MARGIN, alignment=enums.TA_RIGHT,
                          rightIndent=PAGE_WIDTH / 10))
styles.add(ParagraphStyle(name='BoldLeft', fontName=BOLD_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='BoldRight', fontName=BOLD_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_RIGHT))
styles.add(ParagraphStyle(name='ItalicLeft', fontName=ITALIC_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='ItalifRight', fontName=ITALIC_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_RIGHT))
styles.add(ParagraphStyle(name='Center', alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='Left', alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='Right', alignment=enums.TA_RIGHT))
styles.add(ParagraphStyle(name='LetterLeft', fontSize=LARGE_FONTSIZE, alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='LetterBoldLeft', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE, alignment=enums.TA_LEFT))


def _create_application(application_buffer, application):
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN, PAGE_HEIGHT - 2 * PAGE_MARGIN,
                             id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=every_page_frame)

    doc = BaseDocTemplate(application_buffer, pageTemplates=[every_page_template], pagesize=A4)

    elements = []

    # cannot use licence get_title_with_variants because licence isn't saved yet so can't get variants
    if application.variants.exists():
        title = '{} ({})'.format(application.licence_type.name.encode('UTF-8'), ' / '.join(application.variants.all().
                                 values_list('name', flat=True)))
    else:
        title = application.licence_type.name.encode('UTF-8')

    elements.append(Paragraph('Application for {}'.format(title), styles['InfoTitleVeryLargeCenter']))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    elements.append(_create_metadata(application))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    for field, datum in zip(application.licence_type.application_schema, application.data):
        _create_data(field, datum, elements, 0)

    doc.build(elements)

    return application_buffer


def _create_data(field, data, elements, indent_index):
    paragraph_style = ParagraphStyle('', leftIndent=indent_index * 20)
    if field['type'] == 'section':
        paragraph_style.fontName = BOLD_FONTNAME
        paragraph_style.fontSize = LARGE_FONTSIZE
        elements.append(Paragraph(field['label'], paragraph_style))
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        for child_data in data[field['name']]:
            for child_field in field['children']:
                _create_data(child_field, child_data, elements, indent_index)
    elif field['type'] == 'group':
        paragraph_style.fontName = BOLD_FONTNAME

        for group_index, child_data in enumerate(data[field['name']]):
            elements.append(Paragraph('{} {}'.format(field['label'], group_index + 1), paragraph_style))
            elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
            for child_field in field['children']:
                _create_data(child_field, child_data, elements, indent_index + 1)
    else:
        paragraph_style.fontName = BOLD_FONTNAME
        elements.append(Paragraph(field['label'], paragraph_style))
        paragraph_style.fontName = DEFAULT_FONTNAME
        elements.append(Paragraph(data[field['name']], paragraph_style))

        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))


def _create_metadata(application):
    # dates and licensing officer
    metadata_table_style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('ALIGN', (0, 0), (-2, -1), 'LEFT'),
                                       ('ALIGN', (-1, 0), (-1, -1), 'LEFT')])

    top_row = [
        Paragraph('Licensee:', styles['BoldLeft']),
        Paragraph(application.applicant.get_full_name(), styles['Left']),
        Paragraph('Lodgement Number:', styles['BoldLeft']),
        Paragraph('{}-{}'.format(application.lodgement_number, application.lodgement_sequence), styles['Left'])
    ]

    address = application.applicant_profile.postal_address
    address_paragraphs = [Paragraph(address.line1, styles['Left']), Paragraph(address.line2, styles['Left']),
                          Paragraph(address.line3, styles['Left']),
                          Paragraph('%s %s %s' % (address.locality, address.state, address.postcode), styles['Left']),
                          Paragraph(address.country.name, styles['Left'])]

    bottow_row = [
        Paragraph('Address:', styles['BoldLeft']),
        address_paragraphs,
        Paragraph('Lodgement Date:', styles['BoldLeft']),
        Paragraph(application.lodgement_date.strftime(DATE_FORMAT), styles['Left'])
    ]

    left_heading_cell_width = 60
    right_heading_cell_width = 110
    value_cell_width = (PAGE_WIDTH - (2 * PAGE_MARGIN) - (2 * left_heading_cell_width + right_heading_cell_width)) / 2

    return Table([top_row, bottow_row],
                 colWidths=[left_heading_cell_width, value_cell_width, right_heading_cell_width, value_cell_width],
                 style=metadata_table_style)


def create_application_pdf_bytes(application):
    application_buffer = BytesIO()

    _create_application(application_buffer, application)

    # Get the value of the BytesIO buffer
    value = application_buffer.getvalue()
    application_buffer.close()

    return value
