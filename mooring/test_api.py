from .test_setup import TestSetup
from django.test import Client, RequestFactory
from mixer.backend.django import mixer
from datetime import datetime, timedelta
import json
import sys
from .models import *

#superAdminUN = 'test.superadmin@dbca.wa.gov.au'
#adminUN = 'test.admin@dbca.wa.gov.au'
#nonAdminUN = 'test.customer@dbca.wa.gov.au'


class AdmissionsBookingViewSetTestCase(TestSetup):
    url = '/api/admissionsbooking/'

    def test_api_get_admin(self):
        """Test the Admissions Booking API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Admissions Booking API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test that anonymous users can't use the Admissions Booking endpoint
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_post_to_api(self):
        """Test the Admissions Booking API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url, {'arrival': '01-01-1970'})
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Admissions Booking API endpoint POST response when logged in as non admin user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url, {'arrival': '01-01-1970'})
        self.assertEqual(response.status_code, 403)
    
    def test_api_post_anon(self):
        """Test the Admissions Booking API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url, {'arrival': '01-01-1970'})
        self.assertEqual(response.status_code, 403)

class AdmissionsRatesViewSetTestCase(TestSetup):
    # url = '/api/admissions/price_history.json'
    url2 = "/api/admissions/add_price.json"
    url = '/api/admissions/'
    start_date = datetime.now() + timedelta(days=3)
    end_date = datetime.now() + timedelta(days=7)
    data = {
        'period_start' : "{}-{}-{}".format(start_date.year, start_date.month, start_date.day),
        'period_end' : "{}-{}-{}".format(end_date.year, end_date.month, end_date.day),
        'adult_cost' : 12.00,
        'adult_overnight_cost' : 17.00,
        'children_cost' : 5.00,
        'children_overnight_cost' : 7.00,
        'infant_cost' : 1.00,
        'infant_overnight_cost' : 2.00,
        'family_cost' : 30.00,
        'family_overnight_cost' : 42.00,
        'comment' : "aisjhdakjd;ajdsad",
        'editable' : False,
    }

    def test_api_get_admin(self):
        """Test the Admissions Rates API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Admissions Rates API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_anon(self):
        """Test the Admissions Rates API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_post_admin(self):
        """Test the Admissions Rates API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        self.data['reason'] = self.adReason.id
        self.data['mooring_group'] = self.ria.id
        response = self.client.post(self.url2, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_api_post_non_admin(self):
        """Test the Admissions Rates API endpoint POST response when logged in as non admin user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url2, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_api_post_anon(self):
        """Test the Admissions Rates API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url2, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_delete_admin(self):
        """Test the Admissions Rates API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        id = AdmissionsRate.objects.all()[0].id
        url = self.url + str(id) + ".json"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_api_delete_non_admin(self):
        """Test the Admissions Rates API endpoint POST response when logged in as non admin user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.delete(self.url + str(self.adRate.id) + ".json")
        self.assertEqual(response.status_code, 204)
    
    def test_api_delete_anon(self):
        """Test the Admissions Rates API endpoint POST response when not logged in.
        """
        response = self.client.delete(self.url + str(self.adRate.id) + ".json")
        self.assertEqual(response.status_code, 403)


class AdmissionsReasonViewSetTestCase(TestSetup):
    url = '/api/admissionsReasons/'

    def test_api_get_admin(self):
        """Test the Admissions Reason API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Admissions Reason API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Admissions Reason API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Admissions Reason API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_get_non_admin(self):
        """Test the Admissions Reasons API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Admissions Reasons API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)


# Currently errors that mooringarea has no mooring_group.
# class AvailabilityAdminViewSetTestCase(TestSetup):
#     url = '/api/availability_admin/'

#     def test_api_get_admin(self):
#         """Test the Availability Admin API endpoint GET response when logged in as admin user.
#         """
#         self.client.login(email=adminUN, password='pass')
#         print "DEBUG: ", self.area
#         print "DEBUG: ", self.areaGroup.moorings
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)

#     def test_api_get_non_admin(self):
#         """Test the Availability Admin API endpoint GET response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_get_anon(self):
#         """Test the Admissions Admin API endpoint GET response when not logged in.
#         """
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_admin(self):
#         """Test the Admissions Admin API endpoint POST response when logged in as admin user.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 405)

