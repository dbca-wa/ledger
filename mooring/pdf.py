import os
from io import BytesIO
import calendar
from datetime import datetime, date, timedelta
from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, ListFlowable, KeepTogether, PageBreak, Image, ImageAndFlowables
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

from django.core.files import File
from django.conf import settings

from mooring.models import Booking, BookingVehicleRego, AdmissionsBooking

DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'mooring', 'static', 'mooring','img','mooring_header.png')

LICENCE_HEADER_IMAGE_WIDTH = 840
LICENCE_HEADER_IMAGE_HEIGHT = 166

DPAW_BUSINESS = ''
DPAW_EMAIL = ''
DPAW_URL = ''
DPAW_PHONE = ''
DPAW_FAX = ''
DPAW_PO_BOX = ''


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
LETTER_IMAGE_WIDTH = LICENCE_HEADER_IMAGE_WIDTH/3.0
LETTER_IMAGE_HEIGHT = LICENCE_HEADER_IMAGE_HEIGHT/3.0
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

    # footer
    current_x = PAGE_WIDTH - LETTER_HEADER_MARGIN
    current_y = LETTER_HEADER_MARGIN

    #canvas.setFont(DEFAULT_FONTNAME, SMALL_FONTSIZE)
    #canvas.setFillColor(HexColor(LETTER_BLUE_FONT))

    #canvas.drawRightString(current_x, current_y, DPAW_URL)
    #canvas.drawRightString(current_x, current_y + SMALL_FONTSIZE,
    #                       'Phone: {} Fax: {} Email: {}'.format(DPAW_PHONE, DPAW_FAX, DPAW_EMAIL))
    #canvas.drawRightString(current_x, current_y + SMALL_FONTSIZE * 2, DPAW_PO_BOX)

    #canvas.setFont(BOLD_ITALIC_FONTNAME, SMALL_FONTSIZE)

    #canvas.drawRightString(current_x, current_y + SMALL_FONTSIZE * 3, DPAW_BUSINESS)


