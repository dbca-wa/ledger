import json
import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from wildlifelicensing.apps.applications.models import IDRequest, AmendmentRequest, ApplicationDeclinedDetails
from wildlifelicensing.apps.applications import utils
from wildlifelicensing.apps.main.tests.helpers import SocialClient, get_or_create_default_customer, is_login_page, \
    get_or_create_default_officer, get_or_create_default_assessor_group, is_email, get_email, clear_mailbox, \
    upload_id, clear_all_id_files, is_client_authenticated
from wildlifelicensing.apps.applications.tests.helpers import create_and_lodge_application, get_or_create_assessment, \
    get_or_create_condition
from wildlifelicensing.apps.applications.emails import ApplicationIDUpdateRequestedEmail,\
    ApplicationAmendmentRequestedEmail
from wildlifelicensing.apps.main.models import Region


class TestStatusLifeCycle(TestCase):
    fixtures = ['licences.json']

    def setUp(self):
        self.client = SocialClient()
        self.officer = get_or_create_default_officer()
        self.user = get_or_create_default_customer()
        self.assertNotEqual(self.officer, self.user)

    def tearDown(self):
        self.client.logout()
        clear_mailbox()
        clear_all_id_files()

    def test_id_update(self):
        """
        Test that when an ID update is required and the users update their ID the customer and id status are correctly
         updated
        """
        application = create_and_lodge_application(self.user)
        self.client.login(self.officer.email)
        self.assertTrue(is_client_authenticated(self.client))
        clear_mailbox()
        data = {
            'officer': self.officer.pk,
            'application': application.pk,
            'reason': IDRequest.REASON_CHOICES[0][0],
            'text': 'you to upload an ID.'
        }
        url = reverse('wl_applications:id_request')
        self.assertFalse(is_email())
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        resp_data = json.loads(response.content.decode('utf8'))
        self.assertIn('id_check_status', resp_data)
        self.assertIn('processing_status', resp_data)
        application.refresh_from_db()
        self.assertEqual('id_required', application.customer_status)
        self.assertEqual('awaiting_update', application.id_check_status)
        self.assertEqual('awaiting_applicant_response', application.processing_status)
        self.assertTrue(is_email())
        email = get_email()
        self.assertIn(application.applicant_profile.email, email.to)
        self.assertEqual(ApplicationIDUpdateRequestedEmail.subject, email.subject)

        # now user upload ID
        self.client.logout()
        self.assertIsNone(self.user.identification)
        self.client.login(self.user.email)
        self.assertTrue(is_client_authenticated(self.client))
        self.client.get(reverse('wl_main:identification'))
        upload_id(self.user)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.identification)
        application.refresh_from_db()
        self.assertEqual('updated', application.id_check_status)
        self.assertEqual('under_review', application.customer_status)
        self.assertEqual('ready_for_action', application.processing_status)

    def test_application_amendment(self):
        """
        Test that when an amendment is required, the user receives an email and can amend their application. When the
        user relodged, the officer can see the amendment and set the review status accordingly.
        """
        application = create_and_lodge_application(self.user)
        self.assertFalse(application.can_user_edit)

        self.client.login(self.officer.email)

        post_data = {
            'officer': self.officer.pk,
            'application': application.pk,
            'reason': AmendmentRequest.REASON_CHOICES[0][0],
            'text': 'Application needs more data'
        }

        response = self.client.post(reverse('wl_applications:amendment_request'), post_data)

        self.assertEqual(200, response.status_code)

        resp_data = json.loads(response.content.decode('utf8'))

        application.refresh_from_db()

        self.assertIn('review_status', resp_data)
        self.assertEquals(resp_data['review_status'], utils.REVIEW_STATUSES[application.review_status])
        self.assertIn('processing_status', resp_data)
        self.assertEquals(resp_data['processing_status'], utils.PROCESSING_STATUSES[application.processing_status])

        self.assertEqual(application.customer_status, 'amendment_required')
        self.assertEqual(application.processing_status, 'awaiting_applicant_response')
        self.assertEqual(application.review_status, 'awaiting_amendments')

        amendment_request = AmendmentRequest.objects.filter(application=application).first()

        self.assertIsNotNone(amendment_request)

        self.assertEquals(amendment_request.status, 'requested')

        self.assertTrue(is_email())
        email = get_email()
        self.assertIn(application.applicant_profile.email, email.to)
        self.assertEqual(ApplicationAmendmentRequestedEmail.subject, email.subject)

        # user logs in
        self.client.logout()
        self.client.login(self.user.email)

        self.assertTrue(application.can_user_edit)

        response = self.client.get(reverse('wl_applications:edit_application', args=(application.pk,)), follow=True)

        # check that client will be redirected to the enter details page
        self.assertRedirects(response, reverse('wl_applications:enter_details'), status_code=302,
                             target_status_code=200)

        # edit and resubmit data
        post_params = {
            'project_title-0-0': 'New Title',
            'lodge': True
        }

        response = self.client.post(reverse('wl_applications:enter_details'), post_params)

        # check that client is redirected to preview
        self.assertRedirects(response, reverse('wl_applications:preview'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        response = self.client.post(reverse('wl_applications:preview'))

        # FIXME: simulate full checkout process instead of skipping
        self.client.get(reverse('wl_applications:complete'))

        application.refresh_from_db()

        self.assertFalse(application.can_user_edit)

        self.assertEqual(application.data[0]['project_details'][0]['project_title'], 'New Title')

        self.assertEqual(application.customer_status, 'under_review')
        self.assertEqual(application.processing_status, 'ready_for_action')
        self.assertEqual(application.review_status, 'amended')

        amendment_request.refresh_from_db()

        self.assertEquals(amendment_request.status, 'amended')

        # officer logs in
        self.client.logout()
        self.client.login(self.officer.email)

        post_data = {
            'applicationID': application.id,
            'status': 'accepted'
        }

        response = self.client.post(reverse('wl_applications:set_review_status'), post_data)

        self.assertEquals(response.status_code, 200)

        application.refresh_from_db()

        self.assertEquals(application.review_status, 'accepted')

    def test_character_check(self):
        """
        Test that the character check shows for questionable characters
        """
        self.user.character_flagged = True
        self.user.save()
        application = create_and_lodge_application(self.user)

        self.assertEquals(application.character_check_status, 'not_checked')

        self.client.login(self.officer.email)

        response = self.client.get(reverse('wl_applications:process', args=(application.pk,)))

        self.assertContains(response, '<span class="glyphicon glyphicon-user"></span>')

        post_data = {
            'applicationID': application.id,
            'status': 'accepted'
        }

        response = self.client.post(reverse('wl_applications:set_character_check_status'), post_data)

        self.assertEquals(response.status_code, 200)

        application.refresh_from_db()

        self.assertEquals(application.character_check_status, 'accepted')

    def test_issued_status_after_entering_condition(self):
        """
        Test that if an application has been issued, entering condition leave the status as issued
        @see https://kanboard.dpaw.wa.gov.au/?controller=TaskViewController&action=show&task_id=2736&project_id=24
        """
        application = create_and_lodge_application(self.user)
        # set some conditions
        url = reverse('wl_applications:enter_conditions', args=[application.pk])
        condition = get_or_create_condition('0001', {"text": "For unit test"})
        data = {
            'conditionID': [condition.pk]
        }
        self.client.login(self.officer.email)
        self.assertTrue(is_client_authenticated(self.client))
        resp = self.client.post(url, data=data, follow=True)
        self.assertEquals(200, resp.status_code)
        application.refresh_from_db()
        self.assertEquals(application.processing_status, 'ready_to_issue')

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

        # now repost conditions
        url = reverse('wl_applications:enter_conditions', args=[application.pk])
        condition = get_or_create_condition('0001', {"text": "For unit test"})
        data = {
            'conditionID': [condition.pk]
        }
        resp = self.client.post(url, data=data, follow=True)
        self.assertEquals(200, resp.status_code)
        application.refresh_from_db()
        # status should not be 'ready_to_issue' but 'issued'
        expected_status = 'issued'
        self.assertEquals(application.processing_status, expected_status)

    def test_issued_declined_licences_cannot_be_assessed(self):
        """
        Test that if a licence has been issued or application declined, assessments can no longer be done.
        @see https://kanboard.dpaw.wa.gov.au/?controller=TaskViewController&action=show&task_id=2743&project_id=24
        """
        # create application to issue
        application = create_and_lodge_application(self.user)

        # send out assessment
        assessment = get_or_create_assessment(application)
        self.assertEquals(assessment.status, 'awaiting_assessment')

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

        assessment.refresh_from_db()
        self.assertEquals(assessment.status, 'assessment_expired')

        # create application to decline
        application = create_and_lodge_application(self.user)

        # send out assessment
        assessment = get_or_create_assessment(application)
        self.assertEquals(assessment.status, 'awaiting_assessment')

        # decline licence
        resp = self.client.post(reverse('wl_applications:process', args=[application.pk]), data={'decline': True},
                                follow=True)
        self.assertEquals(200, resp.status_code)

        assessment.refresh_from_db()
        self.assertEquals(assessment.status, 'assessment_expired')

    def test_declined_applications_status(self):
        """
        Test that if an application has been declined, the officer and customer will both have a declined status
        @see https://kanboard.dpaw.wa.gov.au/?controller=TaskViewController&action=show&task_id=2741&project_id=24
        """
        # create application to decline
        application = create_and_lodge_application(self.user)

        self.client.login(self.officer.email)

        # decline licence
        resp = self.client.post(reverse('wl_applications:process', args=[application.pk]),
                                data={'decline': True, 'reason': 'N/A'},
                                follow=True)
        self.assertEquals(200, resp.status_code)

        application.refresh_from_db()

        self.assertEquals(application.customer_status, 'declined')
        self.assertEquals(application.processing_status, 'declined')

        # Test that the reason is stored
        details = ApplicationDeclinedDetails.objects.filter(application=application).first()
        self.assertIsNotNone(details)
        self.assertEqual(application, details.application)
        self.assertEqual(self.officer, details.officer)
        self.assertEquals('N/A', details.reason)


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
            reverse('wl_applications:process', args=[self.application.pk]),
        ]

        self.process_urls_post = [
            {
                'url': reverse('wl_applications:process', args=[self.application.pk]),
                'data': {
                    'applicationID': self.application.pk,
                }
            },
            {
                'url': reverse('wl_applications:assign_officer'),
                'data': {
                    'applicationID': self.application.pk,
                    'userID': self.officer.pk,
                }
            },
            {
                'url': reverse('wl_applications:set_id_check_status'),
                'data': {
                    'applicationID': self.application.pk,
                    'status': 'accepted',
                }
            },
            {
                'url': reverse('wl_applications:id_request'),
                'data': {
                    'applicationID': self.application.pk,
                }
            },
            {
                'url': reverse('wl_applications:set_character_check_status'),
                'data': {
                    'applicationID': self.application.pk,
                    'status': 'accepted',
                }
            },
            {
                'url': reverse('wl_applications:set_review_status'),
                'data': {
                    'applicationID': self.application.pk,
                    'status': 'accepted',
                }
            },
            {
                'url': reverse('wl_applications:amendment_request'),
                'data': {
                    'applicationID': self.application.pk,
                }
            },
            {
                'url': reverse('wl_applications:send_for_assessment'),
                'data': {
                    'applicationID': self.application.pk,
                    'assGroupID': get_or_create_default_assessor_group().pk,
                    'status': 'awaiting_assessment'
                }
            },
            {
                'url': reverse('wl_applications:remind_assessment'),
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

        # logged-in. Should get a 403
        self.client.login(self.user.email)
        for url in self.process_urls_get:
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 403)
        for url in self.process_urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertEqual(response.status_code, 403)

    def test_officer_access(self):
        self.client.login(self.officer.email)
        for url in self.process_urls_get:
            response = self.client.get(url, follow=False)
            self.assertEqual(200, response.status_code)
        for url in self.process_urls_post:
            response = self.client.post(url['url'], url['data'], follow=True)
            self.assertEquals(200, response.status_code)