#     def test_api_post_non_admin(self):
#         """Test the Availability Admin API endpoint POST response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_anon(self):
#         """Test the Availability Admin API endpoint POST response when not logged in.
#         """
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

""" Believe this API endpoint is no longer used."""
# class AvailabilityRatisViewSetTestCase(TestSetup):
#     url = '/api/availability_ratis/'

#     def test_api_get_admin(self):
#         """Test the Availability Ratis API endpoint GET response when logged in as admin user.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)


""" Get error: MooringArea object has no attribute 'mooring_group'
"""
# class AvailabilityViewSet2TestCase(TestSetup):
#     url = '/api/availability2/'

#     def test_api_get_admin(self):
#         """Test the Availability View Set (2) API endpoint GET response when logged in as admin.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)

class BookingPeriodOptionsViewSetTestCase(TestSetup):
    url = '/api/bookingPeriodOptions/'

    def test_api_get_admin(self):
        """ Test the Booking Period Options API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """ Test the Booking Period Options API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """ Test the Booking Period Options API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """ Test the Booking Period Options API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """ Test the Booking Period Options API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """ Test the Booking Period Options API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

#    def test_api_delete_admin(self):
#        """ Test the Booking Period Options API endpoint POST Delete response when logged in as admin.
#        """
#        self.assertTrue(self.bpo)
#        self.client.login(email=self.adminUN, password='pass')
#
#        bpo = mixer.blend(BookingPeriodOption)
#        bpo.save()
#        id = bpo.id
#        url = self.url + str(id) + ".json"
#        response = self.client.delete(url)
#        self.assertEqual(response.status_code, 403)
#        try:
#            bpo = BookingPeriodOption.objects.get(id=id)
#        except BookingPeriodOption.DoesNotExist:
#            bpo = None
#        self.assertFalse(bpo)

    def test_api_delete_non_admin(self):
        """ Test the Booking Period Options API endpoint POST Delete response when logged in as non-admin.
        """
        self.url = self.url + str(self.bpo.id) + "/"
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_delete_anon(self):
        """ Test the Booking Period Options API endpoint POST Delete response when not logged in.
        """
        self.url = self.url + str(self.bpo.id) + "/"
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)


class BookingPeriodViewSetTestCase(TestSetup):
    url = '/api/bookingPeriod/'
    data = {}

    def test_api_get_admin(self):
        """ Test the Booking Period API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """ Test the Booking Period API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """ Test the Booking Period API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """ Test the Booking Period API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        self.data['name'] = 'name123456'
        self.data['booking_period'] = [self.bpo.id]
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_api_post_non_admin(self):
        """ Test the Booking Period API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        self.data['name'] = 'name123456'
        self.data['booking_period'] = [self.bpo.id]
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """ Test the Booking Period API endpoint POST response when not logged in.
        """
        self.data['name'] = 'name123456'
        self.data['booking_period'] = [self.bpo.id]
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        
    def test_api_update_admin(self):
        """ Test the Booking Period API endpoint PUT response with parameter response when logged in as admin user.
        """
        self.url = self.url + str(self.bp.id) + "/"
        self.client.login(email=self.adminUN, password='pass')
        self.data['name'] = 'name123456'
        self.data['booking_period'] = [self.bpo.id]
        response = self.client.put(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 200) 

    def test_api_update_non_admin(self):
        """ Test the Booking Period API endpoint PUT response with parameter response when logged in as external user.
        """
        self.url = self.url + str(self.bp.id) + "/"
        self.client.login(email=self.nonAdminUN, password='pass')
        self.data['name'] = 'name123456'
        self.data['booking_period'] = [self.bpo.id]
        response = self.client.put(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_update_anon(self):
        """ Test the Booking Period API endpoint PUT response with parameter response when not logged in.
        """
        self.url = self.url + str(self.bp.id) + "/"
        self.data['name'] = 'name123456'
        self.data['booking_period'] = [self.bpo.id]
        response = self.client.put(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)


""" Unsure how to test this."""
# class BookingRefundsReportViewTestCase(TestSetup):
#     url = 'api/reports/booking_refunds'
#     data = {}

#     def test_api_get_admin(self):
#         """ Test the Booking Refunds Report API endpoint GET response logged in as admin user.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertTrue(response.status_code, 200)


