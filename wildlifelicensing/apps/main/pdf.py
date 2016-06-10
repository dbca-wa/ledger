import os

from io import BytesIO
from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader

from django.core.files import File
from django.conf import settings

from wildlifelicensing.apps.main.helpers import render_user_name

from ledger.accounts.models import Document

DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'wildlifelicensing', 'static', 'wl', 'img', 'bw_dpaw_header_logo.png')

HEADER_MARGIN = 10
HEADER_SMALL_BUFFER = 3

PAGE_MARGIN = 20
PAGE_TOP_MARGIN = 200

PAGE_WIDTH, PAGE_HEIGHT = A4

DEFAULT_FONTNAME = 'Helvetica'
BOLD_FONTNAME = 'Helvetica-Bold'

VERY_LARGE_FONTSIZE = 14
LARGE_FONTSIZE = 12
MEDIUM_FONTSIZE = 10
SMALL_FONTSIZE = 8

PARAGRAPH_BOTTOM_MARGIN = 5

SECTION_BUFFER_HEIGHT = 10

DATE_FORMAT = '%d/%m/%Y'


def _create_licence_header(canvas, doc):
    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y = PAGE_HEIGHT - HEADER_MARGIN

    canvas.drawCentredString(PAGE_WIDTH / 2, current_y - LARGE_FONTSIZE, 'DEPARTMENT OF PARKS AND WILDLIFE')

    current_y -= 30

    dpaw_header_logo = ImageReader(DPAW_HEADER_LOGO)
    dpaw_header_logo_size = dpaw_header_logo.getSize()
    canvas.drawImage(dpaw_header_logo, HEADER_MARGIN, current_y - dpaw_header_logo_size[1])

    current_x = HEADER_MARGIN + dpaw_header_logo_size[0] + 5

    canvas.setFont(DEFAULT_FONTNAME, SMALL_FONTSIZE)

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER), 'Enquiries:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'Telephone:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, 'Facsimile:')

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4 - HEADER_MARGIN, 'Correspondance:')

    current_x += 80

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER), '17 DICK PERRY AVE, KENSINGTON, WESTERN AUSTRALIA')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, '08 9219 9000')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, '08 9219 8242')

    canvas.setFont(BOLD_FONTNAME, SMALL_FONTSIZE)
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4 - HEADER_MARGIN, 'Locked Bag 30')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5 - HEADER_MARGIN, 'Bentley Delivery Centre WA 6983')

    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y -= 36
    current_x += 200

    canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER), 'PAGE')
    canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'NO.')

    canvas.setFont(DEFAULT_FONTNAME, LARGE_FONTSIZE)

    current_x += 50

    canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER), str(canvas.getPageNumber()))
    canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER) * 2, doc.licence.licence_no)


def _get_authorised_person_names(application):
    authorised_persons = []
    for ap in application.data.get('authorised_persons', []):
        if ap.get('ap_given_names') and ap.get('ap_given_names'):
            authorised_persons.append('%s %s' % (ap['ap_given_names'], ap['ap_surname']))

    return authorised_persons


