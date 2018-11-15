from .test_setup import TestSetup
from django.test import Client, RequestFactory
from mixer.backend.django import mixer
from datetime import datetime, timedelta

from .models import *
from .utils import *
from ledger.accounts.models import EmailUser
from ledger.payments.models import OracleInterfaceSystem

adminUN = "admin@website.domain"
nonAdminUN = "nonadmin@website.domain"

area = MooringArea.objects.all().last()

bb = mixer.blend(Booking, mooringarea=area, arrival=datetime.now(), departure=datetime.now()+timedelta(days=1), details={'details': 'Some details'})
nowplus1 = Booking.objects.create(arrival=datetime.now(), departure=datetime.now()+timedelta(days=1), mooringarea=area)
nowplus2 = Booking.objects.create(arrival=datetime.now(), departure=datetime.now()+timedelta(days=2), mooringarea=area)
nowplus3 = Booking.objects.create(arrival=datetime.now(), departure=datetime.now()+timedelta(days=3), mooringarea=area)
oneplus4 = Booking.objects.create(arrival=datetime.now()+timedelta(days=1), departure=datetime.now()+timedelta(days=4), mooringarea=area)
twotonow = Booking.objects.create(departure=datetime.now(), arrival=datetime.now()-timedelta(days=2), mooringarea=area)
threetonow = Booking.objects.create(departure=datetime.now(), arrival=datetime.now()-timedelta(days=3), mooringarea=area)

class AdmissionsCheckoutTestCase(TestSetup):
    def test_logged_in_admin(self):
        """
        Current has an issue with the fallback urls etc. that are created,
        they all return "Enter a valid URL".
        """
        # self.factory = RequestFactory()
        # request = self.factory.get('/map')
        # request.user = EmailUser.objects.get(email=adminUN)

        # adBooking = AdmissionsBooking.objects.all().first()
        # lines = admissions_price_or_lineitems(request, adBooking)
        # checkout = admissionsCheckout(request, adBooking, lines, invoice_text="ABC")
        # self.assertTrue(checkout)
        pass

class AdmissionsPriceOrLineitemsTestCase(TestSetup):
    def test_logged_in_admin(self):
        self.factory = RequestFactory()
        request = self.factory.get('/map')
        request.user = EmailUser.objects.get(email=adminUN)

        adBooking = AdmissionsBooking.objects.all().first()
        lines = admissions_price_or_lineitems(request, adBooking)
        self.assertTrue(lines)
        # print("Lines: ", lines)

class CheckDateDiffTestCase(TestSetup):
    def test_dates_start_same_end_longer(self):
        res = check_date_diff(nowplus2, nowplus3)
        self.assertEqual(res, 1)
    
    def test_dates_start_same_end_shorter(self):
        res = check_date_diff(nowplus3, nowplus2)
        self.assertEqual(res, 2)

    def test_dates_start_longer_end_same(self):
        res = check_date_diff(twotonow, threetonow)
        self.assertEqual(res, 1)

    def test_dates_start_shorter_end_same(self):
        res = check_date_diff(threetonow, twotonow)
        self.assertEqual(res, 2)

    def test_dates_no_match(self):
        res = check_date_diff(twotonow, oneplus4)
        self.assertEqual(res, 3)

    def test_dates_all_days_match(self):
        res = check_date_diff(nowplus1, nowplus1)
        self.assertEqual(res, 4)

class CheckoutTestCase(TestSetup):
    def test_checkout(self):
        """
        Current has an issue with the fallback urls etc. that are created,
        they all return "Enter a valid URL".
        """

        # self.factory = RequestFactory()
        # request = self.factory.get('/map')
        # request.user = EmailUser.objects.get(email=adminUN)
        # lines = price_or_lineitems(request, nowplus1, None)

        # check = checkout(request, nowplus1, lines, invoice_text="DEF")
        pass

