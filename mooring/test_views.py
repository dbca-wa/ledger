from .test_setup import TestSetup
from django.test import Client
from mixer.backend.django import mixer

from .models import *
from ledger.accounts.models import EmailUser, EmailUserManager

adminUN = "admin@website.domain"
nonAdminUN = "nonadmin@website.domain"

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
        self.client.login(username=adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the account view will load whilst logged in as non admin.
        """
        url = '/account/'
        self.client.login(username=nonAdminUN, password="pass")
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
        self.client.login(username=adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the admin view will redirect to login page whilst logged in as non admin.
        """
        url = '/admin/'
        self.client.login(username=nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class AdmissionsTestCase(TestSetup):
    def test_not_logged_in(self):
        """Test that the admissions view will load whilst not logged in.
        """
        url = '/admissions/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_admin(self):
        """Test that the admissions view will load whilst logged in as admin.
        """
        url = '/admissions/'
        self.client.login(username=adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the admissions view will load whilst logged in as non admin.
        """
        url = '/admissions/'
        self.client.login(username=nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

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
        self.client.login(username=adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the admissions costs view will not load whilst logged in as non admin.
        """
        url = '/admissions-cost/'
        self.client.login(username=nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 302)

class AvailabilityTestCase(TestSetup):
    """Test availability2 as availability is not used for moorings anymore.
    """
    def test_not_logged_in(self):
        """Test that the availability view will load whilst not logged in.
        """
        url = '/availability2/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_admin(self):
        """Test that the availability view will load whilst logged in as admin.
        """
        url = '/availability2/'
        self.client.login(username=adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the availability view will load whilst logged in as non-admin.
        """
        url = '/availability2/'
        self.client.login(username=nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

"""Would have availability_admin tested here however it seems broken/not in use at the moment."""

# class BookingTestCase(TestSetup):

class BookingAbortTestCase(TestSetup):
    def test_not_logged_in_no_booking(self):
        """Test that the booking abort view will redirect whilst not logged in and no booking.
        """
        url = '/booking/abort/'
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your session has expired");

    # def test_not_logged_in_with_booking(self):
    #     """Test that the booking abort view will load whilst not logged in and booking.
    #     """
    #     url = '/booking/abort/'
    #     booking = mixer.blend(Booking, mooringarea=None)
    #     request.session['ps_booking'] = booking.id
    #     response = self.client.get(url, HTTP_HOST="website.domain")
    #     self.assertEqual(response.status_code, 200)

    def test_logged_in_admin_no_booking(self):
        """Test that the booking abort view will redirect whilst logged in as admin and no booking.
        """
        url = '/booking/abort/'
        self.client.login(username=adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your session has expired");
    
    # def test_logged_in_admin_with_booking(self):
    #     """Test that the booking abort view will load whilst logged in as admin and booking.
    #     """
    #     url = '/booking/abort/'
    #     self.client.login(username=adminUN, password="pass")
    #     booking = mixer.blend(Booking)
    #     request.session['ps_booking'] = booking.id
    #     response = self.client.get(url, HTTP_HOST="website.domain")
    #     self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin_no_booking(self):
        """Test that the booking abort view will redirect whilst logged in as non-admin and no booking.
        """
        url = '/booking/abort/'
        self.client.login(username=nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your session has expired");

    # def test_logged_in_non_admin_with_booking(self):
    #     """Test that the booking abort view will redirect whilst logged in as non-admin and booking.
    #     """
    #     url = '/booking/abort/'
    #     self.client.login(username=nonAdminUN, password="pass")
    #     booking = mixer.blend(Booking)
    #     request.session['ps_booking'] = booking.id
    #     response = self.client.get(url, HTTP_HOST="website.domain")
    #     self.assertEqual(response.status_code, 200)



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
        self.client.login(username=adminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)

    def test_logged_in_non_admin(self):
        """Test that the map view will load whilst logged in as non-admin.
        """
        url = '/map/'
        self.client.login(username=nonAdminUN, password="pass")
        response = self.client.get(url, HTTP_HOST="website.domain")
        self.assertEqual(response.status_code, 200)