# Same as above.
# class BookingReportViewTestCase(TestSetup):
    # url = 'api/reports/bookings'


# Same as above.
# class BookingSettlementReportView(TestSetup):
#     url = 'api/reports/booking_settlements'


class BookingViewSetTestCase(TestSetup):

#    print "--==================BookingViewSetTestCase=======================================-------"
#    print adminUN
#    print "--==================BookingViewSetTestCase=======================================-------" 
    url = '/api/booking/'
    start_date = datetime.now()
    end_date = datetime.now() + timedelta(days=3)
    data = {
        'arrival' : "{}/{}/{}".format(start_date.year, start_date.month, start_date.day),
        'departure' : "{}/{}/{}".format(end_date.year, end_date.month, end_date.day),
        'guests' : {
            'adult' : 2,
            'concession' : 0,
            'child' : 1,
            'infant' : 0,
            'mooring' : None
        },
        'costs' : {
            'total' : 33.00
        },
        'customer' : {
            'email' : '',
            'first_name' : "John",
            'last_name' : "Doe",
            'phone' : '01234567890',
            'country' : "Australia",
            'postcode' : '6000'
        },
    }

    def test_api_get_admin(self):
        """ Test the Booking View API endpoint GET response logged in as admin user.
        """
        self.data['customer']['email'] = self.adminUN
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertTrue(response.status_code, 200)

    def test_api_get_non_admin(self):
        """ Test the Booking View API endpoint GET response when logged in as external user.
        """
        self.data['customer']['email'] = self.adminUN
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """ Test the Booking View API endpoint GET response when not logged in.
        """
        self.data['customer']['email'] = self.adminUN
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    # Using post should work, however changes to utils has broken the calls.
    # The API does not seem to include a vessel_size parameter in the booking_details
    # variable. Because of this we get a 400 response and the object does not create. 
    # Non admin and anon calls do respond with 403, as expected so will leave them.
    # def test_api_post_admin(self):
    #     """ Test the Booking View API endpoint POST response when logged in as admin user.
    #     """
    #     self.client.login(email=adminUN, password='pass')
    #     self.data['campsites'] = [self.site.id]
    #     print "DEBUG: ", self.data
    #     response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
    #     self.assertEqual(response.status_code, 200)

    def test_api_post_non_admin(self):
        """ Test the Booking View API endpoint POST response when logged in as external user.
        """
        self.data['customer']['email'] = self.adminUN
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """ Test the Booking View API endpoint POST response when not logged in.
        """
        self.data['customer']['email'] = self.adminUN
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)


class BulkPricingViewTestCase(TestSetup):
    url = '/api/bulkPricing/'
    data = {}

    def test_api_get_admin(self):
        """ Test the Bulk Pricing API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_get_non_admin(self):
        """ Test the Bulk Pricing API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """ Test the Bulk Pricing API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    # Serializer (BulkPricingSerializer) validates against Marina.objects, which does not
    # exist in models. Therefore believe this is old, and no longer used. Post requests
    # fail because the model created cannot be validated when serialized.
    # def test_api_post_admin(self):
    #     """ Test the Bulk Pricing API endpoint POST response when logged in as admin user.
    #     """
    #     self.client.login(email=adminUN, password='pass')
    #     start_date = datetime.now().date()
    #     self.data = {
    #         'park' : self.park.id,
    #         'campgrounds' : [1],
    #         'adult' : 10.00,
    #         'concession' : 8.00,
    #         'child' : 6.00,
    #         'period_start' : "{}/{}/{}".format(start_date.day, start_date.month, start_date.year),
    #         'reason' : 1,
    #         'details' : "Text here for details",
    #         'type' : 1
    #     }
    #     print "DEBUG: ", self.data
    #     response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
    #     self.assertEqual(response.status_code, 200)

    def test_api_post_non_admin(self):
        """ Test the Bulk PricingAPI endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """ Test the Bulk Pricing API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

