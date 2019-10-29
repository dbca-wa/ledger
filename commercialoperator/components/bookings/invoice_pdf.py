import os

from decimal import Decimal as D
from io import BytesIO
from oscar.templatetags.currency_filters import currency
from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, ListFlowable, \
    KeepTogether, PageBreak, Flowable, NextPageTemplate, FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from reportlab.lib import colors

from django.core.files import File
from django.conf import settings

from ledger.accounts.models import Document
from ledger.checkout.utils import calculate_excl_gst

DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'ledger', 'payments','static', 'payments', 'img','dbca_logo.jpg')
DPAW_HEADER_LOGO_SM = os.path.join(settings.BASE_DIR, 'ledger', 'payments','static', 'payments', 'img','dbca_logo_small.png')
BPAY_LOGO = os.path.join(settings.BASE_DIR, 'ledger', 'payments','static', 'payments', 'img', 'BPAY_2012_PORT_BLUE.png')

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
styles.add(ParagraphStyle(name='LongString', alignment=enums.TA_LEFT,wordWrap='CJK'))

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
    def __init__(self, current_x, current_y, proposal, invoice):
        Flowable.__init__(self)
        self.current_x = current_x
        self.current_y = current_y
        self.proposal = proposal
        self.invoice = invoice

    def __repr__(self):
        return 'remittance'

    def __logo_line(self):
        canvas = self.canv
        current_y, current_x = self.current_y, self.current_x
        canvas.setFont(DEFAULT_FONTNAME, MEDIUM_FONTSIZE)
        dpaw_header_logo = ImageReader(DPAW_HEADER_LOGO_SM)

        dpaw_header_logo_size = dpaw_header_logo.getSize()
        canvas.drawImage(dpaw_header_logo, HEADER_MARGIN, current_y - (dpaw_header_logo_size[1]/1.8),height=dpaw_header_logo_size[1]/1.8, mask='auto', width=dpaw_header_logo_size[0]/1.8)

        current_y = -20
        canvas.setFont(BOLD_FONTNAME, MEDIUM_FONTSIZE)
        canvas.drawRightString(current_x * 45,current_y,'Remittance Advice')

        #current_y -= 20
        #canvas.setFont(DEFAULT_FONTNAME, MEDIUM_FONTSIZE)
        #canvas.drawString(current_x * 27,current_y,'PLEASE DETACH AND RETURN WITH YOUR PAYMENT')

        current_y -= 50
        canvas.setFont(DEFAULT_FONTNAME, MEDIUM_FONTSIZE)
        canvas.drawString(current_x, current_y, 'ABN: 38 052 249 024')
        self.current_y = current_y

    def __payment_line(self):
        canvas = self.canv
        current_y, current_x = self.current_y, self.current_x
        bpay_logo = ImageReader(BPAY_LOGO)
        #current_y -= 40
        # Pay By Cheque
        cheque_x = current_x + 4 * inch
        cheque_y = current_y - 10
        #canvas.setFont(BOLD_FONTNAME, MEDIUM_FONTSIZE)
        #canvas.drawString(cheque_x, cheque_y, 'Pay By Cheque:')
        #canvas.setFont(DEFAULT_FONTNAME, 9)
        #cheque_y -= 15
        #canvas.drawString(cheque_x, cheque_y, 'Make cheque payable to: Department of Parks and Wildlife')
        #cheque_y -= 15
        #canvas.drawString(cheque_x, cheque_y, 'Mail to: Department of Parks and Wildlife')
        #cheque_y -= 15
        #canvas.drawString(cheque_x + 32, cheque_y, 'Locked Bag 30')
        #cheque_y -= 15
        #canvas.drawString(cheque_x + 32, cheque_y, 'Bentley Delivery Centre WA 6983')
        if self.invoice.payment_method in [self.invoice.PAYMENT_METHOD_MONTHLY_INVOICING, self.invoice.PAYMENT_METHOD_BPAY]:
            # Outer BPAY Box
            canvas.rect(current_x,current_y - 25,2.3*inch,-1.2*inch)
            canvas.setFillColorCMYK(0.8829,0.6126,0.0000,0.5647)
            # Move into bpay box
            current_y += 5
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

        self.current_y = current_y

    def __footer_line(self):
        canvas = self.canv
        current_y, current_x = self.current_y, self.current_x
        current_y -= 2 * inch
        canvas.setFont(DEFAULT_FONTNAME, LARGE_FONTSIZE)
        canvas.setFillColor(colors.black)
        canvas.drawString(current_x, current_y, 'Invoice Number')
        canvas.drawString(PAGE_WIDTH/4, current_y, 'Invoice Date')
        canvas.drawString((PAGE_WIDTH/4) * 2, current_y, 'GST included')
        canvas.drawString((PAGE_WIDTH/4) * 3, current_y, 'Invoice Total')
        current_y -= 20
        canvas.setFont(DEFAULT_FONTNAME, MEDIUM_FONTSIZE)
        canvas.drawString(current_x, current_y, self.invoice.reference)
        canvas.drawString(PAGE_WIDTH/4, current_y, self.invoice.created.strftime(DATE_FORMAT))
        canvas.drawString((PAGE_WIDTH/4) * 2, current_y, currency(self.invoice.amount - calculate_excl_gst(self.invoice.amount) if not _is_gst_exempt(self.proposal, self.invoice) else 0.0))
        canvas.drawString((PAGE_WIDTH/4) * 3, current_y, currency(self.invoice.amount))

    def draw(self):
        #if settings.BPAY_ALLOWED:
        if self.invoice.payment_method in [self.invoice.PAYMENT_METHOD_MONTHLY_INVOICING, self.invoice.PAYMENT_METHOD_BPAY]:
            self.__logo_line()
            self.__payment_line()
        self.__footer_line()

