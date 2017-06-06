import os

from django.core.urlresolvers import reverse
from django.test import TestCase

from wildlifelicensing.apps.main.tests.helpers import SocialClient, get_or_create_default_customer, \
    get_or_create_default_officer, create_licence, create_random_customer, get_or_create_default_assessor
from wildlifelicensing.apps.applications.tests.helpers import create_and_lodge_application
from ledger.payments import pdf


class ViewApplicationTestCase(TestCase):
    fixtures = ['licences.json', 'countries.json', 'catalogue.json', 'partner.json']

    def setUp(self):
        self.customer = get_or_create_default_customer(include_default_profile=True)
        self.officer = get_or_create_default_officer()
        self.assessor = get_or_create_default_assessor()
        self.not_allowed_customer = create_random_customer()
        self.assertNotEqual(self.not_allowed_customer, self.customer)

        self.client = SocialClient()
        self.application = create_and_lodge_application(self.customer)

    def tearDown(self):
        self.client.logout()

    def test_view_application_pdf(self):
        """
        Testing that when a user requests the application as a pdf they are returned a response containing a pdf
        """
        self.client.login(self.officer.email)

        response = self.client.get(reverse('wl_applications:view_application_pdf', args=(self.application.pk,)))

        self.assertEquals(response['content-type'], 'application/pdf')


    def test_view_application_pdf_permissions(self):
        """
        Testing that only officers, assessors and customer that owns the application can view the application pdf
        """
        url = reverse('wl_applications:view_application_pdf', args=(self.application.pk,))
        allowed = [self.officer, self.assessor, self.customer]
        forbidden = [self.not_allowed_customer]

        for user in allowed:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
            self.client.logout()

        for user in forbidden:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(403, response.status_code)
            self.client.logout()
