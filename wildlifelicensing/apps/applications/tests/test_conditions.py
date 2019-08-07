from datetime import date

from django.test import TestCase
from django.shortcuts import reverse
from django_dynamic_fixture import G

from wildlifelicensing.apps.main.tests.helpers import get_or_create_default_customer, is_login_page, \
    get_or_create_default_assessor, add_assessor_to_assessor_group, SocialClient, get_or_create_default_officer, \
    add_to_group, clear_mailbox, get_emails
from wildlifelicensing.apps.applications.tests import helpers as app_helpers
from wildlifelicensing.apps.applications.models import AssessmentCondition, Condition, Assessment
from wildlifelicensing.apps.main.helpers import is_assessor, get_user_assessor_groups
from wildlifelicensing.apps.main.models import AssessorGroup
from ledger.accounts.models import EmailUser


class TestViewAccess(TestCase):
    fixtures = ['licences.json', 'conditions.json', 'returns.json']

    def setUp(self):
        self.client = SocialClient()
        self.user = get_or_create_default_customer()
        self.officer = get_or_create_default_officer()
        self.application = app_helpers.create_and_lodge_application(self.user, **{
            'data': {
                'title': 'My Application'
            }
        })
        self.assessment = app_helpers.get_or_create_assessment(self.application)
        self.condition = Condition.objects.first()
        self.assessment_condition = AssessmentCondition.objects.create(assessment=self.assessment,
                                                                       condition=self.condition,
                                                                       order=1)

        self.urls_get = [
            reverse('wl_applications:enter_conditions', args=[self.application.pk]),
            reverse('wl_applications:search_conditions')
        ]

        self.urls_post = [
            {
                'url': reverse('wl_applications:create_condition', args=[self.application.pk]),
                'data': {
                    'code': '123488374',
                    'text': 'condition text'
                }
            },
            {
                'url': reverse('wl_applications:set_assessment_condition_state'),
                'data': {
                    'assessmentConditionID': self.assessment_condition.pk,
                    'acceptanceStatus': 'accepted',
                }
            },
            {
                'url': reverse('wl_applications:enter_conditions', args=[self.application.pk]),
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
                self.assertRedirects(response, reverse('wl_dashboard:tables_customer'), status_code=302,
                                     target_status_code=200)
        for url in self.urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('wl_dashboard:tables_customer'), status_code=302,
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
            reverse('wl_applications:enter_conditions', args=[self.application.pk]),
            reverse('wl_applications:enter_conditions_assessor', args=[self.application.pk, self.assessment.pk]),
        ]
        urls_post_forbidden = [
            {
                'url': reverse('wl_applications:create_condition', args=[self.application.pk]),
                'data': {
                    'code': '123488374',
                    'text': 'condition text'
                }
            },
            {
                'url': reverse('wl_applications:set_assessment_condition_state'),
                'data': {
                    'assessmentConditionID': self.assessment_condition.pk,
                    'acceptanceStatus': 'accepted',
                }
            },
            {
                'url': reverse('wl_applications:enter_conditions', args=[self.application.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
                }
            },
            {
                'url': reverse('wl_applications:enter_conditions_assessor',
                               args=[self.application.pk, self.assessment.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
                }
            },
        ]
        # Allowed
        urls_get_allowed = [
            reverse('wl_applications:search_conditions')
        ]
        urls_post_allowed = [
        ]
        for url in urls_get_forbidden:
            response = self.client.get(url, follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('wl_dashboard:tables_assessor'), status_code=302,
                                     target_status_code=200)
        for url in urls_post_forbidden:
            response = self.client.post(url['url'], url['data'], follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('wl_dashboard:tables_assessor'), status_code=302,
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
            reverse('wl_applications:enter_conditions', args=[self.application.pk]),
        ]
        urls_post_forbidden = [
            {
                'url': reverse('wl_applications:create_condition', args=[self.application.pk]),
                'data': {
                    'code': '123488374',
                    'text': 'condition text'
                }
            },
            {
                'url': reverse('wl_applications:set_assessment_condition_state'),
                'data': {
                    'assessmentConditionID': self.assessment_condition.pk,
                    'acceptanceStatus': 'accepted',
                }
            },
            {
                'url': reverse('wl_applications:enter_conditions', args=[self.application.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
                }
            },
        ]
        # Allowed
        urls_get_allowed = [
            reverse('wl_applications:search_conditions'),
            reverse('wl_applications:enter_conditions_assessor', args=[self.application.pk, self.assessment.pk]),
        ]
        urls_post_allowed = [
            {
                'url': reverse('wl_applications:enter_conditions_assessor',
                               args=[self.application.pk, self.assessment.pk]),
                'data': {
                    'conditionID': [self.condition.pk],
                }
            },
        ]
        for url in urls_get_forbidden:
            response = self.client.get(url, follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('wl_dashboard:tables_assessor'), status_code=302,
                                     target_status_code=200)
        for url in urls_post_forbidden:
            response = self.client.post(url['url'], url['data'], follow=True)
            if response.status_code != 403:
                self.assertRedirects(response, reverse('wl_dashboard:tables_assessor'), status_code=302,
                                     target_status_code=200)
        for url in urls_get_allowed:
            response = self.client.get(url, follow=True)
            self.assertEqual(200, response.status_code)

        for url in urls_post_allowed:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertEqual(200, response.status_code)


class TestAssignAssessor(TestCase):
    fixtures = ['licences.json', 'conditions.json']

    def setUp(self):
        self.client = SocialClient()
        self.user = get_or_create_default_customer()
        self.officer = get_or_create_default_officer()
        self.application = app_helpers.create_and_lodge_application(self.user, **{
            'data': {
                'title': 'My Application'
            }
        })

        self.assessor_group = G(AssessorGroup, name='District7', email='district7@test.com')
        self.assessor_1 = G(EmailUser, email='assessor1@test.com', dob='1967-04-04')
        add_to_group(self.assessor_1, 'Assessors')
        add_to_group(self.assessor_1, self.assessor_group)

        self.assessor_2 = G(EmailUser, email='assesor2@test.com', dob='1968-04-04')
        add_to_group(self.assessor_2, 'Assessors')
        add_to_group(self.assessor_2, self.assessor_group)

    def _issue_assessment(self, application, assessor_group):
        self.client.login(self.officer.email)

        url = reverse('wl_applications:send_for_assessment')
        payload = {
            'applicationID': application.pk,
            'assGroupID': assessor_group.pk
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        self.client.logout()
        clear_mailbox()
        data = resp.json()
        return Assessment.objects.filter(pk=data['assessment']['id']).first()

    def test_email_sent_to_assessor_group(self):
        """
        Test that when an officer issue an assessment an email is sent to the group email
        """
        # officer issue assessment
        self.client.login(self.officer.email)

        url = reverse('wl_applications:send_for_assessment')
        payload = {
            'applicationID': self.application.pk,
            'assGroupID': self.assessor_group.pk
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        # we should have one email sent to the assessor
        emails = get_emails()
        self.assertEqual(len(emails), 1)
        email = emails[0]
        recipients = email.to
        self.assertEqual(len(recipients), 1)
        expected_recipient = self.assessor_group.email
        self.assertEqual(recipients[0], expected_recipient)

        # the response is a json response. It should contain the assessment id
        expected_content_type = 'application/json'
        self.assertEqual(resp['content-type'], expected_content_type)
        data = resp.json()
        self.assertTrue('assessment' in data)
        self.assertTrue('id' in data['assessment'])
        assessment = Assessment.objects.filter(pk=data['assessment']['id']).first()
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment.application, self.application)
        expected_status = 'awaiting_assessment'
        self.assertEqual(assessment.status, expected_status)
        # check more data
        self.assertEqual(assessment.assessor_group, self.assessor_group)
        self.assertEqual(assessment.officer, self.officer)

        self.assertEqual(assessment.date_last_reminded, date.today())
        self.assertEqual(assessment.conditions.count(), 0)
        self.assertEqual(assessment.comment, '')
        self.assertEqual(assessment.purpose, '')

    def test_assign_assessment_send_email(self):
        """
        Use case: assessor_1 assign the assessment to assessor_2.
         Test that assessor_2 should receive an email with a link.
         The email should be also log in the communication log
        """
        assessment = self._issue_assessment(self.application, self.assessor_group)
        previous_comm_log = app_helpers.get_communication_log(assessment.application)
        previous_action_list = app_helpers.get_action_log(assessment.application)

        url = reverse('wl_applications:assign_assessor')
        self.client.login(self.assessor_1.email)
        payload = {
            'assessmentID': assessment.id,
            'userID': self.assessor_2.id
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        # the response is a json response. It should contain the assessment id
        expected_content_type = 'application/json'
        self.assertEqual(resp['content-type'], expected_content_type)

        # we should have one email sent to the assessor
        emails = get_emails()
        self.assertEqual(len(emails), 1)
        email = emails[0]
        recipients = email.to
        self.assertEqual(len(recipients), 1)
        expected_recipient = self.assessor_2.email
        self.assertEqual(recipients[0], expected_recipient)
        # the subject should contains 'assessment assigned'
        self.assertTrue(email.subject.find('assessment assigned') > -1)
        # the body should get a url to assess the application
        expected_url = reverse('wl_applications:enter_conditions_assessor',
                               args=[assessment.application.pk, assessment.pk])
        self.assertTrue(email.body.find(expected_url) > -1)

        # test that the email has been logged.
        new_comm_log = app_helpers.get_communication_log(assessment.application)
        self.assertEqual(len(new_comm_log), len(previous_comm_log) + 1)
        previous_recipients = [entry['to'] for entry in previous_comm_log]
        self.assertNotIn(self.assessor_2.email, previous_recipients)
        new_recipients = [entry['to'] for entry in new_comm_log]
        self.assertIn(self.assessor_2.email, new_recipients)

        # it should also be recorded in the action list
        new_action_list = app_helpers.get_action_log(assessment.application)
        self.assertEqual(len(new_action_list), len(previous_action_list) + 1)

    def test_assign_to_me_no_email(self):
        """
        Use case: assessor_1 assign the assessment to himself.
         test that no email is sent
        """
        assessment = self._issue_assessment(self.application, self.assessor_group)
        previous_comm_log = app_helpers.get_communication_log(assessment.application)
        previous_action_list = app_helpers.get_action_log(assessment.application)

        url = reverse('wl_applications:assign_assessor')
        self.client.login(self.assessor_1.email)
        payload = {
            'assessmentID': assessment.id,
            'userID': self.assessor_1.id
        }
        resp = self.client.post(url, data=payload)
        # the response is a json response. It should contain the assessment id
        expected_content_type = 'application/json'
        self.assertEqual(resp['content-type'], expected_content_type)

        # we should have one email sent to the assessor
        emails = get_emails()
        self.assertEqual(len(emails), 0)

        # com log should be unchanged.
        new_comm_log = app_helpers.get_communication_log(assessment.application)
        self.assertEqual(new_comm_log, previous_comm_log)

        # but should be recorded in the action list
        new_action_list = app_helpers.get_action_log(assessment.application)
        self.assertEqual(len(new_action_list), len(previous_action_list) + 1)