#def _set_template_group(mooring_var):


#def get_template_group(mooring_var):



def _create_header(canvas, doc, draw_page_number=True):
    canvas.saveState()
    canvas.setTitle('Invoice')
    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y = PAGE_HEIGHT - HEADER_MARGIN

    dpaw_header_logo = ImageReader(DPAW_HEADER_LOGO)
    dpaw_header_logo_size = dpaw_header_logo.getSize()
    canvas.drawImage(dpaw_header_logo, PAGE_WIDTH / 3, current_y - (dpaw_header_logo_size[1]/2),width=dpaw_header_logo_size[0]/2, height=dpaw_header_logo_size[1]/2, mask='auto')

    current_y -= 70
    canvas.drawCentredString(PAGE_WIDTH / 2, current_y - LARGE_FONTSIZE, 'TAX INVOICE')

    current_y -= 20
    canvas.drawCentredString(PAGE_WIDTH / 2, current_y - LARGE_FONTSIZE, 'ABN: 38 052 249 024')

    # Invoice address details
    invoice_details_offset = 37
    current_y -= 10

    invoice = doc.invoice
    proposal = doc.proposal
    bi = proposal.bookings.filter(invoices__invoice_reference=invoice.reference)
    licence_number = proposal.approval.lodgement_number if proposal.approval else None

    # TODO need to fix, since individual parks can be exempt, Below calculation assumes NO PARK IS exempt
    #is_gst_exempt = proposal.application_type.is_gst_exempt if proposal.fee_invoice_reference == invoice.reference else False

    canvas.setFont(BOLD_FONTNAME, SMALL_FONTSIZE)
    current_x = PAGE_MARGIN + 5
    if proposal.org_applicant:
        canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER),    proposal.applicant)
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2,invoice.owner.get_full_name())
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3,invoice.owner.email)
    current_x += 452

    #write Invoice details
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER),'Date')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER),invoice.created.strftime(DATE_FORMAT))
    canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'Page')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, str(canvas.getPageNumber()))
    canvas.drawRightString(current_x + 20, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, 'Licence Number')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, licence_number)
    canvas.drawRightString(current_x + 20, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, 'Invoice Number')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, invoice.reference)
    canvas.drawRightString(current_x + 20, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5, 'Total (AUD)')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5, currency(invoice.amount))
    canvas.drawRightString(current_x + 20, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 6, 'GST included (AUD)')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 6, currency(invoice.amount - calculate_excl_gst(invoice.amount) if not _is_gst_exempt(proposal, invoice) else 0.0))
    canvas.drawRightString(current_x + 20, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 7, 'Paid (AUD)')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 7, currency(invoice.payment_amount))
    canvas.drawRightString(current_x + 20, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 8, 'Outstanding (AUD)')
    canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 8, currency(invoice.balance))

    if bi and bi[0].deferred_payment_date and invoice.payment_method in [invoice.PAYMENT_METHOD_MONTHLY_INVOICING, invoice.PAYMENT_METHOD_BPAY]:
        canvas.drawRightString(current_x + 20, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 9, 'Payment Due Date')
        canvas.drawString(current_x + invoice_details_offset, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 9, bi[0].deferred_payment_date.strftime(DATE_FORMAT))

    canvas.restoreState()

