import os
from django.conf import settings
from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from parkstay.models import Booking


LICENCE_HEADER_IMAGE_WIDTH = 840
LICENCE_HEADER_IMAGE_HEIGHT = 166
DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'parkstay', 'static', 'ps', 'img', 'parkstay_header.png')
DPAW_BUSINESS = 'Parks and Visitor Services'
DPAW_EMAIL = 'campgrounds@dpaw.wa.gov.au'
DPAW_URL = 'https://parks.dpaw.wa.gov.au'
DPAW_PHONE = '(08) 9219 9000'
DPAW_FAX = '(08) 9423 8242'
DPAW_PO_BOX = 'Locked Bag 104, Bentley Delivery Centre, Western Australia 6983'
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
LETTER_IMAGE_WIDTH = LICENCE_HEADER_IMAGE_WIDTH / 3.0
LETTER_IMAGE_HEIGHT = LICENCE_HEADER_IMAGE_HEIGHT / 3.0
LETTER_HEADER_RIGHT_LABEL_OFFSET = 400
LETTER_HEADER_RIGHT_INFO_OFFSET = 450
LETTER_HEADER_SMALL_BUFFER = 5
LETTER_ADDRESS_BUFFER_HEIGHT = 40
LETTER_BLUE_FONT = 0x045690

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
styles.add(ParagraphStyle(name='ItalicRight', fontName=ITALIC_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_RIGHT))
styles.add(ParagraphStyle(name='Center', alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='Left', alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='Right', alignment=enums.TA_RIGHT))
styles.add(ParagraphStyle(name='LetterLeft', fontSize=LARGE_FONTSIZE, alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='LetterBoldLeft', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE, alignment=enums.TA_LEFT))


def _create_letter_header_footer(canvas, doc):
    # header
    current_y = PAGE_HEIGHT - LETTER_HEADER_MARGIN

    dpaw_header_logo = ImageReader(DPAW_HEADER_LOGO)
    canvas.drawImage(dpaw_header_logo, LETTER_HEADER_MARGIN, current_y - LETTER_IMAGE_HEIGHT,
                     width=LETTER_IMAGE_WIDTH, height=LETTER_IMAGE_HEIGHT)


def create_confirmation(confirmation_buffer, booking):
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=every_page_frame, onPage=_create_letter_header_footer)

    doc = BaseDocTemplate(confirmation_buffer, pageTemplates=[every_page_template], pagesize=A4)

    elements = []

    elements.append(Paragraph('BOOKING CONFIRMATION', styles['InfoTitleVeryLargeCenter']))

    table_data = []
    table_data.append([Paragraph('Campground', styles['BoldLeft']), Paragraph('{}, {}'.format(booking.campground.name, booking.campground.park.name), styles['BoldLeft'])])

    if booking.first_campsite_list:
        campsites = []
        if booking.campground.site_type == 0:
            for item in booking.first_campsite_list:
                campsites.append(item.name if item else "")
        elif booking.campground.site_type == 1 or 2:
            for item in booking.first_campsite_list:
                campsites.append(item.type.split(':', 1)[0] if item else "")
        campsite = ', '.join(campsites)
        result = {x: campsites.count(x) for x in campsites}
        for key, value in result.items():
            campsite = ', '.join(['%sx %s' % (value, key) for (key, value) in result.items()])

    table_data.append([Paragraph('Camp Site', styles['BoldLeft']), Paragraph(campsite, styles['Left'])])

    table_data.append([Paragraph('Dates', styles['BoldLeft']), Paragraph(booking.stay_dates, styles['Left'])])
    table_data.append([Paragraph('Number of guests', styles['BoldLeft']), Paragraph(booking.stay_guests, styles['Left'])])
    table_data.append([Paragraph('Name', styles['BoldLeft']), Paragraph(u'{} {} ({})'.format(booking.details.get('first_name', ''), booking.details.get('last_name', ''), booking.customer.email if booking.customer else None), styles['Left'])])
    table_data.append([Paragraph('Booking confirmation number', styles['BoldLeft']), Paragraph(booking.confirmation_number, styles['Left'])])

    if booking.vehicle_payment_status:
        vehicle_data = []
        for r in booking.vehicle_payment_status:
            data = [Paragraph(r['Type'], styles['Left']), Paragraph(r['Rego'], styles['Left'])]
            if r.get('Paid') is not None:
                if r['Paid'] == 'Yes':
                    data.append(Paragraph('Entry fee paid', styles['Left']))
                elif r['Paid'] == 'No':
                    data.append(Paragraph('Unpaid', styles['Left']))
                elif r['Paid'] == 'pass_required':
                    data.append(Paragraph('Park Pass Required', styles['Left']))
            vehicle_data.append(data)

        vehicles = Table(vehicle_data, style=TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        table_data.append([Paragraph('Vehicles', styles['BoldLeft']), vehicles])
    else:
        table_data.append([Paragraph('Vehicles', styles['BoldLeft']), Paragraph('No vehicles', styles['Left'])])

    if booking.campground.additional_info:
        table_data.append([Paragraph('Additional confirmation information', styles['BoldLeft']), Paragraph(booking.campground.additional_info, styles['Left'])])

    elements.append(Table(table_data, colWidths=(200, None), style=TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])))

    doc.build(elements)
    return confirmation_buffer


def test():
    import tempfile
    import subprocess

    b = Booking.objects.get(id=34901)

    t = tempfile.NamedTemporaryFile()
    create_confirmation(t, b)
    t.flush()
    subprocess.call(['evince', t.name])
    t.close()
