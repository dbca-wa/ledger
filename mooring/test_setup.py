from django.test import TestCase
from django.test import Client
from mixer.backend.django import mixer
from django.conf import settings
from importlib import import_module
import time
from .models import *
#from drf_extra_fields.geo_fields import PointField
from django.contrib.gis.geos import Point
from ledger.accounts.models import EmailUser, EmailUserManager
from ledger.payments.models import Invoice, OracleInterfaceSystem
from oscar.apps.order.models import Order
import random
import string

class TestSetup(TestCase):
#    client = Client()

    def setUp(self):
#        adminUN = "admin@website.domain"
#        nonAdminUN = "nonadmin@website.domain"
        self.client = Client()
        #self.superAdminUN = load_superAdminUN
        #self.adminUN = load_adminUN
        #self.nonAdminUN = load_nonAdminUN

#        self.superAdminUN = self.random_email()
#        self.adminUN = self.random_email()
#        self.nonAdminUN = self.random_email()
        self.superAdminUN = 'test.superadmin@dbcatest.com'
        self.adminUN = 'test.admin@dbcatest.com'
        self.nonAdminUN = 'test.customer@dbcatest.com'
        superadminUser = None
        adminUser = None
        user = None
        eum = EmailUserManager()
#        self.superadminUser = load_customer 
#        self.adminUser = load_adminUser
#        self.customer = load_superadminUser
#        self.superadminUser = EmailUser.objects.create_superuser(pk=1,email=self.superAdminUN, password="pass")
        self.superadminUser = EmailUser.objects.create(email=self.superAdminUN, password="pass", is_staff=True, is_superuser=True)
        self.superadminUser.set_password('pass')
        self.superadminUser.save()
#        self.adminUser = EmailUser.objects.create_user(pk=2,email=self.adminUN, password="pass", )
        self.adminUser  = EmailUser.objects.create(email=self.adminUN,password="pass",is_staff=True, is_superuser=False)
        self.adminUser.set_password('pass')       
        self.adminUser.save() 

        self.customer = EmailUser.objects.create(email=self.nonAdminUN, password="pass", is_staff=False, is_superuser=False)
        self.customer.set_password('pass')
        self.customer.save()
        ria = MooringAreaGroup.objects.create(name='Rottnest')
        pvs = MooringAreaGroup.objects.create(name='PVS')

        GlobalSettings.objects.create(key=2,mooring_group=ria,value=25)
        GlobalSettings.objects.create(key=2,mooring_group=pvs,value=25) 
        adLoc = AdmissionsLocation.objects.create(key='ria', text='Rottnest Island Authority', mooring_group=ria)
        region = Region.objects.create(name='Rottnest Island',abbreviation='rottnest-island', ratis_id=10, wkb_geometry=Point(115.56141,-32.07424), zoom_level='10', mooring_group=ria)
        district = District.objects.create(name='Rottnest Island',abbreviation='rottnest-island', region=region,ratis_id=10, mooring_group=ria)
        #user.set_password('pass')
        #user.is_staff = False
        #user.save()
        ria.members.add(self.adminUser)
        ria.save()

