from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import OrganisationAddress
from ledger.accounts.models import EmailUser
from commercialoperator.components.organisations.models import Organisation, OrganisationContact, UserDelegation
from commercialoperator.components.main.models import ApplicationType, Park
from commercialoperator.components.proposals.models import Proposal, ProposalType, ProposalOtherDetails, ProposalPark
from commercialoperator.components.approvals.models import Approval

import csv
import os
import datetime
import string
from dateutil.relativedelta import relativedelta

import logging
logger = logging.getLogger(__name__)

class OrganisationReader():
    """
    Reads csv file and creates Licensees (Organisations or individuals)
    Usage:
        from commercialoperator.utils.migration_utils import OrganisationReader
        reader = OrganisationReader('/tmp/General_Compliance_Report_1.csv')
        reader._create_organisation_data()
        reader.create_licences()
    """

    def __init__(self, filename):
        self.not_found = []
        self.org_lines = self._read_organisation_data(filename)

    def _create_organisation(self, data, count, debug=False):

        #print 'Data: {}'.format(data)
        #user = None
        try:
            user, created = EmailUser.objects.get_or_create(
                email__icontains=data['email1'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone_number': data['phone_number1'],
                    'mobile_number': data['mobile_number'],
                },
            )
        except Exception, e:
            print data['email1']

        if debug:
            print 'User: {}'.format(user)

        abn_existing = []
        abn_new = []
        process = True
        try:
            ledger_organisation.objects.get(abn=data['abn'])
            abn_existing.append(data['abn'])
            print '{}, Existing ABN: {}'.format(count, data['abn'])
            process = False
        except Exception, e:
            print '{}, Add ABN: {}'.format(count, data['abn'])
        print 'DATA: {}'.format(data)
        print

        if process:
            try:
                #print 'Country: {}'.format(data['country'])
                country=Country.objects.get(printable_name__icontains=data['country'])
                oa, created = OrganisationAddress.objects.get_or_create(
                    line1=data['address_line1'],
                    locality=data['suburb'],
                    postcode=data['postcode'] if data['postcode'] else '0000',
                    defaults={
                        'line2': data['address_line2'],
                        'line3': data['address_line3'],
                        'state': data['state'],
                        'country': country.code,
                    }
                )
            except MultipleObjectsReturned:
                oa = OrganisationAddress.objects.filter(
                    line1=data['address_line1'],
                    locality=data['suburb'],
                    postcode=data['postcode'] if data['postcode'] else '0000',
                    line2=data['address_line2'],
                    line3=data['address_line3'],
                    state=data['state'],
                    country=country.code
                ).first()

            except:
                print 'Country 2: {}'.format(data['country'])
                raise
            if debug:
                print 'Org Address: {}'.format(oa)

            try:
                lo, created = ledger_organisation.objects.get_or_create(
                    abn=data['abn'],
                    defaults={
                        'name': data['licencee'],
                        'postal_address': oa,
                        'billing_address': oa,
                        'trading_name': data['trading_name']
                    }
                )
                if created:
                    abn_new.append(data['abn'])
                else:
                    print '******** ERROR ********* abn already exists {}'.format(data['abn'])

            except Exception, e:
                print 'ABN: {}'.format(data['abn'])
                raise

            if debug:
                print 'Ledger Org: {}'.format(lo)

            try:
                org, created = Organisation.objects.get_or_create(organisation=lo)
            except Exception, e:
                print 'Org: {}'.format(org)
                raise

            if debug:
                print 'Organisation: {}'.format(org)

            try:
                delegate, created = UserDelegation.objects.get_or_create(organisation=org, user=user)
            except Exception, e:
                print 'Delegate Creation Failed: {}'.format(user)
                raise

            if debug:
                print 'Delegate: {}'.format(delegate)

            try:
                oc, created = OrganisationContact.objects.get_or_create(
                    organisation=org,
                    email=user.email,
                    defaults={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone_number': user.phone_number,
                        'mobile_number': user.mobile_number if data['mobile_number'] else '',
                        'user_status': 'active',
                        'user_role': 'organisation_admin',
                        'is_admin': True
                    }
                )
            except Exception, e:
                print 'Org Contact: {}'.format(user)
                raise

            if debug:
                print 'Org Contact: {}'.format(oc)

            #return abn_new, abn_existing

        return abn_new, abn_existing

    def _read_organisation_data(self, filename, verify=False):
        def get_start_date(data, row):
            try:
                expiry_date = datetime.datetime.strptime(data['expiry_date'], '%d-%b-%y').date() # '05-Feb-89'
            except Exception, e:
                data.update({'start_date': None})
                data.update({'issue_date': None})
                data.update({'expiry_date': None})
                #logger.error('Expiry Date: {}'.format(data['expiry_date']))
                #logger.error('Data: {}'.format(data))
                #raise
                return

            term = data['term'].split() # '3 YEAR'

            if 'YEAR' in term[1]:
                start_date = expiry_date - relativedelta(years=int(term[0]))
            if 'MONTH' in term[1]:
                start_date = expiry_date - relativedelta(months=int(term[0]))
            else:
                start_date = datetime.date.today()

            data.update({'start_date': start_date})
            data.update({'issue_date': start_date})
            data.update({'expiry_date': expiry_date})

        lines=[]
        try:
            '''
            Example csv
                address, town/city, state (WA), postcode, org_name, abn, trading_name, first_name, last_name, email, phone_number
                123 Something Road, Perth, WA, 6100, Import Test Org 3, 615503, DDD_03, john, Doe_1, john.doe_1@dbca.wa.gov.au, 08 555 5555

                File No:Licence No:Expiry Date:Term:Trading Name:Licensee:ABN:Title:First Name:Surname:Other Contact:Address 1:Address 2:Address 3:Suburb:State:Country:Post:Telephone1:Telephone2:Mobile:Insurance Expiry:Survey Cert:Name:SPV:ATAP Expiry:Eco Cert Expiry:Vessels:Vehicles:Email1:Email2:Email3:Email4
                2018/001899-1:HQ70324:28-Feb-21:3 YEAR:4 U We Do:4 U We Do Pty Ltd::MR:Petrus:Grobler::Po Box 2483:::ESPERANCE:WA:AUSTRALIA:6450:458021841:::23-Jun-18::::30-Jun-18::0:7:groblerp@gmail.com:::
            To test:
                from commercialoperator.components.proposals.models import create_organisation_data
                create_migration_data('commercialoperator/utils/csv/orgs.csv')
            '''
            with open(filename) as csvfile:
                reader = csv.reader(csvfile, delimiter=str(':'))
                header = next(reader) # skip header
                for row in reader:
                    data={}
                    data.update({'file_no': row[0].translate(None, string.whitespace)})
                    data.update({'licence_no': row[1].translate(None, string.whitespace)})
                    data.update({'expiry_date': row[2].strip()})
                    data.update({'term': row[3].strip()})

                    get_start_date(data, row)

                    data.update({'trading_name': row[4].strip()})
                    data.update({'licencee': row[5].strip()})
                    data.update({'abn': row[6].translate(None, string.whitespace)})
                    data.update({'title': row[7].strip()})
                    data.update({'first_name': row[8].strip().capitalize()})
                    data.update({'last_name': row[9].strip().capitalize()})
                    data.update({'other_contact': row[10].strip()})
                    data.update({'address_line1': row[11].strip()})
                    data.update({'address_line2': row[12].strip()})
                    data.update({'address_line3': row[13].strip()})
                    data.update({'suburb': row[14].strip().capitalize()})
                    data.update({'state': row[15].strip()})

                    country = ' '.join([i.lower().capitalize() for i in row[16].strip().split()])
                    if country == 'A':
                        country = 'Australia'
                    data.update({'country': country})

                    data.update({'postcode': row[17].translate(None, string.whitespace)})
                    data.update({'phone_number1': row[18].translate(None, b' -()')})
                    data.update({'phone_number2': row[19].translate(None, b' -()')})
                    data.update({'mobile_number': row[20].translate(None, b' -()')})

                    emails = row[21].translate(None, b' -()').split(',')
                    for num, email in enumerate(emails, 1):
                        data.update({'email{}'.format(num): email})

                    data.update({'insurance_expiry_date': row[22].strip()})
                    data.update({'survey_cert': row[23].strip()})
                    data.update({'name': row[24].strip()})
                    data.update({'spv': row[25].strip()})
                    data.update({'atap_expiry': row[26].strip()})
                    data.update({'eco_cert_expiry': row[27].strip()})
                    data.update({'vessels': row[28].strip()})
                    data.update({'vehicles': row[29].strip()})
                    #data.update({'land_parks': row[30].translate(None, b' -()').split})
                    data.update({'land_parks': 'Geikie Gorge National Park,Lawley River National Park,Purnululu National Park'.split(',')})
                    #print data

                    lines.append(data)

        except:
            logger.info('Main {}'.format(data))
            raise

        return lines


    def _migrate_approval(self, data):
        from commercialoperator.components.approvals.models import Approval
        org_applicant = None
        proxy_applicant = None
        submitter=None
        try:

            if data['email1']:
                #try:
                #    submitter = EmailUser.objects.get(email__icontains=data['email1'])
                #except:
                #    submitter = EmailUser.objects.create(email=data['email1'], password = '')
                try:
                    submitter = EmailUser.objects.get(email__icontains=data['email1'])
                except:
                    submitter = EmailUser.objects.create(
                        email=data['email1'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        phone_number=data['phone_number1'],
                        mobile_number=data['mobile_number'],
                    )

                if data['abn']:
                    #org_applicant = Organisation.objects.get(organisation__name=data['org_applicant'])
                    org_applicant = Organisation.objects.get(organisation__abn=data['abn'])
            else:
                #ValidationError('Licence holder is required')
                logger.error('Licence holder is required: submitter {}, abn {}'.format(data['submitter'], data['abn']))
                self.not_found.append({'submitter': data['submitter'], 'abn': data['abn']})
                return None
        except Exception, e:
            #raise ValidationError('Licence holder is required: \n{}'.format(e))
            logger.error('Licence holder is required: submitter {}, abn {}'.format(data['submitter'], data['abn']))
            self.not_found.append({'submitter': data['submitter'], 'abn': data['abn']})
            return None

        #application_type=ApplicationType.objects.get(name=data['application_type'])
        #application_name = application_type.name
        application_type=ApplicationType.objects.get(name='T Class')
        #application_name = 'T Class'
        # Get most recent versions of the Proposal Types
        qs_proposal_type = ProposalType.objects.all().order_by('name', '-version').distinct('name')
        proposal_type = qs_proposal_type.get(name=application_type.name)
        proposal= Proposal.objects.create(
                        application_type=application_type,
                        submitter=submitter,
                        org_applicant=org_applicant,
                        schema=proposal_type.schema
                    )

        approval = Approval.objects.create(
                        issue_date=data['issue_date'],
                        expiry_date=data['expiry_date'],
                        start_date=data['start_date'],
                        org_applicant=org_applicant,
                        submitter=submitter,
                        current_proposal=proposal
                    )

        proposal.lodgement_number = proposal.lodgement_number.replace('A', 'AM') # Application Migrated
        proposal.approval= approval
        proposal.processing_status='approved'
        proposal.customer_status='approved'
        proposal.migrated=True
        approval.migrated=True
        other_details = ProposalOtherDetails.objects.create(proposal=proposal)

        for park_name in data['land_parks']:
            park = Park.objects.get(name=park_name)
            ProposalPark.objects.create(proposal=proposal, park=park)

        proposal.save()
        approval.save()
        return approval

    def create_organisation_data(self):
        abn_existing = []
        abn_new = []
        count = 1
        for data in self.org_lines:
            new, existing = self._create_organisation(data, count)
            count += 1
            abn_new = new + abn_new
            abn_existing = existing + abn_existing

        print 'New: {}, Existing: {}'.format(len(abn_new), len(abn_existing))
        print 'New: {}'.format(abn_new)
        print 'Existing: {}'.format(abn_existing)

    def create_licences(self):
        approval_error = []
        approval_new = []
        for data in self.org_lines:
            try:
                approval = self._migrate_approval(data)
                approval_new.append(approval) if approval else approval_error(data)
                print 'Added: {}'.format(approval)
            except Exception, e:
                print 'Exception {}'.format(e)
                print 'Data: {}'.format(data)
                approval_error.append([e, data])

        print 'Approvals: {}'.format(approval_new)
        print 'Approval Errors: {}'.format(approval_error)
        print 'Approvals: {}, Approval_Errors: {}'.format(len(approval_new), len(approval_error))





