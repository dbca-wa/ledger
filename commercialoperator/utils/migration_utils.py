from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import OrganisationAddress
from ledger.accounts.models import EmailUser
from commercialoperator.components.organisations.models import Organisation, OrganisationContact, UserDelegation
from commercialoperator.components.main.models import ApplicationType, Park
from commercialoperator.components.proposals.models import Proposal, ProposalType, ProposalOtherDetails, ProposalPark
from commercialoperator.components.approvals.models import Approval
from commercialoperator.components.bookings.models import ApplicationFee, ParkBooking, Booking
from django.core.exceptions import MultipleObjectsReturned
from ledger.address.models import Country

import csv
import os
import datetime
import string
from dateutil.relativedelta import relativedelta

import logging
logger = logging.getLogger(__name__)

def run_deploy(tclass_csv, eclass_csv):
    """
    tclass_csv: 'commercialoperator/utils/csv/Commercial-Licences-Migration-20191119.csv'
    eclass_csv: 'commercialoperator/utils/csv/E-Class-20191119.csv'
    """
    clear_applications()

    reader = OrganisationReader(tclass_csv)
    reader.create_organisation_data()
    reader.create_licences()

    reader = OrganisationReader(eclass_csv)
    #reader.create_organisation_data()
    reader.create_licences()


def clear_applications():
    def reset_sql_idx():
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute('''ALTER SEQUENCE commercialoperator_applicationfee_id_seq RESTART WITH 1''')
        cursor.execute('''ALTER SEQUENCE commercialoperator_parkbooking_id_seq RESTART WITH 1''')
        cursor.execute('''ALTER SEQUENCE commercialoperator_booking_id_seq RESTART WITH 1''')
        cursor.execute('''ALTER SEQUENCE commercialoperator_approval_id_seq RESTART WITH 1''')
        cursor.execute('''ALTER SEQUENCE commercialoperator_proposal_id_seq RESTART WITH 1''')

    print 'ApplicationFee: {}'.format(ApplicationFee.objects.all().delete())
    print 'ParkBooking: {}'.format(ParkBooking.objects.all().delete())
    print 'Booking: {}'.format(Booking.objects.all().delete())
    print 'Approval: {}'.format(Approval.objects.all().delete())
    print 'Proposal: {}'.format(Proposal.objects.all().delete())

    print 'Reset PK IDX'
    reset_sql_idx()


