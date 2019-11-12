import os
from io import BytesIO
from datetime import date

from reportlab.lib import enums
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, ListFlowable, \
    KeepTogether, PageBreak, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, black

from django.core.files import File
from django.conf import settings
from django.core.exceptions import ValidationError

from commercialoperator.components.approvals.models import ApprovalDocument

#BW_DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'wildlifelicensing', 'static', 'wl', 'img',
#                                   'bw_dpaw_header_logo.png')

BW_DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'commercialoperator', 'static', 'commercialoperator', 'img',
                                   'dbca-logo.jpg')

COLOUR_DPAW_HEADER_LOGO = os.path.join(settings.BASE_DIR, 'wildlifelicensing', 'static', 'wl', 'img',
                                       'colour_dpaw_header_logo.png')

#LICENCE_HEADER_IMAGE_WIDTH = 170
LICENCE_HEADER_IMAGE_WIDTH = 320
#LICENCE_HEADER_IMAGE_HEIGHT = 42
LICENCE_HEADER_IMAGE_HEIGHT = 60

DPAW_EMAIL = settings.SUPPORT_EMAIL
DPAW_URL = settings.DEP_URL
DPAW_PHONE = settings.DEP_PHONE
DPAW_FAX = settings.DEP_FAX
DPAW_PO_BOX = settings.DEP_POSTAL


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
DATE_FORMAT2 = '%d %B %Y'

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
styles.add(ParagraphStyle(name='BoldCenter', fontName=BOLD_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='ItalicLeft', fontName=ITALIC_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='ItalifRight', fontName=ITALIC_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_RIGHT))
styles.add(ParagraphStyle(name='ItalicCenter', fontName=ITALIC_FONTNAME, fontSize=MEDIUM_FONTSIZE, alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='Center', alignment=enums.TA_CENTER))
styles.add(ParagraphStyle(name='Left', alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='Right', alignment=enums.TA_RIGHT))
styles.add(ParagraphStyle(name='LetterLeft', fontSize=LARGE_FONTSIZE, alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='LetterBoldLeft', fontName=BOLD_FONTNAME, fontSize=LARGE_FONTSIZE, alignment=enums.TA_LEFT))
styles.add(ParagraphStyle(name='WebAddress', alignment=enums.TA_LEFT, textColor='blue'))

def _create_approval_header(canvas, doc, draw_page_number=True):
    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    current_y = PAGE_HEIGHT - HEADER_MARGIN

    #canvas.drawCentredString(PAGE_WIDTH / 2, current_y - LARGE_FONTSIZE, '{}'.format(settings.DEP_NAME.upper()))

    current_y -= 30

    dpaw_header_logo = ImageReader(BW_DPAW_HEADER_LOGO)
    canvas.drawImage(dpaw_header_logo, HEADER_MARGIN, current_y - 58,
                     width=LICENCE_HEADER_IMAGE_WIDTH, height=LICENCE_HEADER_IMAGE_HEIGHT)

    current_x = HEADER_MARGIN + LICENCE_HEADER_IMAGE_WIDTH + 5


    # canvas.setFont(DEFAULT_FONTNAME, SMALL_FONTSIZE)

    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER), 'Enquiries:')
    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'Telephone:')
    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, 'Facsimile:')
    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, 'Web Site:')
    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5, 'Correspondance:')

    # current_x += 80

    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER),
    #                   '17 DICK PERRY AVE, KENSINGTON, WESTERN AUSTRALIA')
    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 2, '08 9219 9000')
    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 3, '08 9219 8242')
    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 4, doc.site_url)

    # canvas.setFont(BOLD_FONTNAME, SMALL_FONTSIZE)
    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 5, 'Locked Bag 30')
    # canvas.drawString(current_x, current_y - (SMALL_FONTSIZE + HEADER_SMALL_BUFFER) * 6,
    #                   'Bentley Delivery Centre WA 6983')

    canvas.setFont(BOLD_FONTNAME, LARGE_FONTSIZE)

    #print current_x, current_y

    #current_y -= 36
    current_y -= 2
    #current_x += 10
    current_x += 150

    if draw_page_number:
        canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER), 'PAGE')

    if hasattr(doc, 'approval'):
        canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER) * 2, 'NO.')

    canvas.setFont(DEFAULT_FONTNAME, LARGE_FONTSIZE)

    current_x += 50

    if draw_page_number:
        canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER), str(canvas.getPageNumber()))

    if hasattr(doc, 'approval'):
        canvas.drawString(current_x, current_y - (LARGE_FONTSIZE + HEADER_SMALL_BUFFER) * 2,
                          '{}'.format(doc.approval.lodgement_number))

