from django.test import TestCase
from django.test import Client
from mixer.backend.django import mixer
from django.conf import settings
from importlib import import_module

from .models import *

from ledger.accounts.models import EmailUser, EmailUserManager
from ledger.payments.models import Invoice
from oscar.apps.order.models import Order


class TestSetup(TestCase):
    client = Client()

    def setUp(self):
        adminUN = "admin@website.domain"
        nonAdminUN = "nonadmin@website.domain"
        
        instance = EmailUserManager()
        adminUser = EmailUser.objects.create_superuser(email=adminUN, password="pass")
        user = EmailUser.objects.create_user(email=nonAdminUN, password="pass")

        userAdmin = EmailUser.objects.get(email=adminUN)
        orderAdmin = mixer.blend(Order, user=userAdmin)
        invoiceAdmin = mixer.blend(Invoice, order_number=orderAdmin.number, reference="123456")

        userNonAdmin = EmailUser.objects.get(email=nonAdminUN)
        orderNonAdmin = mixer.blend(Order, user=userNonAdmin)
        invoiceNonAdmin = mixer.blend(Invoice, order_number=orderNonAdmin.number, reference="987654")

        aReason = AdmissionsReason.objects.create(text="abc", detailRequired=False, editable=True)
        self.adRate = AdmissionsRate.objects.create(period_start=datetime.now() - timedelta(days=2), period_end=None, adult_cost="15",
                adult_overnight_cost="20", concession_cost="5", concession_overnight_cost="7", children_cost="5",
                children_overnight_cost="7", infant_cost="5", infant_overnight_cost="7", family_cost="30", family_overnight_cost="40",
                comment=None, reason=aReason)
        AdmissionsOracleCode.objects.create(oracle_code="0516")
        adBooking = AdmissionsBooking.objects.create(customer=None, booking_type=1, arrivalDate=datetime.now(), overnightStay=False,
                vesselRegNo="ABC123", noOfAdults=1, noOfConcessions=0, noOfChildren=0, noOfInfants=0, warningReferenceNo="", totalCost=10.50)

        openReason = mixer.blend(OpenReason, detailRequired=False)
        self.park = mixer.blend(MarinePark, zoom_level=1, oracle_code="0516")
        self.area = mixer.blend(MooringArea, park=mixer.SELECT)
        self.areaGroup = mixer.blend(MooringAreaGroup, moorings=self.area.id)
        self.site = mixer.blend(Mooringsite, mooringarea=self.area)
        self.bpo = mixer.blend(BookingPeriodOption)
        self.bp = mixer.blend(BookingPeriod, booking_period=self.bpo)
        self.bp2 = BookingPeriod.objects.create(name='selfbp2')
        self.siteRate = mixer.blend(MooringsiteRate, campsite=self.site, booking_period=self.bp)
        self.booking = mixer.blend(Booking, departure=datetime.now(), arrival=datetime.now()-timedelta(days=3), mooringarea=self.area)
        self.msBooking = mixer.blend(MooringsiteBooking, campsite=self.site, booking=self.booking, from_dt=(datetime.now()+timedelta(days=1)).date(), to_dt=(datetime.now()+timedelta(days=4)).date())
        # self.MABRange = mixer.blend(MooringAreaBookingRange, campground=self.area, skip_validation=True)

        self.adReason = mixer.blend(AdmissionsReason, detailRequired=False)
        self.prReason = mixer.blend(PriceReason, detailRequired=False)
        self.opReason = mixer.blend(OpenReason, detailRequired=False)
        
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key


        
        
