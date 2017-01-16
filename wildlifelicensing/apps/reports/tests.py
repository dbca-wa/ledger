from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status

from wildlifelicensing.apps.main.helpers import is_assessor, is_customer, is_officer
from wildlifelicensing.apps.main.tests import helpers


class ReportsTestCase(TestCase):
    fixtures = ['licences.json']

    def setUp(self):
        self.customer = helpers.get_or_create_default_customer()
        self.assertTrue(is_customer(self.customer))
        self.officer = helpers.get_or_create_default_officer()
        self.assertTrue(is_officer(self.officer))
        self.assessor = helpers.get_or_create_default_assessor()
        self.assertTrue(is_assessor(self.assessor))
        self.client = helpers.SocialClient()

    def tearDown(self):
        self.client.logout()

    def test_page_authorisation(self):
        url = reverse('wl_reports:reports')
        forbidden = [self.customer, self.assessor]
        client = helpers.SocialClient()
        for user in forbidden:
            client = helpers.SocialClient()
            client.login(user.email)
            response = client.get(url, follow=True)
            self.assertRedirects(response, helpers.get_user_home_url(user),
                                 status_code=302, target_status_code=200, fetch_redirect_response=False)
            client.logout()

        allowed = [self.officer]
        for user in allowed:
            client.login(user.email)
            response = client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            client.logout()

    def test_report_menu(self):
        """Testing that a user can access the main report generation menu screen"""
        pass

    def test_applications_report(self):
        """Testing that a user can create an applications report"""
        pass

    def test_licences_report(self):
        """Testing that a user can create a licences report"""
        pass

    def test_returns_report(self):
        """Testing that a user can create an returns report"""
        pass
