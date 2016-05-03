import os

from io import BytesIO
from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader

from django.conf import settings


DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'wildlifelicensing', 'static', 'wl', 'img', 'bw_dpaw_header_logo.png')

HEADER_MARGIN = 10
HEADER_SMALL_BUFFER = 3

PAGE_MARGIN = 20
PAGE_TOP_MARGIN = 200

PAGE_WIDTH, PAGE_HEIGHT = A4

DEFAULT_FONTNAME = 'Helvetica'
DEFAULT_FONTSIZE = 12

SMALL_FONTSIZE = 8


def _create_header(canvas, doc):
    canvas.setFont('Helvetica-Bold', DEFAULT_FONTSIZE)

    current_y = PAGE_HEIGHT - HEADER_MARGIN

    canvas.drawCentredString(PAGE_WIDTH / 2, current_y - DEFAULT_FONTSIZE, 'DEPARTMENT OF PARKS AND WILDLIFE')

    current_y -= 30

    dpaw_header_logo = ImageReader(DPAW_HEADER_LOGO)
    dpaw_header_logo_size = dpaw_header_logo.getSize()
    canvas.drawImage(dpaw_header_logo, HEADER_MARGIN, current_y - dpaw_header_logo_size[1])

    current_x = HEADER_MARGIN + dpaw_header_logo_size[0] + 5

    canvas.setFont('Helvetica', SMALL_FONTSIZE)

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER), 'Enquiries:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'Telephone:')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, 'Facsimile:')

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4 - HEADER_MARGIN, 'Correspondance:')

    current_x += 80

    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER), '17 DICK PERRY AVE, KENSINGTON, WESTERN AUSTRALIA')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, '08 9219 9000')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, '08 9219 8242')

    canvas.setFont('Helvetica-Bold', SMALL_FONTSIZE)
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4 - HEADER_MARGIN, 'Locked Bag 30')
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5 - HEADER_MARGIN, 'Bentley Delivery Centre WA 6983')

    canvas.setFont('Helvetica-Bold', DEFAULT_FONTSIZE)

    current_y -= 36
    current_x += 200

    canvas.drawString(current_x, current_y - (DEFAULT_FONTSIZE + HEADER_SMALL_BUFFER), 'PAGE')
    canvas.drawString(current_x, current_y - (DEFAULT_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'NO.')
    canvas.drawString(current_x - 54, current_y - (DEFAULT_FONTSIZE + HEADER_SMALL_BUFFER) * 3, 'PERSON NO.')

    canvas.setFont('Helvetica', DEFAULT_FONTSIZE)

    current_x += 50

    canvas.drawString(current_x, current_y - (DEFAULT_FONTSIZE + HEADER_SMALL_BUFFER), str(canvas.getPageNumber()))
    canvas.drawString(current_x, current_y - (DEFAULT_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'SF010807')
    canvas.drawString(current_x, current_y - (DEFAULT_FONTSIZE + HEADER_SMALL_BUFFER) * 3, '179911')


def create_licence_pdf(filename, licence, application):
    licence_buffer = BytesIO()

    # note to self, up to here, gotta figure out this margin stuff
    frame = Frame(PAGE_MARGIN, PAGE_HEIGHT, PAGE_WIDTH - 2 * PAGE_MARGIN,
                  PAGE_HEIGHT - 200 - PAGE_MARGIN, id='EveryPageFrame')
    every_page_template = PageTemplate(id='EveryPage', frames=frame, onPage=_create_header)

    doc = BaseDocTemplate(licence_buffer, pageTemplates=[every_page_template],
                          pagesize=A4)

    elements = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=enums.TA_CENTER))
    styles.add(ParagraphStyle(name='Right', alignment=enums.TA_RIGHT))

    elements.append(Paragraph(licence.licence_type.act, styles['Center']))
    elements.append(Paragraph(licence.licence_type.code.upper(), styles['Center']))
    elements.append(Paragraph(licence.licence_type.name, styles['Center']))
    elements.append(Paragraph(licence.licence_type.statement, styles['Center']))
    elements.append(Paragraph(licence.licence_type.authority, styles['Right']))

    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = licence_buffer.getvalue()
    licence_buffer.close()

    return pdf