class ClosureReasonViewSetTestCase(TestSetup):
    url = '/api/closureReasons/'

    def test_api_get_admin(self):
        """ Test the Closure Reason API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Closure Reason API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Closure Reason API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Closure Reason API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Closure Reason API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Closure Reason API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

class ContactViewSetTestCase(TestSetup):
    url = '/api/contacts/'
    data = {
        'name' : "Testing Contact",
        'phone_number' : "01234567890",
        'email' : '',
        'description' : "Some text..",
        'opening_hours' : "Some more text",
        'other_services' : "Other services"
    }

    def test_api_get_admin(self):
        """ Test the Contact View API endpoint GET response when logged in as admin user.
        """
        self.data['email'] = self.adminUN
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Contact View API endpoint GET response when logged in as external user.
        """
        self.data['email'] = self.adminUN
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Contact View API endpoint GET response when not logged in.
        """
        self.data['email'] = self.adminUN
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Contact View API endpoint POST response when logged in as admin user.
        """
        self.data['email'] = self.adminUN
        self.data['mooring_group'] = self.ria.id
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_api_post_non_admin(self):
        """Test the Contact View API endpoint POST response when logged in as external user.
        """
        self.data['email'] = self.adminUN
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Contact View API endpoint POST response when not logged in.
        """
        self.data['email'] = self.adminUN
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

class CountryViewSetTestCase(TestSetup):
    url = '/api/countries/'

    def test_api_get_admin(self):
        """ Test Country View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Country View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_anon(self):
        """Test the Country View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Country View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Country View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_anon(self):
        """Test the Country View API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

class DistrictViewSetTestCase(TestSetup):
    url = '/api/districts/'
    data = {
        'name' : "A Name",
        'abbreviation' : "Nme",
        'ratis_id' : -1
    }

    def test_api_get_admin(self):
        """ Test the District View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the District View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the District View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the District View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        self.data['region'] = self.region.id
        self.data['mooring_group'] = self.ria.id

        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_api_post_non_admin(self):
        """Test the District View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the District View API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

class FeatureViewSetTestCase(TestSetup):
    url = '/api/features/'
    data = {
        'name' : "A Name",
        'description': "Description text",
        'image' : None
    }

    def test_api_get_admin(self):
        """ Test the Feature View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Feature View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Feature View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Feature View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_api_post_non_admin(self):
        """Test the Feature View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Feature View API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)


class GetProfileTestCase(TestSetup):
    url = '/api/profile'

    def test_api_get_admin(self):
        """ Test the Get Profile API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        json_resp =  response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_resp["email"], self.adminUN)

    def test_api_get_non_admin(self):
        """Test the Get Profile API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        json_resp =  response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_resp["email"], self.nonAdminUN)

    def test_api_get_anon(self):
        """Test the Get Profile API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Get Profile API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Get Profile API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_anon(self):
        """Test the Get Profile API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

class MarinaEntryRateViewSetTestCase(TestSetup):
    url = '/api/parkentryrate/'
    start = datetime.now().date()
    end = datetime.now().date()
    data = {
        'period_start' : "{}-{}-{}".format(start.year, start.month, start.day),
        'period_end' : "{}-{}-{}".format(end.year, end.month, end.day),
        'details' : "Some details text",
        'vehicle' : 1.00,
        'motorobike' : 1.00,
        'concession' : 1.00
    }

    def test_api_get_admin(self):
        """ Test the Marina Entry Rate API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Marina Entry Rate API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Marina Entry Rate API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Marina Entry Rate API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        self.data['reason'] = self.prReason.id
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_api_post_non_admin(self):
        """Test the Marina Entry Rate API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        self.data['reason'] = self.prReason.id
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Marina Entry Rate API endpoint POST response when not logged in.
        """
        self.data['reason'] = self.prReason.id
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

class MarinaViewSetTestCase(TestSetup):
    url = '/api/parks/'
    url2 = '/api/parks/price_history/'
    url3 = '/api/parks/add_price/'
    start = datetime.now().date()
    end = datetime.now().date()
    data = {
        'period_start' : "{}-{}-{}".format(start.year, start.month, start.day),
        'period_end' : "{}-{}-{}".format(end.year, end.month, end.day),
        'details' : "Some details text",
        'vehicle' : 1.00,
        'motorobike' : 1.00,
        'concession' : 1.00
    }

    def test_api_get_admin(self):
        """ Test the Marina View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Marina View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Marina View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_admin_2(self):
        """ Test the Marina View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin_2(self):
        """Test the Marina View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon_2(self):
        """Test the Marina View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Marina View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        self.data['reason'] = self.prReason.id
        response = self.client.post(self.url3, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_api_post_non_admin(self):
        """Test the Marina View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        self.data['reason'] = self.prReason.id
        response = self.client.post(self.url3, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Marina View API endpoint POST response when not logged in.
        """
        self.data['reason'] = self.prReason.id
        response = self.client.post(self.url3, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

class MarineParkMapsViewSetTestCase(TestSetup):
    url = '/api/marine_parks_map/'

    def test_api_get_admin(self):
        """ Test the Marine Parks Maps API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Marine Parks Maps API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_anon(self):
        """Test the Marine Parks Maps API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_post_admin(self):
        """Test the Marine Parks Maps API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Marine Parks Maps API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_anon(self):
        """Test the Marine Parks Maps API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

class MarineParksRegionMapViewSetTestCase(TestSetup):
    url = '/api/region_marine_parks_map/'

    def test_api_get_admin(self):
        """ Test the Marine Parks Region Maps API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Marine Parks Region Maps API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_anon(self):
        """Test the Marine Parks Region Maps API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_post_admin(self):
        """Test the Marine Parks Region Maps API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Marine Parks Region Maps API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_anon(self):
        """Test the Marine Parks Region Maps API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

class MaximumStayViewSetTestCase(TestSetup):
    url = '/api/maxStayReasons/'

    def test_api_get_admin(self):
        """ Test the Maximum Stay View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Maximum Stay View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Maximum Stay View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Maximum Stay View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Maximum Stay View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Maximum Stay View API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)