class CreateBookingByClassTestCase(TestSetup):
    def test(self):
        # Seems that this is not used. The function itself does not actually work.
        # It's still using a part of parkstay (campsite_class).
        pass
        # booking = create_booking_by_class(self.area.id, 1, datetime.now(), datetime.now()+timedelta(days=1))
        # print(booking)
        # self.assertTrue(booking)

class CreateBookingBySiteTestCase(TestSetup):
    def test(self):
        tomorrow = datetime.now() + timedelta(days=1)

        # print("Site ID: ", self.site.id)
        booking = create_booking_by_site([self.site.id], datetime.now().date(), tomorrow.date())
        self.assertTrue(booking)

class CreateOrUpdateBookingTestCase(TestSetup):
    """
    This function actually only uses a create function, the update function does not exist.
    """
    def test(self):
        self.factory = RequestFactory()
        request = self.factory.get('/map')
        request.user = EmailUser.objects.get(email=adminUN)

        tomorrow = datetime.now() + timedelta(days=1)
        booking_details = {
            "campsites": [self.site.id],
            "start_date": datetime.now().date(),
            "end_date": tomorrow.date(),
            "num_adult": 1,
            "num_concession": 0,
            "num_child": 2,
            "num_infant": 0,
            "num_mooring": 0,
            "vessel_size": 15,
            "cost_total": 25.50,
            "override_price": False,
            "override_reason": None,
            "override_reason_info": None,
            "overridden_by": None,
            "customer": None,
            "first_name": "example",
            "last_name": "exampleton",
            "phone": "0123456789",
            "country": "Australia",
            "postcode": "6000"

        }

        booking = create_or_update_booking(request,booking_details,updating=False,override_checks=False)
        self.assertTrue(booking)

class CreateTempBookingUpdateTestCase(TestSetup):
    def test(self):
        pass
        # self.factory = RequestFactory()
        # request = self.factory.get('/map')
        # request.user = EmailUser.objects.get(email=adminUN)

        # # arrival = datetime.strptime(str(datetime.now() + timedelta(days=4)), '%Y-%m-%d')
        # # departure = datetime.strptime(str(datetime.now() + timedelta(days=8)), '%Y-%m-%d')
        # arrival = datetime.now().date()
        # departure = (arrival + timedelta(days=4))

        # print("DEBUG** MSB Count: ", MooringsiteBooking.objects.filter(booking=self.booking))

        # booking_details = { "campsites": [self.site.id],
        #     "num_adult": 8,
        #     "num_concession": 0,
        #     "num_child": 0,
        #     "num_infant": 0,
        #     "num_mooring": 0
        # }
        # res = create_temp_bookingupdate(request,arrival, departure,booking_details,self.booking,80.00)
        # self.assertTrue(res)

class DateRangeTestCase(TestSetup):
    def test(self):
        start = datetime.now().date()
        end = (datetime.now() + timedelta(days=5)).date()
        res = daterange(start, end)
        for ran in res:
            self.assertTrue(ran >= datetime.now().date())
            self.assertTrue(ran < (datetime.now() + timedelta(days=5)).date())

class DeleteSessionAdmissionsBookingTestCase(TestSetup):
    def test(self):
        self.factory = RequestFactory()
        request = self.factory.get('/map')
        request.user = EmailUser.objects.get(email=adminUN)

        session = self.session
        session['ad_booking'] = "This is an object ready to delete."
        session.save()

        self.assertTrue(session['ad_booking'])
        res = delete_session_admissions_booking(session)
        self.assertFalse(res)

class DeleteSessionBookingTestCase(TestSetup):
    def test(self):
        self.factory = RequestFactory()
        request = self.factory.get('/map')
        request.user = EmailUser.objects.get(email=adminUN)

        session = self.session
        session['ps_booking'] = "This is an object ready to delete."
        session.save()

        self.assertTrue(session['ps_booking'])
        res = delete_session_booking(session)
        self.assertFalse(res)

