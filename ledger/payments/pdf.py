import os

from io import BytesIO
from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, ListFlowable, \
    KeepTogether, PageBreak, Flowable, NextPageTemplate, FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from svglib.svglib import svg2rlg

from django.core.files import File
from django.conf import settings

from wildlifelicensing.apps.main.helpers import render_user_name

from ledger.accounts.models import Document

DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'ledger', 'payments','static', 'payments', 'img',
                                'dpaw_logo.png')

BPAY_LOGO = os.path.join(settings.BASE_DIR, 'media', 'BPAY_2012_PORT_BLUE.png')

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

class BrokenLine(Flowable):

    def __init__(self, width,height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def __repr__(self):
        return 'Line {}'.format(self.width)

    def draw(self):
        self.canv.setDash(3,3)
        self.canv.line(0, self.height,self.width,self.height)

class Remittance(Flowable):
    def __init__(self,current_x,current_y,invoice):
        Flowable.__init__(self)
        self.current_x = current_x
        self.current_y = current_y
        self.invoice = invoice

    def __repr__(self):
        return 'remittance'
    
    def __logo_line(self):
        canvas = self.canv
        current_y, current_x = self.current_y, self.current_x
        canvas.setFont(DEFAULT_FONTNAME, MEDIUM_FONTSIZE)
        dpaw_header_logo = ImageReader(DPAW_HEADER_LOGO)

        #dpaw_header_logo = svg2rlg(str(DPAW_HEADER_LOGO))
        dpaw_header_logo_size = dpaw_header_logo.getSize()
        canvas.drawImage(dpaw_header_logo, HEADER_MARGIN, current_y - (dpaw_header_logo_size[1]/1.5),height=dpaw_header_logo_size[1]/1.5, mask='auto', width=dpaw_header_logo_size[0]/1.5)
        
        current_y = -20
        canvas.setFont(BOLD_FONTNAME, MEDIUM_FONTSIZE)
        canvas.drawRightString(current_x * 45,current_y,'Remittance Advice')
        
        current_y -= 20
        canvas.setFont(DEFAULT_FONTNAME, MEDIUM_FONTSIZE)
        canvas.drawString(current_x * 27,current_y,'PLEASE DETACH AND RETURN WITH YOUR PAYMENT')
        
        current_y -= 20
        canvas.setFont(DEFAULT_FONTNAME, MEDIUM_FONTSIZE)
        canvas.drawString(current_x, current_y, 'ABN: 38 052 249 024')
        
    
    def __payment_line(self):
        canvas = self.canv
        current_y, current_x = self.current_y, self.current_x
        bpay_logo = ImageReader(BPAY_LOGO)
        current_y -= 40
        # Pay By Cheque
        cheque_x = current_x + 4 * inch
        cheque_y = current_y -50
        canvas.setFont(BOLD_FONTNAME, MEDIUM_FONTSIZE)
        canvas.drawString(cheque_x, cheque_y, 'Pay By Cheque:')
        canvas.setFont(DEFAULT_FONTNAME, 9)
        cheque_y -= 15
        canvas.drawString(cheque_x, cheque_y, 'Make cheque payable to: Department of Parks and Wildlife')
        cheque_y -= 15
        canvas.drawString(cheque_x, cheque_y, 'Mail to: Department of Parks and Wildlife')
        
        
        # Outer BPAY Box
        canvas.rect(current_x,current_y - 40,2.3*inch,-1.2*inch)
        canvas.setFillColorCMYK(0.8829,0.6126,0.0000,0.5647)
        # Move into bpay box
        current_y -= 10
        box_pos = current_x + 0.1 * inch
        bpay_logo_size = bpay_logo.getSize()
        canvas.drawImage(bpay_logo, box_pos, current_y - (bpay_logo_size[1]/12 * 1.7), height= bpay_logo_size[1]/12,width=bpay_logo_size[0]/12, mask='auto')
        # Create biller information box
        biller_x = box_pos + bpay_logo_size[0]/12 + 1
        canvas.rect(biller_x,(current_y - (bpay_logo_size[1]/12 * 1.7)) + 3,1.65*inch,(bpay_logo_size[1]/12)-5)
        # Bpay info
        canvas.setFont(BOLD_FONTNAME, MEDIUM_FONTSIZE)
        info_y = ((current_y - (bpay_logo_size[1]/12 * 1.7)) + 3) + (0.35 * inch)
        canvas.drawString(biller_x + 5, info_y, 'Biller Code: {}'.format(self.invoice.biller_code))
        canvas.drawString(biller_x + 5, info_y - 20, 'Ref: {}'.format(self.invoice.reference))
        # Bpay Info string
        canvas.setFont(BOLD_FONTNAME,SMALL_FONTSIZE)
        canvas.drawString(box_pos, info_y - 0.55 * inch, 'Telephone & Internet Banking - BPAY')
        canvas.setFont(DEFAULT_FONTNAME,6.5)
        canvas.drawString(box_pos, info_y - 0.65 * inch, 'Contact your bank or financial institution to make')
        canvas.drawString(box_pos, info_y - 0.75 * inch, 'this payment from your cheque, savings, debit or')
        canvas.drawString(box_pos, info_y - 0.85 * inch, 'transaction account. More info: www.bpay.com.au')
    
    def __footer_line(self):
        pass
    
    def draw(self):
        self.__logo_line()
        self.__payment_line()


def _create_header(canvas, doc, draw_page_number=True):
    canvas.saveState()
    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y = PAGE_HEIGHT - HEADER_MARGIN

    dpaw_header_logo = ImageReader(DPAW_HEADER_LOGO)

    #dpaw_header_logo = svg2rlg(str(DPAW_HEADER_LOGO))
    dpaw_header_logo_size = dpaw_header_logo.getSize()

    canvas.drawImage(dpaw_header_logo, PAGE_WIDTH / 3, current_y - dpaw_header_logo_size[1],height=dpaw_header_logo_size[1], mask='auto')

    current_y -= 60
    canvas.drawCentredString(PAGE_WIDTH / 2, current_y - LARGE_FONTSIZE, 'TAX INVOICE')

    current_y -= 20
    canvas.drawCentredString(PAGE_WIDTH / 2, current_y - LARGE_FONTSIZE, 'ABN: 38 052 249 024')

    # Invoice address details
    invoice_details_offset = 30
    current_y -= 20
    current_x = HEADER_MARGIN + 471
    invoice = doc.invoice
    #write Invoice details
    canvas.setFont(BOLD_FONTNAME, SMALL_FONTSIZE)
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER),'Date')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER),invoice.created.strftime(DATE_FORMAT))
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'Page')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2,str(canvas.getPageNumber()))
    canvas.drawRightString(current_x + 20, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, 'Invoice Number')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, invoice.reference)
    canvas.drawRightString(current_x + 20, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, 'Total(AUD)')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, str(invoice.amount))
    canvas.restoreState()
    