#        self.userAdmin = EmailUser.objects.get(email=self.adminUN)
#        self.superUserAdmin = EmailUser.objects.get(email=self.superAdminUN)
#        self.customer = EmailUser.objects.get(email=self.nonAdminUN) 
#        self.customer.is_staff =False
#        self.customer.is_superuser =False
#        self.customer.save()

        orderAdmin = mixer.blend(Order, user=self.adminUser)
        invoiceAdmin = mixer.blend(Invoice, order_number=orderAdmin.number, reference="123456")

        userNonAdmin = EmailUser.objects.get(email=self.nonAdminUN)
        orderNonAdmin = mixer.blend(Order, user=self.customer)
        invoiceNonAdmin = mixer.blend(Invoice, order_number=orderNonAdmin.number, reference="987654")

        aReason = AdmissionsReason.objects.create(text="abc", detailRequired=False, editable=True, mooring_group=ria)
        self.adRate = AdmissionsRate.objects.create(period_start=datetime.now() - timedelta(days=2), period_end=None, adult_cost="15",
                adult_overnight_cost="20", concession_cost="5", concession_overnight_cost="7", children_cost="5",
                children_overnight_cost="7", infant_cost="5", infant_overnight_cost="7", family_cost="30", family_overnight_cost="40",
                comment=None, reason=aReason, mooring_group=ria)
        AdmissionsOracleCode.objects.create(oracle_code="0516", mooring_group=ria)
        adBooking = AdmissionsBooking.objects.create(customer=self.customer, booking_type=1, vesselRegNo="ABC123", noOfAdults=1, noOfConcessions=0, noOfChildren=0, noOfInfants=0, warningReferenceNo="", totalCost=10.50)
        adLine = AdmissionsLine.objects.create(arrivalDate=datetime.now(),overnightStay=False,admissionsBooking=adBooking, cost='10.50', location=adLoc)

        openReason = mixer.blend(OpenReason, detailRequired=False, mooring_group=ria)
        self.prReason = mixer.blend(PriceReason, detailRequired=False, mooring_group=ria)


        #OracleInterfaceSystem.objects.create(system_id="0516", enabled=True, deduct_percentage=False, source='MBS', method='MBS-RECEIPTS')

        self.park = mixer.blend(MarinePark, zoom_level=1, oracle_code="0516", mooring_group=ria, district=district)
        #self.area = mixer.blend(MooringArea, park=mixer.SELECT, mooring_group=ria)
        self.area = mixer.blend(MooringArea, park=self.park, mooring_group=ria, name='Mooring 1', address={})
#        self.areaGroup = mixer.blend(MooringAreaGroup, moorings=self.area.id)
#        self.areaGroup = mixer.blend(ria, moorings=self.area.id)
        self.areaGroup = ria
        self.site = mixer.blend(Mooringsite, mooringarea=self.area)
        self.bpo = mixer.blend(BookingPeriodOption)
        self.bp = mixer.blend(BookingPeriod, booking_period=self.bpo)
        self.bp2 = BookingPeriod.objects.create(name='selfbp2')
        self.siteRate = mixer.blend(MooringsiteRate, campsite=self.site, booking_period=self.bp, reason=self.prReason)
        self.booking = mixer.blend(Booking, departure=datetime.now(), arrival=datetime.now()-timedelta(days=3), mooringarea=self.area)
        self.msBooking = mixer.blend(MooringsiteBooking, campsite=self.site, booking=self.booking, from_dt=(datetime.now()+timedelta(days=1)).date(), to_dt=(datetime.now()+timedelta(days=4)).date())
        # self.MABRange = mixer.blend(MooringAreaBookingRange, campground=self.area, skip_validation=True)
        self.region = region
        self.ria = ria
        self.adLoc = adLoc
#        self.region = mixer.blend(Region, name='Rottnest Island',abbreviation='rottnest-island', ratis_id=10, wkb_geometry=Point(115.56141,-32.07424), zoom_level='10', mooring_group=ria)

        self.adReason = mixer.blend(AdmissionsReason, detailRequired=False, mooring_group=ria)
        self.opReason = mixer.blend(OpenReason, detailRequired=False, mooring_group=ria)
        self.maxStayReason = mixer.blend(MaximumStayReason, detailRequired=False, mooring_group=ria)
        
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def random_email(self):
        """Return a random email address ending in dbca.wa.gov.au
        """
#        print time
#        time.sleep(5)
        # import time as systime
        # systime.sleep(2)
        s = ''.join(random.choice(string.ascii_letters) for i in range(80))
        return '{}@dbca.wa.gov.au'.format(s)

        
#def random_email():
#        """Return a random email address ending in dbca.wa.gov.au
#        """
#        s = ''.join(random.choice(string.ascii_letters) for i in range(80))
#        return '{}@dbca.wa.gov.au'.format(s)
#       
#
#load_superAdminUN = random_email()
#load_adminUN = random_email()
#load_nonAdminUN = random_email()
#
#load_superadminUser = EmailUser.objects.create_superuser(email=load_superAdminUN, password="pass")
#load_adminUser = EmailUser.objects.create_user(email=load_adminUN, password="pass", )
#load_customer = EmailUser.objects.create(email=load_nonAdminUN, password="pass", is_staff=False, is_superuser=False)
 