class MooringAreaBookingRangeViewSetTestCase(TestSetup):
    url = '/api/mooring_booking_ranges/'
    start = datetime.now()
    end = datetime.now()+timedelta(days=3)
    data = {
        'status' : 0,
        'range_start' : "{}-{}-{}".format(start.year, start.month, start.day),
        'range_end': "{}-{}-{}".format(end.year, end.month, end.day),
        'details' : "Some details",
    }

    def test_api_get_admin(self):
        """ Test the Mooring Area Booking Range View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooring Area Booking Range View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Mooring Area Booking Range View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    # Not currently passing, does not satisfy the serializer for some reason.
    # def test_api_post_admin(self):
    #     """Test the Mooring Area Booking Range View API endpoint POST response when logged in as admin user.
    #     """
    #     self.client.login(email=adminUN, password='pass')
    #     mabr = MooringAreaBookingRange.objects.all()[0]
    #     id = mabr.id
    #     url = self.url + str(id) + "/"
    #     self.data['id'] = id
    #     self.data['open_reason'] = self.opReason.id
    #     self.data['campground'] = self.area.id
    #     response = self.client.put(url, json.dumps(self.data), partial=True, content_type='application/json')
    #     self.assertEqual(response.status_code, 200)

    def test_api_post_non_admin(self):
        """Test the Mooring Area Booking Range View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        mabr = MooringAreaBookingRange.objects.all()[0]
        id = mabr.id
        url = self.url + str(id) + "/"
        self.data['id'] = id
        self.data['open_reason'] = self.opReason.id
        self.data['campground'] = self.area.id
        response = self.client.put(self.url, json.dumps(self.data), partial=True, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Mooring Area Booking Range View API endpoint POST response when not logged in.
        """
        mabr = MooringAreaBookingRange.objects.all()[0]
        id = mabr.id
        url = self.url + str(id) + "/"
        self.data['id'] = id
        self.data['open_reason'] = self.opReason.id
        self.data['campground'] = self.area.id
        response = self.client.put(self.url, json.dumps(self.data), partial=True, content_type='application/json')
        self.assertEqual(response.status_code, 403)

class MooringAreaMapFilterViewSetTestCase(TestSetup):
    url = '/api/mooring_map_filter/'

    def test_api_get_admin(self):
        """ Test the Mooring Area Map Filter View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooring Area Map Filter View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_anon(self):
        """Test the Mooring Area Map Filter View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_post_admin(self):
        """Test the Mooring Area Map Filter View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Mooring Area Map Filter View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_anon(self):
        """Test the Mooring Area Map Filter View API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

class MooringAreaMapViewSetTestCase(TestSetup):
    url = '/api/mooring_map/'

    def test_api_get_admin(self):
        """ Test the Mooring Area Map View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooring Area Map View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_anon(self):
        """Test the Mooring Area Map View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_post_admin(self):
        """Test the Mooring Area Map View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Mooring Area Map View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_anon(self):
        """Test the Mooring Area Map View API endpoint POST response when not logged in.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