def create_confirmation(confirmation_buffer, booking, mooring_bookings):
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=every_page_frame, onPage=_create_letter_header_footer)

    doc = BaseDocTemplate(confirmation_buffer, pageTemplates=[every_page_template], pagesize=A4)

    elements = []

    elements.append(Paragraph('BOOKING CONFIRMATION', styles['InfoTitleVeryLargeCenter']))

    #im = Image(os.path.join(settings.BASE_DIR, 'mooring', 'static', 'ps', 'img', 'placeholder.jpg'))
    #text1 = Paragraph('But they had not gone twenty yards when they stopped short. An uproar of voices was coming from the farmhouse. They rushed back and looked through the window again. Yes, a violent quarrel was in progress. There were shoutings, bangings on the table, sharp suspicious glances, furious denials. The source of the trouble appeared to be that Napoleon and Mr. Pilkington had each played an ace of spades simultaneously.', styles['Left'])
    #text2 = Paragraph('Twelve voices were shouting in anger, and they were all alike. No question, now, what had happened to the faces of the pigs. The creatures outside looked from pig to man, and from man to pig, and from pig to man again; but already it was impossible to say which was which.', styles['Left'])

    #elements.append(ImageAndFlowables(im, [text1, text2], imageSide='left'))
    table_data = []

    lines = []
    from_date = ""
    to_date = ""
    for i, mb in enumerate(mooring_bookings):
        start = mb.from_dt
        timestamp = calendar.timegm(start.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        start = local_dt.replace(microsecond=start.microsecond)
        start = start.strftime('%d/%m/%Y %H:%M')
        end = mb.to_dt
        timestamp = calendar.timegm(end.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        end = local_dt.replace(microsecond=end.microsecond)
        end_str = end.strftime('%d/%m/%Y %H:%M')
        
        if from_date == "":
            from_date = start
        if i == len(mooring_bookings)-1:
            to_date = end_str
        else:
            next_dt = mooring_bookings[i+1].from_dt
            timestamp = calendar.timegm(next_dt.timetuple())
            local_dt = datetime.fromtimestamp(timestamp)
            next_dt = local_dt.replace(microsecond=next_dt.microsecond)
            next_str = next_dt.strftime('%d/%m/%Y %H:%M')
            if (end + timedelta(minutes=1)) == next_dt and mb.campsite.mooringarea.name == mooring_bookings[i+1].campsite.mooringarea.name:
                #Go to next booking
                to_date = ""
            else:
                to_date = end_str
        if to_date > "":
            lines.append({'from': from_date, 'to':to_date, 'mooring': mb.campsite.mooringarea.name, 'park': mb.campsite.mooringarea.park.name})
            from_date = ""
            to_date = ""

    for i, line in enumerate(lines):
        table_data.append([Paragraph('Mooring {}'.format(i+1), styles['BoldLeft']), Paragraph('{}, {}'.format(line['mooring'], line['park']), styles['BoldLeft'])])
        # campsite = u'{}'.format(booking.first_campsite.type) if booking.mooringarea.site_type == 2 else u'{} ({})'.format(booking.first_campsite.name, booking.first_campsite.type)
    #   table_data.append([Paragraph('Camp Site', styles['BoldLeft']), Paragraph(campsite, styles['Left'])])
        days = (datetime.strptime(line['to'], '%d/%m/%Y %H:%M').date() - datetime.strptime(line['from'], '%d/%m/%Y %H:%M').date()).days
        if days == 0:
            days = 1
        plural = 's' if days > 1 else ''
        table_data.append([Paragraph('Dates', styles['BoldLeft']), Paragraph('{} to {} ({} day{})'.format(line['from'], line['to'], days, plural), styles['Left'])])
        

#    table_data.append([Paragraph('Number of guests', styles['BoldLeft']), Paragraph(booking.stay_guests, styles['Left'])])
    table_data.append([Paragraph('Name', styles['BoldLeft']), Paragraph(u'{} {} ({})'.format(booking.details.get('first_name', ''), booking.details.get('last_name', ''), booking.customer.email if booking.customer else None), styles['Left'])])
    table_data.append([Paragraph('Booking confirmation number', styles['BoldLeft']), Paragraph(booking.confirmation_number, styles['Left'])])

    if booking.vehicle_payment_status:
        vehicle_data = []
        rego = ""
        for r in booking.vehicle_payment_status:
            data = [Paragraph(r['Rego'], styles['Left'])]
            rego = r['Rego']
            if r.get('Paid') != None:
                if r['Paid'] == 'Yes':
                    data.append(Paragraph('Entry fee paid', styles['Left']))
                elif r['Paid'] == 'No':
                    data.append(Paragraph('Unpaid', styles['Left']))
                elif r['Paid'] == 'pass_required':
                    pass
                    #data.append(Paragraph('Marina Pass Required', styles['Left']))
            vehicle_data.append(data)

            
        vehicles = Table(vehicle_data, style=TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        table_data.append([Paragraph('Vessel', styles['BoldLeft']), rego])
    else:
        table_data.append([Paragraph('Vessel', styles['BoldLeft']), Paragraph('No vessel', styles['Left'])])
        
    if booking.mooringarea.additional_info:        
        table_data.append([Paragraph('Additional confirmation information', styles['BoldLeft']), Paragraph(booking.mooringarea.additional_info, styles['Left'])])

    elements.append(Table(table_data, colWidths=(200, None), style=TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])))

    doc.build(elements)
    return confirmation_buffer

def create_admissions_confirmation(confirmation_buffer, admissionsBooking):
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=every_page_frame, onPage=_create_letter_header_footer)

    doc = BaseDocTemplate(confirmation_buffer, pageTemplates=[every_page_template], pagesize=A4)

    overnightStay = ""
    if(admissionsBooking.overnightStay):
        overnightStay = "Yes"
    else:
        overnightStay = "No"

    elements = []

    elements.append(Paragraph('ADMISSIONS BOOKING CONFIRMATION', styles['InfoTitleVeryLargeCenter']))
   
    table_data = []
    table_data.append([Paragraph('Date', styles['BoldLeft']), Paragraph(u'{}'.format(admissionsBooking.arrivalDate), styles['Left'])])
    table_data.append([Paragraph('Name', styles['BoldLeft']), Paragraph(u'{} ({})'.format(admissionsBooking.customer.get_full_name(), admissionsBooking.customer.email if admissionsBooking.customer else None), styles['Left'])])
    table_data.append([Paragraph('Booking confirmation number', styles['BoldLeft']), Paragraph(admissionsBooking.confirmation_number, styles['Left'])])
    table_data.append([Paragraph('Overnight Stay', styles['BoldLeft']), Paragraph(u'{}'.format(overnightStay), styles['Left'])])
    table_data.append([Paragraph('Total paid for attendees', styles['BoldLeft']), Paragraph(u'{}'.format(admissionsBooking.total_admissions), styles['Left'])])
    if admissionsBooking.noOfAdults > 0:
        table_data.append([Paragraph('Adults', styles['BoldLeft']), Paragraph(u'{}'.format(admissionsBooking.noOfAdults), styles['Left'])])
    if admissionsBooking.noOfConcessions > 0:
        table_data.append([Paragraph('Concessions', styles['BoldLeft']), Paragraph(u'{}'.format(admissionsBooking.noOfConcessions), styles['Left'])])
    if admissionsBooking.noOfChildren > 0:
        table_data.append([Paragraph('Children', styles['BoldLeft']), Paragraph(u'{}'.format(admissionsBooking.noOfChildren), styles['Left'])])
    if admissionsBooking.noOfInfants > 0:
        table_data.append([Paragraph('Infants', styles['BoldLeft']), Paragraph(u'{}'.format(admissionsBooking.noOfInfants), styles['Left'])])
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