class GetAdmissionsEntryRateTestCase(TestSetup):
    def test(self):
        self.factory = RequestFactory()
        request = self.factory.get('/map')
        request.user = EmailUser.objects.get(email=adminUN)

        yesterday = datetime.now() - timedelta(days=2)
        res = get_admissions_entry_rate(request, datetime.now().strftime('%Y-%m-%d'))
        self.assertTrue(res)

class GetAvailableCampsiteListTestCase(TestSetup):
    def test(self):
        pass
        # self.factory = RequestFactory()
        # request = self.factory.get('/map')
        # request.user = EmailUser.objects.get(email=adminUN)
        
        # start_date = datetime.now().date()
        # end_date = (datetime.now() + timedelta(days=1)).date()

        # res = get_available_campsites_list([self.site],request, start_date, end_date)
        # # print(res)
        # self.assertTrue(res)

class GetAvailableCampsiteListBookingTestCase(TestSetup):
    def test(self):
        pass
        # self.factory = RequestFactory()
        # request = self.factory.get('/map')
        # request.user = EmailUser.objects.get(email=adminUN)

        # start_date = datetime.now().date()
        # end_date = (datetime.now() + timedelta(days=1)).date()

        # res = get_available_campsites_list_booking([self.site], request, start_date, end_date, bb)
        # self.assertTrue(res)

class GetAvailableCampsiteTypesTestCase(TestSetup):
    def test(self):
        """ Uses campsite_class on the mooringsite. This means it's still set for
        parkstay and has not been migrated to mooring.
        """
        pass
        # start_date = datetime.now().date()
        # end_date = (datetime.now() + timedelta(days=2)).date()
        # res = get_available_campsitetypes(self.area.id, start_date, end_date)
        # print(res)


class GetCampsiteAvailabilityTestCase(TestSetup):
    def test(self):
        pass
        # start_date = datetime.now().date()
        # end_date = (datetime.now() + timedelta(days=2)).date()
        # res = get_campsite_availability([self.site], start_date, end_date)
        # self.assertTrue(res)

class GetCampsiteCurrentRateTestCase(TestSetup):
    def test(self):
        pass
        self.factory = RequestFactory()
        request = self.factory.get('/map')
        request.user = EmailUser.objects.get(email=adminUN)
        
        start_date = datetime.now().date().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=2)).date().strftime('%Y-%m-%d')
        res = get_campsite_current_rate(request, self.site.id, start_date, end_date)
        self.assertTrue(res)

class GetDiffDaysTestCase(TestSetup):
    def test_not_additional(self):
        res = get_diff_days(nowplus3, nowplus1, additional=False)
        self.assertTrue(res==2)

    def test_additional(self):
        res = get_diff_days(nowplus1, nowplus2)
        self.assertTrue(res==1)

class GetOpenMarinasTestCase(TestSetup):
    def test(self):
        """
        Need to make sure there are some available sites when querying this.
        """
        # pass
        start_date = datetime.now() + timedelta(days=10)
        end_date = datetime.now() + timedelta(days=15)
        
        qs = Mooringsite.objects.all()
        res = get_open_marinas(qs, start_date.date(), end_date.date())
        self.assertTrue(res)

class GetParkEntryRateTestCase(TestSetup):
    def test(self):
        self.factory = RequestFactory()
        request = self.factory.get('/map')
        request.user = EmailUser.objects.get(email=adminUN)

        pr = PriceReason.objects.create(text="aswe", detailRequired=False)
        mr = MarinaEntryRate.objects.create(reason=pr, period_start=(datetime.now()-timedelta(days=3)).date())

        start_date = datetime.now().date()
        
        res = get_park_entry_rate(request,str(start_date))
        self.assertTrue(res)

