from django.test import TestCase

from wildlifelicensing.apps.main.tests.helpers import *
from wildlifelicensing.apps.applications.tests.helpers import *
from wildlifelicensing.apps.main.helpers import is_assessor, get_user_assessor_groups


class TestViewAccess(TestCase):
    fixtures = ['conditions.json']

    def setUp(self):
        self.client = SocialClient()
        self.user = get_or_create_default_customer()
        self.officer = get_or_create_default_officer()
        self.application = create_and_lodge_application(self.user, **{
            'data': {
                'title': 'My Application'
            }
        })
        self.assessment = get_or_create_assessment(self.application)
        self.condition = Condition.objects.first()
        self.assessment_condition = AssessmentCondition.objects.create(assessment=self.assessment,
                                                                       condition=self.condition,
                                                                       order=1)
        self.urls_get = [
            reverse('applications:enter_conditions', args=[self.application.pk]),
            reverse('applications:enter_conditions_assessor', args=[self.application.pk, self.assessment.pk]),
            reverse('applications:search_conditions')
        ]

        self.urls_post = [
            {
                'url': reverse('applications:create_condition'),
                'data': {
                    'code': '123488374',
                    'text': 'condition text'
                }
            },
            {
                'url': reverse('applications:set_assessment_condition_state'),
                'data': {
                    'assessmentConditionID': self.assessment_condition.pk,
                    'acceptanceStatus': 'accepted',
                }
            },
            {
                'url': reverse('applications:submit_conditions', args=[self.application.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
                }
            },
            {
                'url': reverse('applications:submit_conditions_assessor',
                               args=[self.application.pk, self.assessment.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
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
        for url in self.urls_get:
            response = self.client.get(url, follow=True)
            self.assertTrue(is_login_page(response))

        for url in self.urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertTrue(is_login_page(response))

        # logged-in. Should throw a 403 or redirect to login
        self.client.login(self.user.email)
        for url in self.urls_get:
            response = self.client.get(url, follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('dashboard:tables_customer'), status_code=302,
                                     target_status_code=200)
        for url in self.urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('dashboard:tables_customer'), status_code=302,
                                     target_status_code=200)

    def test_officer_access(self):
        """
        Officer should be able to access any views
        """
        self.client.login(self.officer.email)
        for url in self.urls_get:
            response = self.client.get(url, follow=False)
            self.assertEqual(200, response.status_code)
        for url in self.urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertEquals(200, response.status_code)

    def test_assessor_access_limited(self):
        """
        Test that an assessor cannot edit an assessment that doesn't belong to their group
        All accessor can search conditions
        """
        assessor = get_or_create_default_assessor()
        self.client.login(assessor.email)
        # This assessor doesn't belong to a group
        self.assertTrue(is_assessor(assessor))
        self.assertFalse(get_user_assessor_groups(assessor))

        # forbidden
        urls_get_forbidden = [
            reverse('applications:enter_conditions', args=[self.application.pk]),
            reverse('applications:enter_conditions_assessor', args=[self.application.pk, self.assessment.pk]),
        ]
        urls_post_forbidden = [
            {
                'url': reverse('applications:create_condition'),
                'data': {
                    'code': '123488374',
                    'text': 'condition text'
                }
            },
            {
                'url': reverse('applications:set_assessment_condition_state'),
                'data': {
                    'assessmentConditionID': self.assessment_condition.pk,
                    'acceptanceStatus': 'accepted',
                }
            },
            {
                'url': reverse('applications:submit_conditions', args=[self.application.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
                }
            },
            {
                'url': reverse('applications:submit_conditions_assessor',
                               args=[self.application.pk, self.assessment.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
                }
            },
        ]
        # Allowed
        urls_get_allowed = [
            reverse('applications:search_conditions')
        ]
        urls_post_allowed = [
        ]
        for url in urls_get_forbidden:
            response = self.client.get(url, follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('dashboard:assessor'), status_code=302,
                                     target_status_code=200)
        for url in urls_post_forbidden:
            response = self.client.post(url['url'], url['data'], follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('dashboard:assessor'), status_code=302,
                                     target_status_code=200)
        for url in urls_get_allowed:
            response = self.client.get(url, follow=True)
            self.assertEqual(200, response.status_code)

        for url in urls_post_allowed:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertEqual(200, response.status_code)

    def test_assessor_access_normal(self):
        """
        Test that an assessor can edit an assessment that belongs to their group
        """
        assessor = get_or_create_default_assessor()
        self.client.login(assessor.email)
        # This assessor doesn't belong to a group
        self.assertTrue(is_assessor(assessor))
        # add the assessor to the assessment group
        self.assertTrue(Assessment.objects.filter(application=self.application).count() > 0)
        for assessment in Assessment.objects.filter(application=self.application):
            add_assessor_to_assessor_group(assessor, assessment.assessor_group)

        # forbidden
        urls_get_forbidden = [
            reverse('applications:enter_conditions', args=[self.application.pk]),
        ]
        urls_post_forbidden = [
            {
                'url': reverse('applications:create_condition'),
                'data': {
                    'code': '123488374',
                    'text': 'condition text'
                }
            },
            {
                'url': reverse('applications:set_assessment_condition_state'),
                'data': {
                    'assessmentConditionID': self.assessment_condition.pk,
                    'acceptanceStatus': 'accepted',
                }
            },
            {
                'url': reverse('applications:submit_conditions', args=[self.application.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
                }
            },
        ]
        # Allowed
        urls_get_allowed = [
            reverse('applications:search_conditions'),
            reverse('applications:enter_conditions_assessor', args=[self.application.pk, self.assessment.pk]),
        ]
        urls_post_allowed = [
            {
                'url': reverse('applications:submit_conditions_assessor',
                               args=[self.application.pk, self.assessment.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
                }
            },
        ]
        for url in urls_get_forbidden:
            response = self.client.get(url, follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('dashboard:assessor'), status_code=302,
                                     target_status_code=200)
        for url in urls_post_forbidden:
            response = self.client.post(url['url'], url['data'], follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('dashboard:assessor'), status_code=302,
                                     target_status_code=200)
        for url in urls_get_allowed:
            response = self.client.get(url, follow=True)
            self.assertEqual(200, response.status_code)

        for url in urls_post_allowed:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertEqual(200, response.status_code)