class MooringAreaStayHistoryViewSetTestCase(TestSetup):
    url = '/api/mooring_stay_history/'
    start = datetime.now()
    end = datetime.now() + timedelta(days=3)
    data = {
        'range_start': "{}-{}-{}".format(start.year, start.month, start.day),
        'range_end': "{}-{}-{}".format(end.year, end.month, end.day),
        'min_days': 1,
        'max_days': 12,
        'min_dba': 1,
        'max_dba': 12,
        'details': "Some details here.",
    }

    def test_api_get_admin(self):
        """ Test the Mooring Area Stay History View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooring Area Stay History View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Mooring Area Stay History View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    # def test_api_post_admin(self):
    #     """Test the Mooring Area Stay History View API endpoint POST response when logged in as admin user.
    #     """
    #     self.data['reason'] = self.maxStayReason.id
    #     self.data['mooringarea'] = self.area.id
    #     self.client.login(email=adminUN, password='pass')
    #     response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
    #     self.assertEqual(response.status_code, 201)

    def test_api_post_non_admin(self):
        """Test the Mooring Area Stay History View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.put(self.url, json.dumps(self.data), partial=True, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Mooring Area Stay History View API endpoint POST response when not logged in.
        """
        response = self.client.put(self.url, json.dumps(self.data), partial=True, content_type='application/json')
        self.assertEqual(response.status_code, 403)

class MooringAreaViewSetTestCase(TestSetup):
    url = '/api/mooring-areas/'
    data = {}
    def test_api_get_admin(self):
        """ Test the Mooring Area View API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooring Area View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Mooring Area View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Mooring Area View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url, {'park': self.park.id, 'address' : {} , 'name': 'Mooring 2'})
        self.assertEqual(response.status_code, 200)

    def test_api_post_non_admin(self):
        """Test the Mooring Area View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Mooring Area View API endpoint POST response when logged in as external user.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

class MooringGroupTestCase(TestSetup):
    url = '/api/mooring_groups/'
    data = {
        'name': "name text"
    }

    def test_api_get_admin(self):
        """ Test the Mooring Group API endpoint GET response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooring Group API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Mooring Group API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

#    def test_api_post_admin(self):
#        """Test the Mooring Group API endpoint POST response when logged in as admin user.
#        """
#        self.client.login(email=self.adminUN, password='pass')
#        self.data['members'] = [self.adminUser.id]
#        self.data['moorings'] = [self.area.id]
#        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
#        self.assertEqual(response.status_code, 201)

    def test_api_post_non_admin(self):
        """Test the Mooring Group API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        self.data['members'] = [self.adminUser.id]
        self.data['moorings'] = [self.area.id]
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Mooring Group API endpoint POST response when logged in as external user.
        """
        self.data['members'] = [self.adminUser.id]
        self.data['moorings'] = [self.area.id]
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

class MooringsiteBookingRangeViewSetTestCase(TestSetup):
    url = '/api/mooringsite_booking_ranges/'
    start = datetime.now()
    end = datetime.now() + timedelta(days=3)
    data = {
        'status' : 0,
        'range_start': "{}/{}/{}".format(start.day, start.month, start.year),
        'range_end': "{}/{}/{}".format(end.day, end.month, end.year),
        'details' : "Some details",
    }

    def test_api_get_admin(self):
        """ Test the Mooring Area Booking Range API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooring Area Booking Range API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Mooring Area Booking Range API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Mooring Area Booking Range API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        self.data['open_reason'] = self.opReason.id
        self.data['campsite'] = self.area.id
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Mooring Area Booking Range API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        self.data['open_reason'] = self.opReason.id
        self.data['campsite'] = self.area.id
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Mooring Area Booking Range API endpoint POST response when logged in as external user.
        """
        self.data['open_reason'] = self.opReason.id
        self.data['campsite'] = self.area.id
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