def _create_licence(licence_buffer, licence, application):
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='OtherPagesFrame')
    every_page_template = PageTemplate(id='OtherPages', frames=every_page_frame, onPage=_create_licence_header)

    doc = BaseDocTemplate(licence_buffer, pageTemplates=[every_page_template],
                          pagesize=A4)

    # this is the only way to get data into the onPage callback function
    doc.licence = licence

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
    styles.add(ParagraphStyle(name='Center', alignment=enums.TA_CENTER))
    styles.add(ParagraphStyle(name='Left', alignment=enums.TA_LEFT))
    styles.add(ParagraphStyle(name='Right', alignment=enums.TA_RIGHT))

    licence_table_style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])

    elements = []

    elements.append(Paragraph(licence.licence_type.act, styles['InfoTitleLargeCenter']))
    elements.append(Paragraph(licence.licence_type.code.upper(), styles['InfoTitleLargeCenter']))
    elements.append(Paragraph(licence.licence_type.name, styles['InfoTitleVeryLargeCenter']))
    elements.append(Paragraph(licence.licence_type.statement, styles['InfoTitleLargeLeft']))
    elements.append(Paragraph(licence.licence_type.authority, styles['InfoTitleLargeRight']))

    # licence conditions
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('Conditions', styles['InfoTitleLargeCenter']))
    conditionList = ListFlowable([Paragraph(condition.text, styles['Left']) for condition in application.conditions.all()])
    elements.append(conditionList)

    # purpose
    if licence.purpose:
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        purposes = []
        for purpose in licence.purpose.split('\r\n'):
            if purpose:
                purposes.append(Paragraph(purpose, styles['Left']))
            else:
                purposes.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        elements.append(Table([[Paragraph('Purpose', styles['BoldLeft']), purposes]],
                              colWidths=(100, PAGE_WIDTH - (2 * PAGE_MARGIN) - 100),
                              style=licence_table_style))

    # authorised persons
    authorised_persons = _get_authorised_person_names(application)
    if len(authorised_persons) > 0:
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        authorized_persons = [Paragraph(ap, styles['Left']) for ap in authorised_persons]
        elements.append(Table([[Paragraph('Authorised Persons', styles['BoldLeft']), authorized_persons]],
                              colWidths=(100, PAGE_WIDTH - (2 * PAGE_MARGIN) - 100),
                              style=licence_table_style))

    # dates and licensing officer
    dates_licensing_officer_table_style = TableStyle([('VALIGN', (0, 0), (-2, -1), 'TOP'),
                                                      ('VALIGN', (0, 0), (-1, -1), 'BOTTOM')])

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Table([[[Paragraph('Date of Issue', styles['BoldLeft']), Paragraph('Valid From', styles['BoldLeft']),
                             Paragraph('Date of Expiry', styles['BoldLeft'])],
                            [Paragraph(licence.issue_date.strftime(DATE_FORMAT), styles['Left']),
                             Paragraph(licence.start_date.strftime(DATE_FORMAT), styles['Left']),
                             Paragraph(licence.end_date.strftime(DATE_FORMAT), styles['Left'])],
                            Paragraph('Licensing Officer', styles['BoldRight']),
                            ]],
                          colWidths=(100, PAGE_WIDTH - (2 * PAGE_MARGIN) - 200, 100),
                          style=dates_licensing_officer_table_style))

    # licensee details
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    address = application.applicant_profile.postal_address
    address_paragraphs = [Paragraph(address.line1, styles['Left']), Paragraph(address.line2, styles['Left']),
                          Paragraph(address.line3, styles['Left']),
                          Paragraph('%s %s %s' % (address.locality, address.state, address.postcode), styles['Left']),
                          Paragraph(address.country.name, styles['Left'])]
    elements.append(Table([[[Paragraph('Licensee:', styles['BoldLeft']), Paragraph('Address', styles['BoldLeft'])],
                            [Paragraph(render_user_name(application.applicant_profile.user), styles['Left'])] + address_paragraphs]],
                          colWidths=(100, PAGE_WIDTH - (2 * PAGE_MARGIN) - 100),
                          style=licence_table_style))

    doc.build(elements)

    return licence_buffer


def create_licence_pdf_document(filename, licence, application):
    licence_buffer = BytesIO()

    _create_licence(licence_buffer, licence, application)

    document = Document.objects.create(name=filename)
    document.file.save(filename, File(licence_buffer), save=True)

    licence_buffer.close()

    return document


def create_licence_pdf_bytes(filename, licence, application):
    licence_buffer = BytesIO()

    _create_licence(licence_buffer, licence, application)

    # Get the value of the BytesIO buffer
    value = licence_buffer.getvalue()
    licence_buffer.close()

    return value