def check_parks():
    parks_not_found = parks_not_found = ['Lesmurdie Falls National Park', 'Goldfields Woodlands Conservation Park and National Park', 'Helena and Aurora Ranges Conservation Park', 'Midgegooroo National Park', 'Parry La \
goons Nature Reserve', 'Stockyard Gully Reserve', 'Wiltshire-Butler National Park', 'Blackwood Bibbulmun', 'Collie Bibbulmun', 'Darling Range Bibbulmun', 'Denmark Bibbulmun', 'Dwellingup Bibbulmun\
', 'Munda Biddi - Collie to Jarrahwood', 'Munda Biddi - Jarrahdale to Nanga', 'Munda Biddi - Mundaring to Jarrahdale', 'Munda Biddi - Nanga to Collie', 'Northcliffe Bibbulmun', 'Pemberton Bibbulmu\
n', 'Walpole Bibbulmun', '', 'Special Permission', 'Cape to Cape - Cape Naturaliste to Prevelly', 'Cape to Cape - Prevelly to Cape Leeuwin', 'Munda Biddi - Denmark to Albany', 'Munda Biddi - Jarra\
hwood to Manjimup', 'Munda Biddi - Manjimup to Northcliffe', 'Munda Biddi - Northcliffe to Walpole', 'Munda Biddi - Walpole to Denmark', 'Cape Range National Park', 'Francois Peron National Park',\
'Leeuwin-Naturaliste National Park', 'Penguin Island Conservation Park', 'Walpole-Nornalup National Park', 'Bruce Rock Nature Reserve', 'Totadgin Nature Reserve', 'Yanneymooning Nature Reserve',\
'Badgingarra National Park', 'Beedelup National Park', 'Boorabbin National Park', 'Brockman National Park', 'Cape Le Grand National Park', 'Coalseam Conservation Park', 'DEntrecasteaux National Pa\
rk', 'Fitzgerald River National Park', 'Gloucester National Park', 'Hamelin Pool Marine Nature Reserve', 'Kalbarri National Park', 'Karijini National Park', 'Kennedy Range National Park', 'Leschen\
ault Peninsula Conservation Park', 'Lesueur National Park', 'Millstream Chichester National Park', 'Mt Frankland National Park', 'Mt Frankland North National Park', 'Mt Frankland South National Pa\
rk', 'Nambung National Park', 'Porongurup National Park', 'Shannon National Park', 'Shell Beach Conservation Park', 'Stirling Range National Park', 'Stokes National Park', 'Torndirrup National Par\
k', 'Two Peoples Bay Nature Reserve', 'Warren National Park', 'Wellington National Park', 'William Bay National Park', 'Drysdale River National Park', 'Prince Regent National Park', 'Geikie Gorge\
National Park', 'Donnelly District State Forest', 'Avon Valley National Park', 'Blackwood River National Park', 'Lane Poole Reserve', 'Walyunga National Park', 'Mitchell River National Park', 'Woo\
ditjup National Park', 'Dirk Hartog Island National Park']

    for park in parks_not_found:
        try:
            p = Park.objects.get(name__icontains=park)
        except:
            park_name = park.split()
            park_obj=None
            if len(park_name) > 0:
                park_obj = Park.objects.filter(name__icontains=park_name[0])
            missing_park_names = list(park_obj.values_list('name', flat=True)) if park_obj else []
            print '{}, {}'.format(park, missing_park_names)

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
        self.parks_not_found = []
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
                #import ipdb; ipdb.set_trace()
                data['licencee'] = data['licencee'] + ' ' if ledger_organisation.objects.filter(name=data['licencee']) else data['licencee']
                
                lo, created = ledger_organisation.objects.get_or_create(
                    abn=data['abn'],
                    defaults={
                        'name': data['licencee'],
                        'postal_address': oa,
                        'billing_address': oa,
                        'trading_name': data['trading_name']
                    }
                )

            except IntegrityError, e:
                lo, created = ledger_organisation.objects.get_or_create(
                    abn=data['abn'],
                    defaults={
                        'name': data['licencee'] + ' ',
                        'postal_address': oa,
                        'billing_address': oa,
                        'trading_name': data['trading_name']
                    }
                )

            except Exception, e:
                print 'Error creating Organisation: {} - {}'.format(data['name'], data['abn'])
                raise

            if created:
                abn_new.append(data['abn'])
            else:
                print '******** ERROR ********* abn already exists {}'.format(data['abn'])

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
                import ipdb; ipdb.set_trace()
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
                import ipdb; ipdb.set_trace()
                print 'Org Contact: {}'.format(user)
                raise

            if debug:
                print 'Org Contact: {}'.format(oc)

            #return abn_new, abn_existing

        return abn_new, abn_existing

    def _read_organisation_data(self, filename, verify=False):
        def get_start_date(data, row):
            #import ipdb; ipdb.set_trace()
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

            #import ipdb; ipdb.set_trace()
            if 'YEAR' in term[1]:
                start_date = expiry_date - relativedelta(years=int(term[0]))
            if 'MONTH' in term[1]:
                start_date = expiry_date - relativedelta(months=int(term[0]))
            else:
                start_date = datetime.date.today()

            if data['start_date'] != '':
                data.update({'start_date': start_date})
            else:
                data.update({'start_date': datetime.date.today()})

            if data['issue_date'] != '':
                issue_date = datetime.datetime.strptime(data['issue_date'], '%d-%b-%y').date() # '05-Feb-89'
                data.update({'issue_date': start_date})
            else:
                data.update({'issue_date': datetime.date.today()})

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

                    emails = row[21].translate(None, b' -()').replace(';', ',').split(',')
                    for num, email in enumerate(emails, 1):
                        data.update({'email{}'.format(num): email})

                    data.update({'t_handbooks': row[22].strip()})
                    data.update({'m_handbooks': row[23].strip()})
                    data.update({'insurance_expiry_date': row[24].strip()})
                    data.update({'survey_cert': row[25].strip()})
                    data.update({'atap_expiry': row[26].strip()})
                    data.update({'eco_cert_expiry': row[27].strip()})
                    data.update({'start_date': row[28].strip()})
                    data.update({'issue_date': row[29].strip()})
                    data.update({'licence_class': row[30].strip()})
                    #data.update({'land_parks': row[31].translate(None, b' -()').split()})
                    data.update({'land_parks': [i.strip().replace('`', '') for i in row[31].split(',')]})
                    #data.update({'land_parks': 'Geikie Gorge National Park,Lawley River National Park,Purnululu National Park'.split(',')})
                    #print data
                    get_start_date(data, row)

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
                    #submitter = EmailUser.objects.get(email__icontains=data['email1'])
                    submitter = EmailUser.objects.get(email=data['email1'])
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
        try:
            if data['licence_class'].startswith('T'):
                application_type=ApplicationType.objects.get(name='T Class')
            elif data['licence_class'].startswith('E'):
                application_type=ApplicationType.objects.get(name='E Class')

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
                try:
                    park = Park.objects.get(name__icontains=park_name)
                    ProposalPark.objects.create(proposal=proposal, park=park)
                except Exception, e:
                    if park_name not in self.parks_not_found:
                        self.parks_not_found.append(park_name)
                    #logger.error('Park: {}'.format(park_name))
                    #import ipdb; ipdb.set_trace()

            proposal.save()
            approval.save()
        except Exception, e:
            logger.error('{}'.format(e))
            import ipdb; ipdb.set_trace()
            return None

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
        print 'Parks Not Found: {}'.format(self.parks_not_found)