class MooringsiteBookingViewSetTestCase(TestSetup):
    url = '/api/mooringsite_bookings/'
    start = datetime.now()
    data = {
        'date': "{}-{}-{}".format(start.year, start.month, start.day)
    }

    def test_api_get_admin(self):
        """ Test the Mooringsite Booking View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooringsite Booking View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Mooringsite Booking View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Mooringsite Booking View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        self.data['campsite'] = self.site.id
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Mooringsite Booking View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        self.data['campsite'] = self.site.id
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_api_post_anon(self):
        """Test the Mooringsite Booking View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        self.data['campsite'] = self.site.id
        response = self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

class MooringsiteClassViewSetTestCase(TestSetup):
    url = '/api/mooringsite_classes/'

    def test_api_get_admin(self):
        """ Test the Mooringsite Class View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooringsite Class View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Mooringsite Class View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Mooringsite Class View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Mooringsite Class View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Mooringsite Class View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)


# This is commented out on URLs. Assuming this API endpoint is no longer used.
# class MooringsiteRateViewSetTestCase(TestSetup):
#     url = ''

#     def test_api_get_admin(self):
#         """ Test the Mooringsite Rate View API endpoint GET response when logged in as admin.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)

#     def test_api_get_non_admin(self):
#         """Test the Mooringsite Rate View API endpoint GET response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_get_anon(self):
#         """Test the Mooringsite Rate View API endpoint GET response when not logged in.
#         """
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_admin(self):
#         """Test the Mooringsite Rate View API endpoint POST response when logged in as admin user.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 400)

#     def test_api_post_non_admin(self):
#         """Test the Mooringsite Rate View API endpoint POST response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_non_admin(self):
#         """Test the Mooringsite Rate View API endpoint POST response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

class MooringsiteStayHistoryViewSetTestCase(TestSetup):
    url = '/api/mooringsites_stay_history/'

    def test_api_get_admin(self):
        """ Test the Mooringsite Stay History View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooringsite Stay History View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Mooringsite Stay History View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Mooringsite Stay History View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Mooringsite Stay History View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_non_admin(self):
        """Test the Mooringsite Stay History View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)


class MooringsiteViewSetTestCase(TestSetup):
    url = '/api/mooringsites/'
    data = {}
    def test_api_get_admin(self):
        """ Test the Mooringsite View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Mooringsite View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Mooringsite View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

#    def test_api_post_admin(self):
#        """Test the Mooringsite View API endpoint POST response when logged in as admin user.
#        """
#        self.client.login(email=self.adminUN, password='pass')
#        response = self.client.post(self.url, {'mooringarea': self.area.id,'number': 1, 'campground' : self.area })
#        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Mooringsite View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_non_admin(self):
        """Test the Mooringsite View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

class OpenReasonViewSetTestCase(TestSetup):
    url = '/api/openReasons/'

    def test_api_get_admin(self):
        """ Test the Open Reason View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Open Reason View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Open Reason View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Open Reason View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Open Reason View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_non_admin(self):
        """Test the Open Reason View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)


class OracleJobTestCase(TestSetup):
    url = '/api/oracle_job'

#    def test_api_get_admin(self):
#        """ Test the Oracle Job View API endpoint GET response when logged in as admin.
#        """
#        start = datetime.now()
#        self.data = {
#           'date': "{}-{}-{}".format(start.year, start.month, start.day)
#        }
#
#        print "==__ OracleJobTestCase test_api_get_admin START"
#        self.client.login(email=self.adminUN, password='pass')
#        response = self.client.get(self.url, {'date': "{}/{}/{}".format(datetime.now().day, datetime.now().month, datetime.now().year), 'override' : False})
#        self.assertEqual(response.status_code, 400)
#        print "==__ OracleJobTestCase test_api_get_admin END"


    def test_api_get_non_admin(self):
        """Test the Oracle Job View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url, {'date': "{}/{}/{}".format(datetime.now().day, datetime.now().month, datetime.now().year), 'override' : False})
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Oracle Job View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url, {'date': "{}/{}/{}".format(datetime.now().day, datetime.now().month, datetime.now().year), 'override' : False})
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Oracle Job View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Oracle Job View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Oracle Job View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

class PriceReasonViewSetTestCase(TestSetup):
    url = '/api/priceReasons/'

    def test_api_get_admin(self):
        """ Test the Price Reason View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Price Reason View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Price Reason View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Price Reason View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Price Reason View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_api_post_non_admin(self):
        """Test the Price Reason View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)


class PromoAreaViewSetTestCase(TestSetup):
    url = '/api/promo_areas/'

    def test_api_get_admin(self):
        """ Test the Promo Area View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Promo Area View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Promo Area View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Promo Area View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Promo Area View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Promo Area View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)


