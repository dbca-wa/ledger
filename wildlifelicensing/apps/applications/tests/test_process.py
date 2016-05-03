from django.test import TestCase
from django.core.urlresolvers import reverse

from wildlifelicensing.apps.main.tests.helpers import SocialClient, get_or_create_default_customer, is_login_page, \
    get_or_create_default_officer, get_or_create_default_assessor_group
from wildlifelicensing.apps.applications.tests.helpers import create_and_lodge_application, get_or_create_assessment


class TestViewAccess(TestCase):
    def setUp(self):
        self.client = SocialClient()
        self.user = get_or_create_default_customer()
        self.officer = get_or_create_default_officer()
        self.application = create_and_lodge_application(self.user, **{
            'data': {
                'title': 'My Application'
            }
        })
        self.process_urls_get = [
            reverse('applications:process', args=[self.application.pk]),
        ]

        self.process_urls_post = [
            {
                'url': reverse('applications:process', args=[self.application.pk]),
                'data': {
                    'applicationID': self.application.pk,
                }
            },
            {
                'url': reverse('applications:assign_officer'),
                'data': {
                    'applicationID': self.application.pk,
                    'userID': self.officer.pk,
                }
            },
            {
                'url': reverse('applications:set_id_check_status'),
                'data': {
                    'applicationID': self.application.pk,
                    'status': 'accepted',
                }
            },
            {
                'url': reverse('applications:id_request'),
                'data': {
                    'applicationID': self.application.pk,
                }
            },
            {
                'url': reverse('applications:set_character_check_status'),
                'data': {
                    'applicationID': self.application.pk,
                    'status': 'accepted',
                }
            },
            {
                'url': reverse('applications:set_review_status'),
                'data': {
                    'applicationID': self.application.pk,
                    'status': 'accepted',
                }
            },
            {
                'url': reverse('applications:amendment_request'),
                'data': {
                    'applicationID': self.application.pk,
                }
            },
            {
                'url': reverse('applications:send_for_assessment'),
                'data': {
                    'applicationID': self.application.pk,
                    'assGroupID': get_or_create_default_assessor_group().pk,
                    'status': 'awaiting_assessment'
                }
            },
            {
                'url': reverse('applications:remind_assessment'),
                'data': {
                    'applicationID': self.application.pk,
                    'assessmentID': get_or_create_assessment(self.application).pk
                }
            },
        ]

    def tearDown(self):
        self.client.logout()

    def test_customer_access(self):
        """
         A Customer cannot access any URL
        """
        # not logged-in
        for url in self.process_urls_get:
            response = self.client.get(url, follow=True)
            self.assertTrue(is_login_page(response))

        for url in self.process_urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertTrue(is_login_page(response))

        # logged-in. Should redirect to dashboard
        self.client.login(self.user.email)
        for url in self.process_urls_get:
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('dashboard:tables_customer'), status_code=302,
                                 target_status_code=200)
        for url in self.process_urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertRedirects(response, reverse('dashboard:tables_customer'), status_code=302,
                                 target_status_code=200)

    def test_officer_access(self):
        self.client.login(self.officer.email)
        for url in self.process_urls_get:
            response = self.client.get(url, follow=False)
            self.assertEqual(200, response.status_code)
        for url in self.process_urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertEquals(200, response.status_code)