def _create_invoice(invoice_buffer, invoice):
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN + 300, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT -485 , id='EveryPagesFrame',showBoundary=0)
    remit_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 550, id='RemitFrame',showBoundary=0)
    every_page_template = PageTemplate(id='EveryPages', frames=[every_page_frame,remit_frame], onPage=_create_header)
    

    doc = BaseDocTemplate(invoice_buffer, pageTemplates=[every_page_template], pagesize=A4)
    

    # this is the only way to get data into the onPage callback function
    doc.invoice = invoice
    owner = invoice.owner

    elements = []
    #elements.append(Spacer(1, SECTION_BUFFER_HEIGHT * 5))

    # Draw Products Table
    invoice_table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID',(0, 0), (-1, -1),1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
        ])
    items = invoice.order.lines.all()
    data = [
        ['Item','Product', 'Quantity','Unit Price','GST', 'Amount']
    ]
    val = 1
    for item in items:
        data.append(
            [
                val,
                item.description,
                item.quantity,
                item.line_price_before_discounts_excl_tax,
                (item.line_price_before_discounts_incl_tax-item.line_price_before_discounts_excl_tax),
                item.line_price_before_discounts_incl_tax
            ]
        )
        val += 1
    t= Table(
            data,
            style=invoice_table_style,
            hAlign='LEFT'
        )
    t._argW[1] = 2.3 * inch
    for x in range (2,6):
        t._argW[x] = 1.2 * inch
    elements.append(t)
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT * 2))
    # /Products Table
    elements.append(Paragraph('Your aplication cannot be processed until payment is received.', styles['Left']))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT * 6))
    
    # Remitttance Frame
    elements.append(FrameBreak())
    boundary = BrokenLine(PAGE_WIDTH - 2 * (PAGE_MARGIN *1.1))
    elements.append(boundary)
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    
    remittance = Remittance(HEADER_MARGIN,HEADER_MARGIN - 10,invoice)
    elements.append(remittance)
    #_create_remittance(invoice_buffer,doc)
    doc.build(elements)
    
    return invoice_buffer

def create_invoice_pdf_bytes(filename, invoice):
    invoice_buffer = BytesIO()

    _create_invoice(invoice_buffer, invoice)

    # Get the value of the BytesIO buffer
    value = invoice_buffer.getvalue()
    invoice_buffer.close()

    return value