def _is_gst_exempt(proposal, invoice):
    # TODO need to fix, since individual parks can be exempt, Below calculation assumes NO PARK IS exempt
    return proposal.application_type.is_gst_exempt if proposal.fee_invoice_reference == invoice.reference else False

def _create_invoice(invoice_buffer, invoice, proposal):

    global DPAW_HEADER_LOGO
#    if  cols_var["TEMPLATE_GROUP"] == 'rottnest':
#        DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'mooring', 'static', 'mooring', 'img','logo-rottnest-island-sm.png')
#    else:
#        DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'ledger', 'payments','static', 'payments', 'img','dbca_logo.jpg')
    DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'ledger', 'payments','static', 'payments', 'img','dbca_logo.jpg')

    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN + 250, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT -450 , id='EveryPagesFrame',showBoundary=0)
    remit_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 600, id='RemitFrame',showBoundary=0)
    every_page_template = PageTemplate(id='EveryPages', frames=[every_page_frame,remit_frame], onPage=_create_header)


    doc = BaseDocTemplate(invoice_buffer, pageTemplates=[every_page_template], pagesize=A4)


    # this is the only way to get data into the onPage callback function
    doc.invoice = invoice
    doc.proposal = proposal
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
    discounts = invoice.order.basket_discounts
    if invoice.text:
        elements.append(Paragraph(invoice.text, styles['Left']))
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT * 2))
    data = [
        ['Item','Product', 'Quantity','Unit Price', 'Total']
    ]
    val = 1
    s = styles["BodyText"]
    s.wordWrap = 'CJK'

    for item in items:
        data.append(
            [
                val,
                Paragraph(item.description, s),
                item.quantity,
                currency(item.unit_price_incl_tax),
                currency(item.line_price_before_discounts_incl_tax)
            ]
        )
        val += 1
    # Discounts
    data.append(
        [
            '',
            '',
            '',
            ''
        ]
    )
    for discount in discounts:
        data.append(
            [
                '',
                discount.offer,
                '',
                '',
                '-${}'.format(discount.amount)
            ]
        )
        val += 1
    t= Table(
            data,
            style=invoice_table_style,
            hAlign='LEFT',
            colWidths=(
            0.7 * inch,
            None,
            0.7 * inch,
            1.0 * inch,
            1.0 * inch,
            )
        )
    elements.append(t)
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT * 2))
    # /Products Table
    if invoice.payment_status != 'paid' and invoice.payment_status != 'over_paid':
        elements.append(Paragraph(settings.INVOICE_UNPAID_WARNING, styles['Left']))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT * 6))

    # Remitttance Frame
    elements.append(FrameBreak())
    boundary = BrokenLine(PAGE_WIDTH - 2 * (PAGE_MARGIN *1.1))
    elements.append(boundary)
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    remittance = Remittance(HEADER_MARGIN,HEADER_MARGIN - 10, proposal, invoice)
    elements.append(remittance)
    #_create_remittance(invoice_buffer,doc)
    doc.build(elements)

    return invoice_buffer

def create_invoice_pdf_bytes(filename, invoice, proposal):
    invoice_buffer = BytesIO()
    _create_invoice(invoice_buffer, invoice, proposal)

    # Get the value of the BytesIO buffer
    value = invoice_buffer.getvalue()
    invoice_buffer.close()

    return value