def _create_approval(approval_buffer, approval, proposal, copied_to_permit, user):
    site_url = settings.SITE_URL
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=[every_page_frame], onPage=_create_approval_header)

    doc = BaseDocTemplate(approval_buffer, pageTemplates=[every_page_template], pagesize=A4)

    # this is the only way to get data into the onPage callback function
    doc.approval = approval
    doc.site_url = site_url
    region = approval.region if hasattr(approval, 'region') else ''
    district = approval.district if hasattr(approval, 'district') else ''
    region_district = '{} - {}'.format(region, district) if district else region

    approval_table_style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])

    elements = []


    title = approval.title.encode('UTF-8') if approval.title else ''

    #Organization details

    address = proposal.applicant_address
    # address = proposal.applicant_address
    if proposal.org_applicant:
        email = proposal.org_applicant.organisation.organisation_set.all().first().contacts.all().first().email
    else:
        email= proposal.submitter.email
    elements.append(Paragraph(email,styles['BoldLeft']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph(_format_name(approval.applicant),styles['BoldLeft']))
    elements.append(Paragraph(address.line1, styles['BoldLeft']))
    elements.append(Paragraph(address.line2, styles['BoldLeft']))
    elements.append(Paragraph(address.line3, styles['BoldLeft']))
    # if proposal.org_applicant:
    #     elements.append(Paragraph('%s %s %s' % (address.locality, address.state, address.postcode), styles['BoldLeft']))
    # else:
    #     elements.append(Paragraph('%s %s' % (address.state, address.postcode), styles['BoldLeft']))
    elements.append(Paragraph('%s %s %s' % (address.locality, address.state, address.postcode), styles['BoldLeft']))
    elements.append(Paragraph(address.country.name, styles['BoldLeft']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph(approval.issue_date.strftime(DATE_FORMAT), styles['BoldLeft']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    #elements.append(Paragraph(title, styles['InfoTitleVeryLargeCenter']))
    #elements.append(Paragraph(approval.activity, styles['InfoTitleLargeLeft']))
    elements.append(Paragraph('APPROVAL OF PROPOSAL {} {} TO UNDERTAKE Commercial Operator Licensing ACTIVITY IN {}'.format(title, proposal.lodgement_number, region_district), styles['InfoTitleLargeLeft']))
    #elements.append(Paragraph(approval.tenure if hasattr(approval, 'tenure') else '', styles['InfoTitleLargeRight']))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('The submitted proposal {} {} has been assessed and approved. The approval is granted on the understanding that: '.format(title, proposal.lodgement_number), styles['BoldLeft']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    list_of_bullets= []
    list_of_bullets.append('The potential impacts of the proposal on values the department manages have been removed or minimised to a level \'As Low As Reasonably Practicable\' (ALARP) and the proposal is consistent with departmental objectives, associated management plans and the land use category/s in the activity area.')
    list_of_bullets.append('Approval is granted for the period {} to {}.  This approval is not valid if {} makes changes to what has been proposed or the proposal has expired.  To change the proposal or seek an extension, the proponent must re-submit the proposal for assessment.'.format(approval.start_date.strftime(DATE_FORMAT), approval.expiry_date.strftime(DATE_FORMAT),_format_name(approval.applicant)))
    list_of_bullets.append('The proponent accepts responsibility for advising {} of new information or unforeseen threats that may affect the risk of the proposed activity.'.format(settings.DEP_NAME_SHORT))
    list_of_bullets.append('Information provided by {0} for the purposes of this proposal will not be provided to third parties without permission from {0}.'.format(settings.DEP_NAME_SHORT))
    list_of_bullets.append('The proponent accepts responsibility for supervising and monitoring implementation of activity/ies to ensure compliance with this proposal. {} reserves the right to request documents and records demonstrating compliance for departmental monitoring and auditing.'.format(settings.DEP_NAME_SHORT))
    list_of_bullets.append('Non-compliance with the conditions of the proposal may trigger a suspension or withdrawal of the approval for this activity.')
    list_of_bullets.append('Management actions listed in Appendix 1 are implemented.')

    understandingList = ListFlowable(
            [ListItem(Paragraph(a, styles['Left']), bulletColour='black', value='circle') for a in list_of_bullets],
            bulletFontName=BOLD_FONTNAME, bulletFontSize=SMALL_FONTSIZE, bulletType='bullet')
            #bulletFontName=BOLD_FONTNAME
    elements.append(understandingList)

    # proposal requirements
    requirements = proposal.requirements.all().exclude(is_deleted=True)
    if requirements.exists():
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        elements.append(Paragraph('The following requirements must be satisfied for the approval of the proposal not to be withdrawn:', styles['BoldLeft']))
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        conditionList = ListFlowable(
            [Paragraph(a.requirement, styles['Left']) for a in requirements.order_by('order')],
            bulletFontName=BOLD_FONTNAME, bulletFontSize=MEDIUM_FONTSIZE)
        elements.append(conditionList)

    # if copied_to_permit:
    #     elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    #     elements.append(Paragraph('Assessor Comments', styles['BoldLeft']))
    #     elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    #     for k,v in copied_to_permit:
    #         elements.append(Paragraph(v.encode('UTF-8'), styles['Left']))
    #         elements.append(Paragraph(k.encode('UTF-8'), styles['Left']))
    #         elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    elements += _layout_extracted_fields(approval.extracted_fields)

    # additional information
    '''if approval.additional_information:
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        elements.append(Paragraph('Additional Information', styles['BoldLeft']))
        elements += _layout_paragraphs(approval.additional_information)'''

    # delegation holds the dates, approvale and issuer details.
    delegation = []

    # dates and licensing officer
    # dates_licensing_officer_table_style = TableStyle([('VALIGN', (0, 0), (-2, -1), 'TOP'),
    #                                                   ('VALIGN', (0, 0), (-1, -1), 'BOTTOM')])

    # delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    # date_headings = [Paragraph('Date of Issue', styles['BoldLeft']), Paragraph('Valid From', styles['BoldLeft']),
    #                  Paragraph('Date of Expiry', styles['BoldLeft'])]
    # date_values = [Paragraph(approval.issue_date.strftime(DATE_FORMAT), styles['Left']),
    #                Paragraph(approval.start_date.strftime(DATE_FORMAT), styles['Left']),
    #                Paragraph(approval.expiry_date.strftime(DATE_FORMAT), styles['Left'])]

    # if approval.original_issue_date is not None:
    #     date_headings.insert(0, Paragraph('Original Date of Issue', styles['BoldLeft']))
    #     date_values.insert(0, Paragraph(approval.original_issue_date.strftime(DATE_FORMAT), styles['Left']))

    # delegation.append(Table([[date_headings, date_values]],
    #                         colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
    #                         style=dates_licensing_officer_table_style))

    # proponent details
    # delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    # address = proposal.applicant.organisation.postal_address
    # address_paragraphs = [Paragraph(address.line1, styles['Left']), Paragraph(address.line2, styles['Left']),
    #                       Paragraph(address.line3, styles['Left']),
    #                       Paragraph('%s %s %s' % (address.locality, address.state, address.postcode), styles['Left']),
    #                       Paragraph(address.country.name, styles['Left'])]
    # delegation.append(Table([[[Paragraph('Licensee:', styles['BoldLeft']), Paragraph('Address', styles['BoldLeft'])],
    #                           [Paragraph(_format_name(approval.applicant),
    #                                      styles['Left'])] + address_paragraphs]],
    #                         colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
    #                         style=approval_table_style))

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('Should you have any queries about this approval, please contact {} {}, '
                                'on {} or by email at {}'.format(user.first_name, user.last_name, settings.DEP_PHONE, user.email), styles['Left']))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('To provide feedback on the system used to submit the approval or update contact details, please '
        'contact {} Works Coordinator - {}'.format(settings.SYSTEM_NAME_SHORT, settings.SUPPORT_EMAIL), styles['Left']))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('Approved on behalf of the', styles['Left']))
    delegation.append(Paragraph('{}'.format(settings.DEP_NAME), styles['BoldLeft']))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    delegation.append(Paragraph('{} {}'.format(user.first_name, user.last_name), styles['Left']))
    delegation.append(Paragraph('{}'.format(region_district), styles['Left']))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph(approval.issue_date.strftime(DATE_FORMAT), styles['Left']))

    elements.append(KeepTogether(delegation))

    # Appendix section
    elements.append(PageBreak())
    elements.append(Paragraph('Appendix 1 - Management Actions', styles['BoldLeft']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    if copied_to_permit:
        # for k,v in copied_to_permit:
        #     elements.append(Paragraph(v.encode('UTF-8'), styles['Left']))
        #     elements.append(Paragraph(k.encode('UTF-8'), styles['Left']))
        #     elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        for item in copied_to_permit:
            for key in item:
               elements.append(Paragraph(key.encode('UTF-8'), styles['Left']))
               elements.append(Paragraph(item[key].encode('UTF-8'), styles['Left']))
    else:
        elements.append(Paragraph('There are no management actions.', styles['Left']))


    doc.build(elements)

    return approval_buffer

def _create_approval_cols(approval_buffer, approval, proposal, copied_to_permit, user):
    site_url = settings.SITE_URL
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=[every_page_frame], onPage=_create_approval_header)

    doc = BaseDocTemplate(approval_buffer, pageTemplates=[every_page_template], pagesize=A4)

    # this is the only way to get data into the onPage callback function
    doc.approval = approval
    doc.site_url = site_url

    approval_table_style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])
    box_table_style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOX', (0,0), (-1,-1), 0.25, black), ('INNERGRID', (0,0), (-1,-1), 0.25, black), ('ALIGN', (0, 0), (-1, -1), 'RIGHT')])

    elements = []

    #Organization details

    address = proposal.applicant_address
    # address = proposal.applicant_address
    if proposal.org_applicant:
        try:
            email = proposal.org_applicant.organisation.organisation_set.all().first().contacts.all().first().email
        except:
            raise ValidationError('There is no contact for Organisation. Please create an Organisation contact')
    else:
        email= proposal.submitter.email
    #elements.append(Paragraph(email,styles['BoldLeft']))
    elements.append(Paragraph('CONSERVATION AND LAND MANAGEMENT REGULATIONS 2002 (PART 7)', styles['ItalicCenter']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('COMMERCIAL OPERATIONS LICENCE', styles['InfoTitleVeryLargeCenter']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    elements.append(Paragraph('The Chief Executive Officer (CEO) of the Department of Biodiversity, Conservation and Attractions hereby grants a commercial operations licence to enter upon and conduct activities within the parks/reserves listed in Schedule 1 of this licence to:', styles['BoldLeft']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    # delegation holds the Licence number and applicant name in table format.
    delegation = []
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Table([[[Paragraph('Licensee:', styles['BoldLeft'])],
                              [Paragraph(_format_name(approval.applicant),
                                         styles['Left'])]]],
                            colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                            style=approval_table_style))

    if approval.current_proposal.org_applicant and approval.current_proposal.org_applicant.organisation.trading_name:
        delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        delegation.append(Table([[[Paragraph('Trading Name:', styles['BoldLeft'])],
                                  [Paragraph(_format_name(approval.current_proposal.org_applicant.organisation.trading_name),
                                             styles['Left'])]]],
                                colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                                style=approval_table_style))


    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Table([[[Paragraph('Licence Number:', styles['BoldLeft'])],
                              [Paragraph(approval.lodgement_number,
                                         styles['Left'])]]],
                            colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                            style=approval_table_style))

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))


    elements.append(KeepTogether(delegation))

    elements.append(Paragraph('Commencing on the {} and expiring on {}.'.format(approval.start_date.strftime(DATE_FORMAT2), approval.expiry_date.strftime(DATE_FORMAT2)),styles['BoldLeft']))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('CONDITIONS', styles['BoldLeft']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    list_of_bullets= []
    list_of_bullets.append('This Commercial Operations Licence is subject to the provisions of the <i>Conservation and Land Management Act 1984</i> and all subsidiary legislation made under it.')
    list_of_bullets.append('The Licensee must comply with and not contravene the conditions and restrictions set out in the Commercial Operator Handbook as varied from time to time by the CEO.')
    list_of_bullets.append('The Licensee must comply with the conditions contained in any schedule of conditions attached to this Commercial Operations Licence.')

    understandingList = ListFlowable(
            [ListItem(Paragraph(a, styles['Left']), bulletColour='black') for a in list_of_bullets],
            bulletFontName=BOLD_FONTNAME, bulletFontSize=MEDIUM_FONTSIZE)
            #bulletFontName=BOLD_FONTNAME
    elements.append(understandingList)

    # proposal requirements
    # requirements = proposal.requirements.all().exclude(is_deleted=True)
    # if requirements.exists():
    #     elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    #     elements.append(Paragraph('The following requirements must be satisfied for the licence not to be withdrawn:', styles['BoldLeft']))
    #     elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    #     conditionList = ListFlowable(
    #         [Paragraph(a.requirement, styles['Left']) for a in requirements.order_by('order')],
    #         bulletFontName=BOLD_FONTNAME, bulletFontSize=MEDIUM_FONTSIZE)
    #     elements.append(conditionList)

    elements += _layout_extracted_fields(approval.extracted_fields)

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    elements.append(Paragraph('{} {}'.format(user.first_name, user.last_name), styles['Left']))
    if user.position_title:
        elements.append(Paragraph('{}'.format(user.position_title), styles['Left']))
    elements.append(Paragraph('As Delegate of CEO', styles['Left']))
    elements.append(Paragraph('Under Section 133(2) of the CALM Act 1984', styles['Left']))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph(approval.issue_date.strftime(DATE_FORMAT), styles['Left']))

    elements.append(PageBreak())
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    table_data=[[Paragraph('Licence Number', styles['BoldLeft']), Paragraph(_format_name(approval.lodgement_number), styles['Left'])],
                [Paragraph('Commencement Date', styles['BoldLeft']), Paragraph(_format_name(approval.start_date).strftime(DATE_FORMAT), styles['Left'])],    
                [Paragraph('Expiry Date', styles['BoldLeft']), Paragraph(_format_name(approval.expiry_date).strftime(DATE_FORMAT), styles['Left'])]]
    t=Table(table_data, colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                            style=box_table_style)
    elements.append(t)

    # Schedule 1
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('SCHEDULE 1', styles['BoldCenter']))
    elements.append(Paragraph('COMMERCIAL OPERATIONS LICENCE ACTIVITIES', styles['BoldCenter']))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    park_data=[]
    for p in approval.current_proposal.selected_parks_activities_pdf:
        #park_data.append([Paragraph(_format_name(p['park']), styles['BoldLeft']),
        #                     [Paragraph(a, styles['Left']) for a in p['activities']]])
        activities_str=[]
        for ac in p['activities']:
            activities_str.append(ac.encode('UTF-8'))
        activities_str=str(activities_str).strip('[]').replace('\'', '')
        park_data.append([Paragraph(_format_name(p['park']), styles['BoldLeft']),
                              Paragraph(activities_str, styles['Left'])])
    if park_data:
        t=Table(park_data, colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                            style=box_table_style)
    elements.append(t)

    # Schedule 2
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('SCHEDULE 2', styles['BoldCenter']))
    elements.append(Paragraph('COMMERCIAL OPERATIONS LICENCE LAND ACCESS TYPES', styles['BoldCenter']))

    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    park_data=[]
    for p in approval.current_proposal.selected_parks_access_types_pdf:
        access_types_str=[]
        for ac in p['access_types']:
            access_types_str.append(ac.encode('UTF-8'))
        access_types_str = ', '.join(access_types_str).replace('\'', '')
        park_data.append([Paragraph(_format_name(p['park']), styles['BoldLeft']),
                              Paragraph(access_types_str, styles['Left'])])
    if park_data:
        t=Table(park_data, colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                            style=box_table_style)
    elements.append(t)

    # Schedule 3
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    elements.append(Paragraph('SCHEDULE 3', styles['BoldCenter']))
    elements.append(Paragraph('COMMERCIAL OPERATIONS LICENCE CONDITIONS', styles['BoldCenter']))
    requirements = proposal.requirements.all().exclude(is_deleted=True)
    if requirements.exists():
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        #elements.append(Paragraph('The following requirements must be satisfied for the licence not to be withdrawn:', styles['BoldLeft']))
        #elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

        conditionList = ListFlowable(
            [Paragraph(a.requirement, styles['Left']) for a in requirements.order_by('order')],
            bulletFontName=BOLD_FONTNAME, bulletFontSize=MEDIUM_FONTSIZE)
        elements.append(conditionList)

    doc.build(elements)

    return approval_buffer