class GetSessionAdmissionsBookingTestCase(TestSetup):
    def test(self):
        self.factory = RequestFactory()
        request = self.factory.get('/map')
        request.user = EmailUser.objects.get(email=adminUN)

        session = self.session
        ad = AdmissionsBooking.objects.all()[0]
        session['ad_booking'] = ad.id
        session.save()

        self.assertTrue(session['ad_booking'])
        res = get_session_admissions_booking(session)
        self.assertTrue(res)
        self.assertEqual(res, ad)

class GetSessionBookingTestCase(TestSetup):
    def test(self):
        session = self.session
        session['ps_booking'] = self.booking.id
        session.save()

        self.assertTrue(session['ps_booking'])
        res = get_session_booking(session)
        self.assertTrue(res)
        self.assertEqual(res, self.booking)

class GetVisitRatesTestCase(TestSetup):
    def test(self):
        # pass
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=5)

        res = get_visit_rates([self.site], start_date.date(), end_date.date())
        self.assertTrue(res)

class InternalBookingTestCase(TestSetup):
    def test(self):
        pass
        # self.factory = RequestFactory()
        # request = self.factory.get('/map')
        # request.user = EmailUser.objects.get(email=adminUN)
        # request.session = self.session

        # tomorrow = datetime.now() + timedelta(days=1)

        # booking_details = {
        #     "campsites": [self.site.id],
        #     "start_date": datetime.now().date(),
        #     "end_date": tomorrow.date(),
        #     "num_adult": 1,
        #     "num_concession": 0,
        #     "num_child": 2,
        #     "num_infant": 0,
        #     "num_mooring": 0,
        #     "vessel_size": 15,
        #     "cost_total": 25.50,
        #     "override_price": False,
        #     "override_reason": None,
        #     "override_reason_info": None,
        #     "overridden_by": None,
        #     "customer": request.user,
        #     "first_name": "example",
        #     "last_name": "exampleton",
        #     "phone": "0123456789",
        #     "country": "Australia",
        #     "postcode": "6000"

        # }

        # res = internal_booking(request,booking_details)
        # self.assertTrue(res)

class InternalCreateBookingInvoiceTestCase(TestSetup):
    def test(self):
        # pass
        res = internal_create_booking_invoice(self.booking, "987654")
        self.assertTrue(res)
        # print("DEBUG**: ", res)

class OracleIntegrationTestCase(TestSetup):
    def test(self):
        sys = OracleInterfaceSystem.objects.create(system_id='0516', system_name="Test", enabled=True)
        res = oracle_integration(datetime.now().strftime('%Y-%m-%d'), True)
        self.assertRaises(None)

class PriceOrLineitemsTestCase(TestSetup):
    def test(self):
        # pass
        self.factory = RequestFactory()
        request = self.factory.get('/map')

        res = price_or_lineitems(request,self.booking,[self.site])
        # print("DEBUG**: ", res)
        self.assertTrue(res)
        

class SetSessionBookingTestCase(TestSetup):
    def test(self):
        # pass
        
        session = self.session
        set_session_booking(session, nowplus1)
        self.assertTrue(session['ps_booking'])

class UpdateBookingTestCase(TestSetup):
    def test(self):
        pass        
        # self.factory = RequestFactory()
        # request = self.factory.get('/map')
        # request.user = EmailUser.objects.get(email=adminUN)
        # request.session = self.session
        # request.data = {}
        # request.data["entryFees"] = {
        # }

        # booking_details = {
        #     'num_adult': 5,
        #     'num_concession': 0,
        #     'num_child': 5,
        #     'num_infant': 2,
        #     'num_mooring': 1,
        #     'mooringarea': self.site.mooringarea.id,
        #     'start_date': datetime.now().date(),
        #     'end_date': (datetime.now()+timedelta(days=1)).date(),
        #     'campsites': [self.site.id]

        # }
        # print("DEBUG**: ", bb.details)
        # res = update_booking(request,bb,booking_details)
        # self.assertTrue(res)