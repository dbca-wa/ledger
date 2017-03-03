from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase

from django_dynamic_fixture import G

from wildlifelicensing.apps.applications.tests import helpers as app_helpers
from wildlifelicensing.apps.main.tests import helpers as main_helpers
from wildlifelicensing.apps.main.models import Region


class TestViewsAccess(TestCase):
    """
    Only officers can access any of the views in the entry modules
    """
    fixtures = ['licences.json']

    def setUp(self):
        self.client = main_helpers.SocialClient()
        self.user = main_helpers.get_or_create_default_customer()
        self.officer = main_helpers.get_or_create_default_officer()
        self.assessor = main_helpers.get_or_create_default_assessor()
        self.lodged_application = app_helpers.create_and_lodge_application(self.user, **{
            'data': {
                'title': 'Lodged Application'
            }
        })
        self.issued_application = app_helpers.create_and_lodge_application(self.user, **{
            'data': {
                'title': 'Issued Application'
            }
        })
        self.licence = app_helpers.issue_licence(self.issued_application, self.officer)
        self.assertIsNotNone(self.licence)
        self.issue_urls_get = [
            {
                'url': reverse('wl_applications:issue_licence', args=[self.lodged_application.pk]),
                'data': None
            },
            {
                'url': reverse('wl_applications:reissue_licence', args=[self.licence.pk]),
                'data': None
            },
            {
                'url': reverse('wl_applications:preview_licence', args=[self.issued_application.pk]),
                'data': app_helpers.get_minimum_data_for_issuing_licence()
            },
        ]

        self.issue_urls_post = [
            {
                'url': reverse('wl_applications:issue_licence', args=[self.lodged_application.pk]),
                'data': app_helpers.get_minimum_data_for_issuing_licence()
            },
        ]

    def tearDown(self):
        self.client.logout()

    def test_customer_access(self):
        """
         A Customer cannot access any URL
        """
        # not logged-in
        for url in self.issue_urls_get:
            response = self.client.get(url['url'], data=url['data'], follow=True)
            self.assertTrue(main_helpers.is_login_page(response))

        for url in self.issue_urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertTrue(main_helpers.is_login_page(response))

        # logged-in. Should redirect to dashboard
        self.client.login(self.user.email)
        for url in self.issue_urls_get:
            response = self.client.get(url['url'], data=url['data'], follow=True)
            self.assertRedirects(response, reverse('wl_dashboard:tables_customer'), status_code=302,
                                 target_status_code=200)
        for url in self.issue_urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertRedirects(response, reverse('wl_dashboard:tables_customer'), status_code=302,
                                 target_status_code=200)

    def test_assessor_access(self):
        """
         An assessor cannot access any URL
        """
        self.client.login(self.assessor.email)
        for url in self.issue_urls_get:
            response = self.client.get(url['url'], data=url['data'], follow=True)
            self.assertRedirects(response, reverse('wl_dashboard:tables_assessor'), status_code=302,
                                 target_status_code=200)
        for url in self.issue_urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertRedirects(response, reverse('wl_dashboard:tables_assessor'), status_code=302,
                                 target_status_code=200)

    def test_officer_access(self):
        """
        An officer should be able to go everywhere
        :return:
        """
        self.client.login(self.officer.email)
        for url in self.issue_urls_get:
            response = self.client.get(url['url'], data=url['data'], follow=True)
            self.assertEqual(200, response.status_code)
        for url in self.issue_urls_post:
            response = self.client.post(url['url'], data=url['data'], follow=True)
            self.assertEquals(200, response.status_code)

    def test_save_licence_details_from_issue_page(self):
        """
        Test that a licence can be saved in an unissued state from the issue page
        """
        # create application to issue
        application = app_helpers.create_and_lodge_application(self.user)

        self.client.login(self.officer.email)

        # save licence
        url = reverse('wl_applications:issue_licence', args=[application.pk])
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        data = {
            'submissionType': 'save',
            'regions': [G(Region).pk],
            'return_frequency': -1,
            'issue_date': str(today),
            'start_date': str(today),
            'end_date': str(tomorrow)
        }
        resp = self.client.post(url, data=data, follow=True)
        self.assertEquals(200, resp.status_code)
        application.refresh_from_db()
        self.assertNotEquals(application.processing_status, 'issued')
        self.assertIsNotNone(application.licence)
        self.assertFalse(application.licence.is_issued)


    def test_issue_licence(self):
        """
        Test that a licence can be issued
        """
        # create application to issue
        application = app_helpers.create_and_lodge_application(self.user)

        self.client.login(self.officer.email)

        # issue licence
        url = reverse('wl_applications:issue_licence', args=[application.pk])
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        data = {
            'regions': [G(Region).pk],
            'return_frequency': -1,
            'issue_date': str(today),
            'start_date': str(today),
            'end_date': str(tomorrow)
        }
        resp = self.client.post(url, data=data, follow=True)
        self.assertEquals(200, resp.status_code)
        application.refresh_from_db()
        self.assertEquals(application.processing_status, 'issued')
        self.assertIsNotNone(application.licence)
        self.assertTrue(application.licence.is_issued)