def _format_name(applicant):
    #return org.name
    return applicant

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
                    elements.append(Paragraph(field['label'], styles['BoldLeft']))

                    if field['help_text']:
                        elements.append(Paragraph(field['help_text'], styles['ItalicLeft']))

                    elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

                    if field['type'] in ['text', 'text_area']:
                        elements += _layout_paragraphs(field['data'])
                    elif field['type'] in ['radiobuttons', 'select']:
                        elements.append(Paragraph(dict([i.values() for i in field['options']]).
                                                  get(field['data'], 'Not Specified'), styles['Left']))
                    else:
                        elements.append(Paragraph(field['data'], styles['Left']))

                elif field['type'] == 'label':
                    if any([option.get('data', 'off') == 'on' for option in field['options']]):
                        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
                        elements.append(Paragraph(field['label'], styles['BoldLeft']))

                        if field['help_text']:
                            elements.append(Paragraph(field['help_text'], styles['ItalicLeft']))

                        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))

                        elements.append(Paragraph(', '.join([option['label'] for option in field['options']
                                                            if option.get('data', 'off') == 'on']),
                                        styles['Left']))
            else:
                if not __children_have_data(field):
                    continue

                elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
                elements.append(Paragraph(field['label'], styles['BoldLeft']))

                if field['help_text']:
                    elements.append(Paragraph(field['help_text'], styles['ItalicLeft']))

                table_data = []
                for index, group in enumerate(field['children']):
                    if index == 0:
                        heading_row = []
                        for child_field in group:
                            heading_row.append(Paragraph(child_field['label'], styles['BoldLeft']))
                        if heading_row:
                            table_data.append(heading_row)

                    row = []
                    for child_field in group:
                        if child_field['type'] in ['radiobuttons', 'select']:
                            row.append(Paragraph(dict([i.values() for i in child_field['options']]).
                                                 get(child_field['data'], 'Not Specified'), styles['Left']))
                        elif child_field['type'] == 'label':
                            if any([option.get('data', 'off') == 'on' for option in child_field['options']]):
                                row.append(Paragraph(', '.join([option['label'] for option in child_field['options']
                                                                if option.get('data', 'off') == 'on']),
                                                     styles['Left']))
                            else:
                                row.append(Paragraph('Not Specified', styles['Left']))
                        else:
                            row.append(Paragraph(child_field['data'], styles['Left']))

                    if row:
                        table_data.append(row)

                if table_data:
                    elements.append(Table(table_data, style=TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])))

    return elements

