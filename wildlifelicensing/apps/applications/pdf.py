from io import BytesIO

from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


PAGE_WIDTH, PAGE_HEIGHT = A4

DEFAULT_FONTNAME = 'Helvetica'
BOLD_FONTNAME = 'Helvetica-Bold'
ITALIC_FONTNAME = 'Helvetica-Oblique'
BOLD_ITALIC_FONTNAME = 'Helvetica-BoldOblique'

VERY_LARGE_FONTSIZE = 16
LARGE_FONTSIZE = 14
MEDIUM_FONTSIZE = 12
SMALL_FONTSIZE = 10

PARAGRAPH_INDENT = 15
PARAGRAPH_BOTTOM_MARGIN = 2

SECTION_BUFFER_HEIGHT = 10

HEADER_MARGIN = 10

PAGE_MARGIN = 20
PAGE_TOP_MARGIN = 200

DATE_FORMAT = '%d/%m/%Y'

MISSING_VALUE_PLACEHOLDER = 'Not specified'
MISSING_FILE_PLACEHOLDER = 'No file attachment provided'


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='ApplicationTitle', fontName=BOLD_FONTNAME, fontSize=VERY_LARGE_FONTSIZE,
                          spaceAfter=HEADER_MARGIN, alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='ApplicationVariantsTitle', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE,
                          spaceAfter=PARAGRAPH_BOTTOM_MARGIN * 2, alignment=enums.TA_CENTER))

styles.add(ParagraphStyle(name='BoldLeft', fontName=BOLD_FONTNAME, fontSize=SMALL_FONTSIZE, alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='Left', alignment=enums.TA_LEFT))


def _create_application(application_buffer, application):
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN, PAGE_HEIGHT - 2 * PAGE_MARGIN,
                             id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=[every_page_frame])

    doc = BaseDocTemplate(application_buffer, pageTemplates=[every_page_template], pagesize=A4)

    elements = []

    elements.append(Paragraph(application.licence_type.name.encode('UTF-8'), styles['ApplicationTitle']))

    # cannot use licence get_title_with_variants because licence isn't saved yet so can't get variants
    if application.variants.exists():
        variants = '({})'.format(' / '.join(application.variants.all().values_list('name', flat=True)))
        elements.append(Paragraph(variants, styles['ApplicationVariantsTitle']))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    elements.append(_create_application_metadata(application))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    for field, datum in zip(application.licence_type.application_schema, application.data):
        _create_application_questionaire(field, datum, elements, 0)

    doc.build(elements)

    return application_buffer


def _create_application_metadata(application):
    # dates and licensing officer
    metadata_table_style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])

    licensee = application.applicant.get_full_name()
    lodgement_number = application.reference

    top_row = [
        Paragraph('Licensee:', styles['BoldLeft']),
        Paragraph(licensee, styles['Left']),
        Paragraph('Lodgement Number:', styles['BoldLeft']),
        Paragraph(lodgement_number, styles['Left'])
    ]

    address = application.applicant_profile.postal_address
    address_paragraphs = [Paragraph(address.line1, styles['Left']), Paragraph(address.line2, styles['Left']),
                          Paragraph(address.line3, styles['Left']),
                          Paragraph('%s %s %s' % (address.locality, address.state, address.postcode), styles['Left']),
                          Paragraph(address.country.name, styles['Left'])]

    lodgement_date = application.lodgement_date.strftime(DATE_FORMAT) if application.lodgement_date is not None else ''

    bottow_row = [
        Paragraph('Address:', styles['BoldLeft']),
        address_paragraphs,
        Paragraph('Lodgement Date:', styles['BoldLeft']),
        Paragraph(lodgement_date, styles['Left'])
    ]

    left_heading_cell_width = 60
    right_heading_cell_width = 110
    value_cell_width = 140

    return Table([top_row, bottow_row],
                 colWidths=[left_heading_cell_width, value_cell_width, right_heading_cell_width, value_cell_width],
                 style=metadata_table_style)


def _format_field_value(field, value):
    if field['type'] in ['radiobuttons', 'select']:
        return value.title() if value else MISSING_VALUE_PLACEHOLDER
    elif field['type'] == 'declaration':
        return 'Declaration checked' if value == 'on' else 'Declaration not checked'
    elif field['type'] == 'checkbox':
        return 'Yes' if value == 'on' else 'No'
    elif field['type'] == 'file':
        return value if value else MISSING_FILE_PLACEHOLDER
    else:
        return value if value else MISSING_VALUE_PLACEHOLDER


def _create_application_questionaire(field, data, elements, indent_index):
    paragraph_style = ParagraphStyle('', spaceAfter=PARAGRAPH_BOTTOM_MARGIN, leftIndent=indent_index * PARAGRAPH_INDENT)
    if field['type'] == 'section':
        paragraph_style.fontName = BOLD_FONTNAME
        paragraph_style.fontSize = LARGE_FONTSIZE
        elements.append(Paragraph('<u>{}</u>'.format(field['label']), paragraph_style))

        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        for child_data in data[field['name']]:
            for child_field in field['children']:
                _create_application_questionaire(child_field, child_data, elements, indent_index)
    elif field['type'] == 'group':
        paragraph_style.fontName = BOLD_FONTNAME
        paragraph_style.fontSize = MEDIUM_FONTSIZE

        # only append the number to the group title if there is more than one group
        show_group_number = len(data.get(field['name'], [])) > 1
        for group_index, child_data in enumerate(data.get(field['name'], [])):
            group_label = '{} {}'.format(field['label'], group_index + 1) if show_group_number else field['label']
            elements.append(Paragraph(group_label, paragraph_style))

            elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

            for child_field in field['children']:
                _create_application_questionaire(child_field, child_data, elements, indent_index + 1)
    else:
        paragraph_style.fontName = BOLD_FONTNAME
        elements.append(Paragraph(field['label'], paragraph_style))

        paragraph_style.fontName = DEFAULT_FONTNAME
        formatted_value = _format_field_value(field, data.get(field['name'], ''))
        elements.append(Paragraph(formatted_value, paragraph_style))

        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        # fields with conditional children
        if 'conditions' in field and data.get(field['name']) in field['conditions']:
            for child_field in field['conditions'][data.get(field['name'])]:
                _create_application_questionaire(child_field, data, elements, indent_index + 1)


def create_application_pdf_bytes(application):
    application_buffer = BytesIO()

    _create_application(application_buffer, application)

    # Get the value of the BytesIO buffer
    value = application_buffer.getvalue()
    application_buffer.close()

    return value
