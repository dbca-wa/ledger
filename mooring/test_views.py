from .test_setup import TestSetup
from django.test import Client
from mixer.backend.django import mixer
from datetime import datetime, timedelta


from .models import *

#adminUN = "admin@website.domain"
#nonAdminUN = "nonadmin@website.domain"


class AccountTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the acount view will redirect to index page whilst not logged in.
        """
        url = '/account/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the account view will load whilst logged in as admin.
        """
        url = '/account/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the account view will load whilst logged in as non admin.
        """
        url = '/account/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

class AdminTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the admin view will redirect to login page whilst not logged in.
        """
        url = '/admin/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the admin view will load whilst logged in as admin.
        """
        url = '/admin/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the admin view will redirect to login page whilst logged in as non admin.
        """
        url = '/admin/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

#class AdmissionsTestCase(TestSetup):
#    def test_not_logged_in(self):
#        """Test that the admissions view will load whilst not logged in.
#        """
#        url = '/admissions/'
#        response = self.client.get(url, HTTP_HOST="website.domain")
#        self.assertEqual(response.status_code, 200)
#
#    def test_logged_in_admin(self):
#        """Test that the admissions view will load whilst logged in as admin.
#        """
#        url = '/admissions/'
#        self.client.login(username=self.adminUN, password="pass")
#        response = self.client.get(url, HTTP_HOST="website.domain")
#        self.assertEqual(response.status_code, 404) 
#
#    def test_logged_in_non_admin(self):
#        """Test that the admissions view will load whilst logged in as non admin.
#        """
#        url = '/admissions/'
#        self.client.login(username=self.nonAdminUN, password="pass")
#        response = self.client.get(url, HTTP_HOST="website.domain")
#        self.assertEqual(response.status_code, 200)

class AdmissionsCostTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the admissions costs view will not load whilst not logged in.
        """
        url = '/admissions-cost/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the admissions costs view will load whilst logged in as admin.
        """
        url = '/admissions-cost/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the admissions costs view will not load whilst logged in as non admin.
        """
        url = '/admissions-cost/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class AvailabilityTestCase(TestSetup):
    """Test availability2 as availability is not used for moorings anymore.
    """
    def test_not_logged_in(self):
        """Test that the availability view will load whilst not logged in.
        """
        url = '/availability2/'
        arrival = datetime.now().date().strftime('%Y/%m/%d')
        departure = datetime.now()+timedelta(days=2)
        departure = departure.date().strftime('%Y/%m/%d')
        response = self.client.get(url, {'arrival': arrival, 'departure': departure, 'site_id': self.area.id}, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_admin(self):
        """Test that the availability view will load whilst logged in as admin.
        """
        url = '/availability2/'
        arrival = datetime.now().date().strftime('%Y/%m/%d')
        departure = datetime.now()+timedelta(days=2)
        departure = departure.date().strftime('%Y/%m/%d')

        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, {'arrival': arrival, 'departure': departure, 'site_id': self.area.id}, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the availability view will load whilst logged in as non-admin.
        """
        url = '/availability2/'
        arrival = datetime.now().date().strftime('%Y/%m/%d')
        departure = datetime.now()+timedelta(days=2)
        departure = departure.date().strftime('%Y/%m/%d')

        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, {'arrival': arrival, 'departure': departure, 'site_id': self.area.id}, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

"""Would have availability_admin tested here however it seems broken/not in use at the moment."""

class BookingTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the booking view will load whilst not logged in.
        """
        url = '/booking/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)
#        self.assertContains(response, "Your session has expired");

    def test_logged_in_admin(self):
        """Test that the booking view will load whilst logged in as admin.
        """
        url = '/booking/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)
        #self.assertContains(response, "Your session has expired");

    def test_logged_in_non_admin(self):
        """Test that the booking view will load whilst logged in as non-admin.
        """
        url = '/booking/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)
#        self.assertContains(response, "Your session has expired");

class BookingAbortTestCase(TestSetup):
    """
    This does not seem to be working currently.
    The "Cancel in progress booking" button takes user to an unrelated
    (broken) URL. The user then has to manually 'back' to get to the 
    moorings website, and refresh in order to see that the current
    booking is cancelled. ============================== 29/10/2018 SE.
    """

    def test_not_logged_in_no_booking(self):
        """Test that the booking abort view will display an error whilst not logged in and no booking.
        """
        url = '/booking/abort/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)
#        self.assertContains(response, "Your session has expired");

    # def test_not_logged_in_with_booking(self):
    #     """Test that the booking abort view will load whilst not logged in and booking.
    #     """
    #     url = '/booking/abort/'
    #     park = mixer.blend(MarinePark, oracle_code="0516", zoom_level=0)
    #     start = datetime.now() - timedelta(days=1)
    #     end = start + timedelta(days=3)
    #     # bRange = BookingRange.objects.create(created=datetime.now(), updated_on=datetime.now(), status=0, closure_reason=None, open_reason=None, details=None, range_start=start, range_end=end)
    #     openReason = OpenReason.objects.create(text="blahsohaipheaf", detailRequired=False, editable=True)
    #     area = mixer.blend(MooringArea, park=park, open_reason_id=openReason.id)

    #     booking = mixer.blend(Booking, mooringarea=area)
    #     session = self.client.session
    #     session['ps_booking'] = booking.id
    #     session.save()
    #     response = self.client.get(url, HTTP_HOST="website.domain")
    #     self.assertEqual(response.status_code, 200)

    def test_logged_in_admin_no_booking(self):
        """Test that the booking abort view will display an error whilst logged in as admin and no booking.
        """
        url = '/booking/abort/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)
        #self.assertContains(response, "Your session has expired")
    
    # def test_logged_in_admin_with_booking(self):
    #     """Test that the booking abort view will load whilst logged in as admin and booking.
    #     """
    #     url = '/booking/abort/'
    #     park = mixer.blend(MarinePark, oracle_code="0516", zoom_level=0)
    #     start = datetime.now() - timedelta(days=1)
    #     end = start + timedelta(days=3)
    #     openReason = OpenReason.objects.create(text="blahsohaipheaf", detailRequired=False, editable=True)
    #     area = mixer.blend(MooringArea, park=park, open_reason_id=openReason.id)
    #     booking = mixer.blend(Booking, mooringarea=area)

    #     self.client.login(username=self.adminUN, password="pass")
    #     session = self.client.session
    #     session['ps_booking'] = booking.id
    #     session.save()

    #     response = self.client.get(url, HTTP_HOST="website.domain")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "Your session has expired")

    def test_logged_in_non_admin_no_booking(self):
        """Test that the booking abort view will display an error whilst logged in as non-admin and no booking.
        """
        url = '/booking/abort/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code,302)
 #       self.assertContains(response, "Your session has expired");

    # def test_logged_in_non_admin_with_booking(self):
    #     """Test that the booking abort view will redirect whilst logged in as non-admin and booking.
    #     """
    #     url = '/booking/abort/'
    #     self.client.login(username=self.nonAdminUN, password="pass")
    #     booking = mixer.blend(Booking)
    #     request.session['ps_booking'] = booking.id
    #     response = self.client.get(url, HTTP_HOST="website.domain")
    #     self.assertEqual(response.status_code, 200)

class CreatedBasketTestCase(TestSetup):
    def test_not_logged_in_no_basket(self):
        """Test that the basket view will redirect whilst not logged in and no basket.
        """
        url = '/createdbasket/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin_no_basket(self):
        """Test that the basket view will redirect whilst logged in as admin and no basket.
        """
        url = '/createdbasket/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_non_admin_no_basket(self):
        """Test that the basket view will redirect whilst logged in as non-admin and no basket.
        """
        url = '/createdbasket/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    #Need to add tests including basket items.


class DashboardTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the dashboard view will redirect whilst not logged in.
        """
        url = '/dashboard/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the dashboard view will load whilst logged in as admin.
        """
        url = '/dashboard/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the dashboard view will redirect whilst not logged in as admin.
        """
        url = '/dashboard/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class DashboardBookingsTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the dashboard bookings view will redirect whilst not logged in.
        """
        url = '/dashboard/bookings'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the dashboard bookings view will load whilst logged in as admin.
        """
        url = '/dashboard/bookings'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the dashboard bookings view will redirect whilst not logged in as admin.
        """
        url = '/dashboard/bookings'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class DashboardBookingsEditTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the dashboard bookings edit view will redirect whilst not logged in.
        """
        url = '/dashboard/bookings/edit/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the dashboard bookings edit view will load whilst logged in as admin.
        """
        url = '/dashboard/bookings/edit/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the dashboard bookings edit view will redirect whilst not logged in as admin.
        """
        url = '/dashboard/bookings/edit/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class DashboardBookingPeriodsTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the dashboard booking period view will redirect whilst not logged in.
        """
        url = '/dashboard/bookingperiod/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the dashboard bookings period view will load whilst logged in as admin.
        """
        url = '/dashboard/bookingperiod/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the dashboard booking period view will redirect whilst not logged in as admin.
        """
        url = '/dashboard/bookingperiod/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class DashboardBulkpricingTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the dashboard bulkpricing view will redirect whilst not logged in.
        """
        url = '/dashboard/bulkpricing/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the dashboard bulkpricing view will load whilst logged in as admin.
        """
        url = '/dashboard/bulkpricing/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the dashboard bulkpricing view will redirect whilst not logged in as admin.
        """
        url = '/dashboard/bulkpricing/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class DashboardMooringsTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the dashboard moorings view will redirect whilst not logged in.
        """
        url = '/dashboard/moorings/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the dashboard moorings view will load whilst logged in as admin.
        """
        url = '/dashboard/moorings/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the dashboard moorings view will redirect whilst not logged in as admin.
        """
        url = '/dashboard/moorings/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class DashboardMooringSiteTypesTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the dashboard mooringsite types view will redirect whilst not logged in.
        """
        url = '/dashboard/mooringsite-types'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the dashboard mooringsite types view will load whilst logged in as admin.
        """
        url = '/dashboard/mooringsite-types'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the dashboard mooringsite types view will redirect whilst not logged in as admin.
        """
        url = '/dashboard/mooringsite-types'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class MapTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the map view will load whilst not logged in.
        """
        url = '/map/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_admin(self):
        """Test that the map view will load whilst logged in as admin.
        """
        url = '/map/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the map view will load whilst logged in as non-admin.
        """
        url = '/map/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

class MyBookingsTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the mybookings view will load whilst not logged in.
        """
        url = '/mybookings/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the mybookings view will load whilst logged in as admin.
        """
        url = '/mybookings/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the mybookings view will load whilst logged in as non-admin.
        """
        url = '/mybookings/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

class SuccessTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the success view will redirect whilst not logged in and no booking made.
        """
        url = '/success/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the success view will redirect whilst logged in as admin and no booking made.
        """
        url = '/success/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_non_admin(self):
        """Test that the success view will redirect whilst logged in as non-admin and no booking made.
        """
        url = '/success/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    #Will need to test with booking made.

class SuccessAdmissionsTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the success admissions view will redirect whilst not logged in and no payment made.
        """
        url = '/success_admissions/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

    def test_logged_in_admin(self):
        """Test that the success admissions view will redirect whilst logged in as admin and no payment made.
        """
        url = '/success_admissions/'
        self.client.login(username=self.adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

        #Will need to test with payment made.

    def test_logged_in_non_admin(self):
        """Test that the success admissions view will redirect whilst logged in as non-admin and no payment made.
        """
        url = '/success_admissions/'
        self.client.login(username=self.nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

#class PaymentPDFInvoiceTestCase(TestSetup):
#
#    def set_invoices(self):
#        pass
#
#    def test_logged_in_admin_own_order(self):
#        """Test that the payment PDF view will load whilst logged in as admin, and admin is owner of order.
#        """
#        self.set_invoices()
#        url = '/mooring/payments/invoice-pdf/123456'
#        self.client.login(username=self.adminUN, password="pass")
#        response = self.client.get(url, HTTP_HOST="website.domain")
#        self.assertEqual(response.status_code, 200)
#
#    def test_logged_in_non_admin_own_order(self):
#        """Test that the payment PDF view will load whilst logged in as non-admin and non-admin is owner of order.
#        """
#        self.set_invoices()
#        url = '/mooring/payments/invoice-pdf/987654'
#        self.client.login(username=self.nonAdminUN, password="pass")
#        response = self.client.get(url, HTTP_HOST="website.domain")
#        self.assertEqual(response.status_code, 200)
#
#    def test_logged_in_admin_not_owner(self):
#        """Test that the payment PDF view will load whilst logged in as non-admin and non-admin is owner of order.
#        """
#        self.set_invoices()
#        url = '/mooring/payments/invoice-pdf/987654'
#        self.client.login(username=self.adminUN, password="pass")
#        response = self.client.get(url, HTTP_HOST="website.domain")
#        self.assertEqual(response.status_code, 403)
#
#    def test_logged_in_non_admin_not_owner(self):
#        """Test that the payment PDF view will not load whilst logged in as non-admin, and admin is owner of order.
#        """
#        self.set_invoices()
#        url = '/mooring/payments/invoice-pdf/123456'
#        self.client.login(username=self.nonAdminUN, password="pass")
#        response = self.client.get(url, HTTP_HOST="website.domain")
#        self.assertEqual(response.status_code, 403)
#
#    def test_not_logged_in_not_owner(self):
#        """Test that the payment PDF view not will load whilst logged in as non-admin, and admin is owner of order.
#        """
#        self.set_invoices()
#        url = '/mooring/payments/invoice-pdf/123456'
#        response = self.client.get(url, HTTP_HOST="website.domain")
#        self.assertEqual(response.status_code, 403)