def create_approval_doc(approval,proposal, copied_to_permit, user):
    approval_buffer = BytesIO()

    #_create_approval(approval_buffer, approval, proposal, copied_to_permit, user)
    _create_approval_cols(approval_buffer, approval, proposal, copied_to_permit, user)
    filename = 'licence-{}.pdf'.format(approval.lodgement_number)
    document = ApprovalDocument.objects.create(approval=approval,name=filename)
    document._file.save(filename, File(approval_buffer), save=True)

    approval_buffer.close()
    return document

def create_approval_pdf_bytes(approval,proposal, copied_to_permit, user):
    """ Essentially the same as create_approval_doc() - but used to preview the licence without creation """
    licence_buffer = BytesIO()
    _create_approval_cols(licence_buffer, approval, proposal, copied_to_permit, user)

    # Get the value of the BytesIO buffer
    value = licence_buffer.getvalue()
    licence_buffer.close()
    return value

def create_renewal_doc(approval,proposal):
    renewal_buffer = BytesIO()

    _create_renewal(renewal_buffer, approval, proposal)
    filename = 'renewal-{}.pdf'.format(approval.id)
    document = ApprovalDocument.objects.create(approval=approval,name=filename)
    document._file.save(filename, File(renewal_buffer), save=True)

    renewal_buffer.close()
    return document