class RateViewSetTestCase(TestSetup):
    url = '/api/rates/'

    def test_api_get_admin(self):
        """ Test the Rate View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Rate View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Rate View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Rate View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 201)

    def test_api_post_non_admin(self):
        """Test the Rate View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_non_admin(self):
        """Test the Rate View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

class RegionViewSetTestCase(TestSetup):
    url = '/api/regions/'

    def test_api_get_admin(self):
        """ Test the Region View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_api_get_non_admin(self):
        """Test the Region View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """Test the Region View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """Test the Region View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Region View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_non_admin(self):
        """Test the Region View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

class RegisteredVesselsViewSetTestCase(TestSetup):
    url = '/api/registeredVessels/'

    def test_api_get_admin(self):
        """ Test the Registered Vessels View API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_get_non_admin(self):
        """Test the Registered Vessels View API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_get_anon(self):
        """Test the Registered Vessels View API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_admin(self):
        """Test the Registered Vessels View API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """Test the Registered Vessels View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_non_admin(self):
        """Test the Registered Vessels View API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

# class UpdateProfileAddressTestCase(TestSetup):
#     url = 'api/profile/update_address'

#     def test_api_get_admin(self):
#         """ Test the Update Profile Address API endpoint GET response when logged in as admin.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 405)

#     def test_api_get_non_admin(self):
#         """Test the Update Profile Address API endpoint GET response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_get_anon(self):
#         """Test the Update Profile Address API endpoint GET response when not logged in.
#         """
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_admin(self):
#         """Test the Update Profile Address API endpoint POST response when logged in as admin user.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 400)

#     def test_api_post_non_admin(self):
#         """Test the Update Profile Address API endpoint POST response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_non_admin(self):
#         """Test the Update Profile Address API endpoint POST response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

# class UpdateProfileContactTestCase(TestSetup):
#     url = 'api/profile/update_contact'

#     def test_api_get_admin(self):
#         """ Test the Update Profile Contact API endpoint GET response when logged in as admin.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 405)

#     def test_api_get_non_admin(self):
#         """Test the Update Profile Contact API endpoint GET response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_get_anon(self):
#         """Test the Update Profile Contact API endpoint GET response when not logged in.
#         """
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_admin(self):
#         """Test the Update Profile Contact API endpoint POST response when logged in as admin user.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 400)

#     def test_api_post_non_admin(self):
#         """Test the Update Profile Contact API endpoint POST response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_non_admin(self):
#         """Test the Update Profile Contact API endpoint POST response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

# class UpdateProfilePersonalTestCase(TestSetup):
#     url = 'api/profile/update_personal'

#     def test_api_get_admin(self):
#         """ Test the Update Profile Personal API endpoint GET response when logged in as admin.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 405)

#     def test_api_get_non_admin(self):
#         """Test the Update Profile Personal API endpoint GET response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_get_anon(self):
#         """Test the Update Profile Personal API endpoint GET response when not logged in.
#         """
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_admin(self):
#         """Test the Update Profile Personal API endpoint POST response when logged in as admin user.
#         """
#         self.client.login(email=adminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 400)

#     def test_api_post_non_admin(self):
#         """Test the Update Profile Personal API endpoint POST response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_api_post_non_admin(self):
#         """Test the Update Profile Personal API endpoint POST response when logged in as external user.
#         """
#         self.client.login(email=self.nonAdminUN, password='pass')
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, 403)

class UsersViewSetTestCase(TestSetup):
    url = '/api/users/'

    def test_api_get_admin(self):
        """ Test the API endpoint GET response when logged in as admin.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Requires more permission to get 200 success code

    def test_api_get_non_admin(self):
        """User API endpoint GET response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_get_anon(self):
        """User API endpoint GET response when not logged in.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_admin(self):
        """User API endpoint POST response when logged in as admin user.
        """
        self.client.login(email=self.adminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_api_post_non_admin(self):
        """User API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_api_post_non_admin(self):
        """User API endpoint POST response when logged in as external user.
        """
        self.client.login(email=self.nonAdminUN, password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