def _create_renewal(renewal_buffer, approval, proposal):
    site_url = settings.SITE_URL
    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN,
                             PAGE_HEIGHT - 160, id='EveryPagesFrame')
    every_page_template = PageTemplate(id='EveryPages', frames=[every_page_frame], onPage=_create_approval_header)

    doc = BaseDocTemplate(renewal_buffer, pageTemplates=[every_page_template], pagesize=A4)

    # this is the only way to get data into the onPage callback function
    doc.approval = approval
    doc.site_url = site_url

    approval_table_style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')])

    elements = []


    #title = approval.title.encode('UTF-8')
    title=''
    # additional information
    '''if approval.additional_information:
        elements.append(Spacer(1, SECTION_BUFFER_HEIGHT))
        elements.append(Paragraph('Additional Information', styles['BoldLeft']))
        elements += _layout_paragraphs(approval.additional_information)'''

    # delegation holds the dates, approvale and issuer details.
    delegation = []
    # proponent details
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    #address = proposal.applicant.organisation.postal_address
    address = proposal.applicant_address
    address_paragraphs = [Paragraph(address.line1, styles['Left']), Paragraph(address.line2, styles['Left']),
                          Paragraph(address.line3, styles['Left']),
                          Paragraph('%s %s %s' % (address.locality, address.state, address.postcode), styles['Left']),
                          Paragraph(address.country.name, styles['Left'])]
    # if proposal.org_applicant:
    #     address_paragraphs = [Paragraph(address.line1, styles['Left']), Paragraph(address.line2, styles['Left']),
    #                       Paragraph(address.line3, styles['Left']),
    #                       Paragraph('%s %s %s' % (address.locality, address.state, address.postcode), styles['Left']),
    #                       Paragraph(address.country.name, styles['Left'])]
    # else:
    #     address_paragraphs = [Paragraph(address.line1, styles['Left']), Paragraph(address.line2, styles['Left']),
    #                       Paragraph(address.line3, styles['Left']),
    #                       Paragraph('%s %s' % (address.state, address.postcode), styles['Left']),
    #                       Paragraph(address.country.name, styles['Left'])]
    delegation.append(Table([[[Paragraph('Licensee:', styles['BoldLeft']), Paragraph('Address', styles['BoldLeft'])],
                              [Paragraph(_format_name(approval.applicant),
                                         styles['Left'])] + address_paragraphs]],
                            colWidths=(120, PAGE_WIDTH - (2 * PAGE_MARGIN) - 120),
                            style=approval_table_style))

    expiry_date = approval.expiry_date.strftime(DATE_FORMAT)
    full_name = proposal.submitter.get_full_name()

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('Dear {} '.format(full_name), styles['Left']))

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    # delegation.append(Paragraph('This is a reminder that your approval: ', styles['Left']))

    # delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))

    # title_with_number = '{} - {}'.format(approval.lodgement_number, title)

    # delegation.append(Paragraph(title_with_number, styles['InfoTitleLargeLeft']))

    # delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    # delegation.append(Paragraph('is due to expire on {}'.format(expiry_date), styles['Left']))

    delegation.append(Paragraph('This is a reminder that your Commercial Operations licence {} expires on {}. '.format(approval.lodgement_number, expiry_date), styles['BoldLeft']))

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('It is important you apply to renew your licence now so that we can process it before your current licence expires.'
                                'If you would like to continue operating within WA\'s national parks and other conservation reserves you need a licence under the Conservation and Land Management Regulations 2002.', styles['Left']))
    #delegation.append(Paragraph('If you would like to continue operating within WA\'s national parks and other conservation reserves you need a licence under the Conservation and Land Management Regulations 2002.'
    #                            , styles['Left']))

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('As a reminder, the Commercial Operator Handbook (2019) outlines the conditions of your licence.'
        'The handbook is available online at the {} website:'.format(settings.DEP_NAME), styles['Left']))
    #delegation.append(Paragraph('The handbook is available online at the {} website: .'.format(settings.DEP_NAME), styles['Left']))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('{}'.format(settings.COLS_HANDBOOK_URL), styles['WebAddress']))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('Please make sure you have access to this handbook, either in hardcopy or online, when operating within WA\'s national parks and conservation reserves.', styles['Left']))
    #delegation.append(Paragraph('', styles['Left']))

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('If you have any questions about how to renew your licence please call Licencing Officer on {} or email licensing@dbca.wa.gov.au.'.format(settings.DEP_PHONE), styles['Left']))

    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Paragraph('Yours sincerely ', styles['Left']))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    delegation.append(Spacer(1, SECTION_BUFFER_HEIGHT))
    #delegation.append(Paragraph('DIRECTOR GENERAL', styles['Left']))
    delegation.append(Paragraph('{}'.format(settings.DEP_NAME), styles['Left']))

    elements.append(KeepTogether(delegation))

    doc.build(elements)

    return renewal_buffer
