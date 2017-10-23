import os
from datetime import date

from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase, TransactionTestCase

from dateutil.relativedelta import relativedelta

from ledger.accounts.models import EmailUser, Document, Address, Profile
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.applications.tests import helpers
from wildlifelicensing.apps.main.models import WildlifeLicenceType
from wildlifelicensing.apps.main.tests.helpers import SocialClient, get_or_create_default_customer, \
    create_random_customer, is_login_page, clear_mailbox, is_client_authenticated, \
    has_response_error_messages, has_response_messages
from ledger.payments.bpay.dashboard.app import application

TEST_ID_PATH = os.path.join('wildlifelicensing', 'apps', 'main', 'test_data', 'test_id.jpg')


class ApplicationEntryTestCase(TestCase):
    fixtures = ['licences.json', 'catalogue.json', 'partner.json']

    def setUp(self):
        helpers.create_default_country()
        self.customer = get_or_create_default_customer()

        self.client = SocialClient()

        self.licence_type = WildlifeLicenceType.objects.get(product_title='regulation-17')
        self.licence_type.identification_required = True
        self.licence_type.save()

    def tearDown(self):
        self.client.logout()
        # clean id file
        if self.customer.identification:
            os.remove(self.customer.identification.path)

    def test_new_application(self):
        """
        Testing that a user can begin the process of creating an application
        """
        self.client.login(self.customer.email)

        original_application_count = Application.objects.count()

        # check that client can access the licence type selection list
        response = self.client.get(reverse('wl_applications:new_application'), follow=True)

        self.assertRedirects(response, reverse('wl_applications:select_licence_type'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        self.assertEquals(Application.objects.count(), original_application_count + 1)

        application = Application.objects.get(pk=response.context['application'].id)

        self.assertEquals(application.application_type, 'new_licence')

        self.assertEqual(self.client.session['application_id'], application.id)

    def test_edit_application(self):
        """
        Testing that a user can edit an application that was either draft or requiring amendments
        """
        application = helpers.create_application(user=self.customer)
        application.customer_status = 'draft'
        application.save()
        application.refresh_from_db()

        self.client.login(self.customer.email)

        response = self.client.get(reverse('wl_applications:edit_application', args=(application.pk,)), follow=True)

        # check that client will be redirected to the enter details page
        self.assertRedirects(response, reverse('wl_applications:enter_details'), status_code=302,
                             target_status_code=200)

        # check that the data contained in the context is the same as the application data
        self.assertEquals(application.data, response.context['application'].data)

        helpers.delete_application_session(self.client)

        # check that an application that's not in an editable state can't be edited
        application.customer_status = 'under_review'
        application.save()

        response = self.client.get(reverse('wl_applications:edit_application', args=(application.pk,)))

        self.assertEqual(response.status_code, 403)

    def test_renew_licence(self):
        """
        Testing that a user can renew a licence and restart the application process based on the previous
        licence's application data
        """
        application = helpers.create_and_lodge_application(user=self.customer)
        licence = helpers.issue_licence(application, licence_data = {
            'end_date': date.today() + relativedelta(days=30),
            'is_renewable': True
        })

        self.client.login(self.customer.email)

        response = self.client.get(reverse('wl_applications:renew_licence', args=(licence.pk,)), follow=True)

        # check that client will be redirected to the enter details page
        self.assertRedirects(response, reverse('wl_applications:enter_details'), status_code=302,
                             target_status_code=200)

        self.assertNotEquals(application.id, response.context['application'].id)

        self.assertEquals(response.context['application'].application_type, 'renewal')

        # check that the data contained in the context is the same as the application data
        self.assertEquals(application.data, response.context['application'].data)

        helpers.delete_application_session(self.client)

        # check that a licence that isn't due to expire within 30 days is not cannot be renewed
        application = helpers.create_and_lodge_application(user=self.customer)
        licence = helpers.issue_licence(application, licence_data = {
            'end_date': date.today() + relativedelta(days=31),
            'is_renewable': True
        })

        response = self.client.get(reverse('wl_applications:renew_licence', args=(licence.pk,)), follow=True)

        self.assertEqual(response.status_code, 403)

        # check that a licence that isn't renewable cannot be renewed
        application = helpers.create_and_lodge_application(user=self.customer)
        licence = helpers.issue_licence(application, licence_data = {
            'end_date': date.today() + relativedelta(days=30),
            'is_renewable': False
        })

        response = self.client.get(reverse('wl_applications:renew_licence', args=(licence.pk,)), follow=True)

        self.assertEqual(response.status_code, 403)

    def test_amend_licence(self):
        """
        Testing that a user can amend a licence and restart the application process based on the previous
        licence's application data
        """
        application = helpers.create_and_lodge_application(user=self.customer)
        licence = helpers.issue_licence(application)

        self.client.login(self.customer.email)

        response = self.client.get(reverse('wl_applications:amend_licence', args=(licence.pk,)), follow=True)

        # check that client will be redirected to the enter details page
        self.assertRedirects(response, reverse('wl_applications:enter_details'), status_code=302,
                             target_status_code=200)

        self.assertNotEquals(application.id, response.context['application'].id)

        self.assertEquals(response.context['application'].application_type, 'amendment')

        # check that the data contained in the context is the same as the application data
        self.assertEquals(application.data, response.context['application'].data)

    def test_select_licence_type(self):
        """
        Testing that a user can display the licence type selection list
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))

        # check that client can access the licence type selection list
        response = self.client.get(reverse('wl_applications:select_licence_type'))
        self.assertEqual(200, response.status_code)

        # check that client can select a licence type the licence type selection list
        response = self.client.get(reverse('wl_applications:select_licence_type', args=(self.licence_type.pk,)))

        self.assertRedirects(response, reverse('wl_applications:check_identification'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

    def test_check_identification_required_no_current_id(self):
        """
        Testing that a user can display the identification required page in the case the user has no
        current identification, and upload an ID.
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(self.licence_type.pk,)))

        # check that client can access the identification required page
        response = self.client.get(reverse('wl_applications:check_identification'))
        self.assertEqual(200, response.status_code)

        with open(TEST_ID_PATH, 'rb') as fp:
            post_params = {
                'identification_file': fp
            }
            response = self.client.post(reverse('wl_applications:check_identification'),
                                        post_params, follow=True)

            self.assertRedirects(response, reverse('wl_applications:create_select_profile'),
                                 status_code=302, target_status_code=200, fetch_redirect_response=True)

            # update customer
            self.customer = EmailUser.objects.get(email=self.customer.email)

    def test_check_identification_required_current_id(self):
        """
        Testing that a user can display the identification required page in the case the user has a
        current identification.
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(self.licence_type.pk,)))
        self.client.get(reverse('wl_applications:check_identification'))

        with open(TEST_ID_PATH, 'rb') as fp:
            self.customer.identification = Document.objects.create(name='test_id')
            self.customer.identification.file.save('test_id.jpg', File(fp), save=True)
            self.customer.save()

        # check that client is redirected to profile creation / selection page
        response = self.client.get(reverse('wl_applications:check_identification'), follow=True)
        self.assertRedirects(response, reverse('wl_applications:create_select_profile'),
                             status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_create_select_profile_create(self):
        """
        Testing that a user can display the create / select profile page and create a profile
        in the case the user has no profile
        """
        self.client.login(self.customer.email)

        original_profile_count = self.customer.profiles.count()

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(self.licence_type.pk,)))

        # check that client can access the profile create/select page
        response = self.client.get(reverse('wl_applications:create_select_profile'))
        self.assertEqual(200, response.status_code)

        # check there is not a profile selection form, meaning there is no profile
        self.assertFalse('profile_selection_form' in response.context)

        post_params = {
            'user': self.customer.pk,
            'name': 'Test Profile',
            'email': 'test@testplace.net.au',
            'institution': 'Test Institution',
            'line1': '1 Test Street',
            'locality': 'Test Suburb',
            'state': 'WA',
            'country': 'AU',
            'postcode': '0001',
            'create': True
        }

        response = self.client.post(reverse('wl_applications:create_select_profile'), post_params)

        # check that client is redirected to enter details page
        self.assertRedirects(response, reverse('wl_applications:enter_details'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        # check that a new profile was created
        self.assertEqual(self.customer.profiles.count(), original_profile_count + 1)

        # check the created profile has been set in the application
        self.assertEquals(self.customer.profiles.first(), Application.objects.first().applicant_profile)

    def test_create_select_profile_select(self):
        """
        Testing that a user can display the create / select profile page and select a profile
        in the case the user has one or more existing profiles
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(self.licence_type.pk,)))

        # create profiles
        address1 = Address.objects.create(user=self.customer, line1='1 Test Street', locality='Test Suburb',
                                          state='WA', postcode='0001')
        profile1 = Profile.objects.create(user=self.customer, name='Test Profile', email='test@testplace.net.au',
                                          institution='Test Institution', postal_address=address1)

        address2 = Address.objects.create(user=self.customer, line1='2 Test Street', locality='Test Suburb',
                                          state='WA', postcode='0001')
        profile2 = Profile.objects.create(user=self.customer, name='Test Profile 2', email='test@testplace.net.au',
                                          institution='Test Institution', postal_address=address2)

        # check that client can access the profile create/select page
        response = self.client.get(reverse('wl_applications:create_select_profile'))
        self.assertEqual(200, response.status_code)

        # check there is a profile selection form, meaning there at least one existing profile
        self.assertTrue('profile_selection_form' in response.context)

        post_params = {
            'profile': profile2.pk,
            'select': True
        }

        response = self.client.post(reverse('wl_applications:create_select_profile'), post_params)

        # check that client is redirected to enter details page
        self.assertRedirects(response, reverse('wl_applications:enter_details'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        # check the created profile has been set in the application
        self.assertEquals(profile2, Application.objects.first().applicant_profile)

    def test_enter_details_draft(self):
        """
        Testing that a user can enter the details of an application form and save as a draft
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(self.licence_type.pk,)))

        application = Application.objects.first()

        # check that the state of the application is temp
        self.assertEqual(application.processing_status, 'temp')

        # check that client can access the enter details page
        response = self.client.get(reverse('wl_applications:enter_details'))
        self.assertEqual(200, response.status_code)

        post_params = {
            'project_title-0-0': 'Test Title',
            'draft': True
        }

        response = self.client.post(reverse('wl_applications:enter_details'), post_params)

        # check that client is redirected to the dashboard
        self.assertRedirects(response, reverse('wl_dashboard:home'), status_code=302, target_status_code=200,
                             fetch_redirect_response=False)

        application.refresh_from_db()

        # check that the state of the application is draft
        self.assertEqual(application.processing_status, 'draft')

        # check that the state of the application is draft
        self.assertEqual(application.data[0]['project_details'][0]['project_title'], 'Test Title')

    def test_enter_details_draft_continue(self):
        """
        Testing that a user can enter the details of an application form and save as a draft
        and continue editing
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(self.licence_type.pk,)))

        application = Application.objects.first()

        # check that the state of the application is temp
        self.assertEqual(application.processing_status, 'temp')

        # check that client can access the enter details page
        response = self.client.get(reverse('wl_applications:enter_details'))
        self.assertEqual(200, response.status_code)

        post_params = {
            'project_title-0-0': 'Test Title',
            'draft_continue': True
        }

        response = self.client.post(reverse('wl_applications:enter_details'), post_params)

        # check that client is redirected back to enter details page
        self.assertRedirects(response, reverse('wl_applications:enter_details'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        application.refresh_from_db()

        # check that the state of the application is draft
        self.assertEqual(application.processing_status, 'draft')

        # check that the state of the application is draft
        self.assertEqual(application.data[0]['project_details'][0]['project_title'], 'Test Title')

    def test_enter_details_preview(self):
        """
        Testing that a user can enter the details of an application form and that the data is
        saved in the session for previewing
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(self.licence_type.pk,)))

        # check that client can access the enter details page
        response = self.client.get(reverse('wl_applications:enter_details'))
        self.assertEqual(200, response.status_code)

        post_params = {
            'project_title-0-0': 'Test Title',
            'lodge': True
        }

        response = self.client.post(reverse('wl_applications:enter_details'), post_params)

        # check that client is redirected to preview
        self.assertRedirects(response, reverse('wl_applications:preview'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        application = Application.objects.first()

        # check that the state of the application is temp
        self.assertEqual(application.processing_status, 'temp')

        # check that the state of the application is draft
        self.assertEqual(application.data[0]['project_details'][0]['project_title'], 'Test Title')

    def test_preview_lodge(self):
        """
        Testing that a user can preview the details of an application form then lodge the application
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(self.licence_type.pk,)))

        application = Application.objects.first()
        self.assertIsNotNone(application.applicant)

        # check that the state of the application is temp
        self.assertEqual(application.processing_status, 'temp')

        response = self.client.post(reverse('wl_applications:preview'))

        # check that client is redirected to checkout
        self.assertRedirects(response, reverse('wl_payments:checkout_application', args=(application.pk,)),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        # FIXME: simulate full checkout process instead of skipping
        self.client.get(reverse('wl_applications:complete'))

        application.refresh_from_db()

        # check that the state of the application is new
        self.assertEqual(application.processing_status, 'new')

    def test_delete_application(self):
        """
        Testing that when a user leaves the application entry workflow unexpectedly, the temporary application
        and session application reference they were working with are deleted.
        """
        self.client.login(self.customer.email)

        response = self.client.get(reverse('wl_applications:new_application'), follow=True)

        self.assertRedirects(response, reverse('wl_applications:select_licence_type'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        application_id = response.context['application'].id

        self.assertIn('application_id', self.client.session)

        self.assertEqual(application_id, self.client.session['application_id'])

        response = self.client.post(reverse('wl_applications:delete_application_session'), {
            'applicationId': application_id
        })

        self.assertEqual(response.status_code, 200)

        self.assertNotIn('application_id', self.client.session)

        self.assertFalse(Application.objects.filter(pk=application_id).exists())

        response = self.client.get(reverse('wl_applications:new_application'))

        self.assertRedirects(response, reverse('wl_applications:select_licence_type'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

    def test_multiple_application_entry_denied(self):
        """
        Testing the if a user is in the process of entering an application and attempts to start/edit/renew/amend
        another application, they are redirected back to home
        """
        entry_denied_message = ('There is currently another application in the process of being entered. Please ' +
                                'conclude or save this application before creating a new one. If you are seeing this ' +
                                'message and there is not another application being entered, you may need to '+ 
                                '<a href="{}">logout</a> and log in again.').format(reverse('accounts:logout'))

        self.client.login(self.customer.email)

        response = self.client.get(reverse('wl_applications:new_application'))

        self.assertRedirects(response, reverse('wl_applications:select_licence_type'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        # attempt to start another new licence application
        response = self.client.get(reverse('wl_applications:new_application'), follow=True)

        self.assertRedirects(response, reverse('wl_dashboard:tables_customer'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        self.assertIn('messages', response.context)
        self.assertEquals(len(response.context['messages']), 1)
        self.assertEquals([str(m.message) for m in response.context['messages']][0], entry_denied_message)

        application = helpers.create_application(user=self.customer)

        # attempt to edit an application
        response = self.client.get(reverse('wl_applications:edit_application', args=(application.pk, )), follow=True)

        self.assertRedirects(response, reverse('wl_dashboard:tables_customer'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        self.assertIn('messages', response.context)
        self.assertEquals(len(response.context['messages']), 1)
        self.assertEquals([str(m.message) for m in response.context['messages']][0], entry_denied_message)

        application = helpers.create_and_lodge_application(user=self.customer)
        licence = helpers.issue_licence(application, licence_data = {
            'end_date': date.today() + relativedelta(days=30),
            'is_renewable': True
        })

        # attempt to renew a licence
        response = self.client.get(reverse('wl_applications:renew_licence', args=(licence.pk, )), follow=True)

        self.assertRedirects(response, reverse('wl_dashboard:tables_customer'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)


        self.assertIn('messages', response.context)
        self.assertEquals(len(response.context['messages']), 1)
        self.assertEquals([str(m.message) for m in response.context['messages']][0], entry_denied_message)

        response = self.client.get(reverse('wl_applications:amend_licence', args=(licence.pk, )), follow=True   )

        # attempt to amend a licence
        self.assertRedirects(response, reverse('wl_dashboard:tables_customer'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        self.assertIn('messages', response.context)
        self.assertEquals(len(response.context['messages']), 1)
        self.assertEquals([str(m.message) for m in response.context['messages']][0], entry_denied_message)

class ApplicationEntrySecurity(TransactionTestCase):
    fixtures = ['licences.json']
    serialized_rollback = True

    def setUp(self):
        self.client = SocialClient()

    def tearDown(self):
        self.client.logout()

    def test_user_access_other_user(self):
        """
        Test that a user cannot edit/view another user application
        """
        customer1 = create_random_customer()
        customer2 = create_random_customer()
        self.assertNotEqual(customer1, customer2)

        application1 = helpers.create_application(user=customer1)
        application2 = helpers.create_application(user=customer2)
        self.assertNotEqual(application1, application2)

        # login as user1
        self.client.login(customer1.email)
        my_url = reverse('wl_applications:edit_application', args=[application1.pk])
        response = self.client.get(my_url)
        self.assertEqual(302, response.status_code)

        forbidden_urls = [
            reverse('wl_applications:edit_application', args=[application2.pk]),
        ]

        for forbidden_url in forbidden_urls:
            response = self.client.get(forbidden_url, follow=True)
            self.assertEqual(403, response.status_code)

    def test_user_access_lodged(self):
        """
        Once the application if lodged the user should not be able to edit it
        """
        customer1 = create_random_customer()
        self.client.login(customer1)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(1,)))

        application = Application.objects.first()
        self.assertIsNotNone(application)
        self.assertIsNotNone(application.applicant)

        # check that the state of the application is temp
        self.assertEqual(application.processing_status, 'temp')

        response = self.client.post(reverse('wl_applications:preview'))

        # check that client is redirected to checkout
        self.assertRedirects(response, reverse('wl_payments:checkout_application', args=(application.pk,)),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        # FIXME: simulate full checkout process instead of skipping
        self.client.get(reverse('wl_applications:complete'))

        application.refresh_from_db()

        # check that the state of the application is new/underreview
        self.assertEqual(application.processing_status, 'new')
        self.assertEqual('under_review', application.customer_status)

        response = self.client.get(reverse('wl_applications:edit_application', args=[application.pk]), follow=True)
        self.assertEqual(403, response.status_code)

    def test_user_not_logged_is_redirected_to_login(self):
        """
        A user not logged in should be redirected to the login page and not see a 403
        """
        customer1 = create_random_customer()
        self.client.login(customer1)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=(1,)))

        application = Application.objects.first()
        self.assertIsNotNone(application)

        # check that the state of the application is temp
        self.assertEqual(application.processing_status, 'temp')

        response = self.client.post(reverse('wl_applications:preview'))

        # check that client is redirected to checkout
        self.assertRedirects(response, reverse('wl_payments:checkout_application', args=(application.pk,)),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        # FIXME: simulate full checkout process instead of skipping
        self.client.get(reverse('wl_applications:complete'))

        application.refresh_from_db()

        # check that the state of the application is new/underreview
        self.assertEqual(application.processing_status, 'new')
        self.assertEqual('under_review', application.customer_status)

        # logout
        self.client.logout()

        response = self.client.get(reverse('wl_applications:edit_application', args=[application.pk]), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue(is_login_page(response))


class TestApplicationDiscardView(TestCase):
    """
    Rules of discard:
    If draft not submitted -> delete the app
    otherwise -> flag as discarded
    @see https://kanboard.dpaw.wa.gov.au/?controller=TaskViewController&action=show&task_id=2833&project_id=24

    External person must be able to discard application pushed back .
    @see https://kanboard.dpaw.wa.gov.au/?controller=TaskViewController&action=show&task_id=2743&project_id=24
    """
    fixtures = ['licences.json', 'catalogue.json', 'partner.json']

    def setUp(self):
        self.client = SocialClient()
        self.officer = helpers.get_or_create_default_officer()
        self.applicant = get_or_create_default_customer()
        self.assertNotEqual(self.officer, self.applicant)

    def tearDown(self):
        self.client.logout()
        clear_mailbox()

    def test_cannot_discard(self):
        """
        Test that an application cannot be discarded if it hasn't been pushed back to the applicant.
        Formally its processing status must be in the list of Application.CUSTOMER_DISCARDABLE_STATE
        :return:
        """
        # lodge application
        application = helpers.create_and_lodge_application(self.applicant)
        self.assertFalse(application.is_discardable)

        # try to discard with get or post
        previous_processing_status = application.processing_status
        previous_customer_status = application.customer_status
        url = reverse('wl_applications:discard_application', args=[application.pk])
        self.client.login(self.applicant.email)
        self.assertTrue(is_client_authenticated(self.client))
        resp = self.client.get(url, follow=True)
        application.refresh_from_db()
        # status should be unchanged
        self.assertNotEqual(application.processing_status, 'discarded')
        self.assertNotEqual(application.customer_status, 'discarded')
        self.assertEqual(application.processing_status, previous_processing_status)
        self.assertEqual(application.customer_status, previous_customer_status)
        # the response should have an error message
        self.assertTrue(has_response_error_messages(resp))

        # same with post method
        resp = self.client.post(url, follow=True)
        application.refresh_from_db()
        # status should be unchanged
        self.assertNotEqual(application.processing_status, 'discarded')
        self.assertNotEqual(application.customer_status, 'discarded')
        self.assertEqual(application.processing_status, previous_processing_status)
        self.assertEqual(application.customer_status, previous_customer_status)
        # the response should have an error message
        self.assertTrue(has_response_error_messages(resp))

    def test_pushed_back_application_discarded_not_deleted(self):
        # lodge application
        application = helpers.create_and_lodge_application(self.applicant)
        self.assertFalse(application.is_discardable)
        # officer request amendment
        url = reverse('wl_applications:amendment_request')
        self.client.login(self.officer.email)
        resp = self.client.post(url, data={
            'application': application.pk,
            'officer': self.officer.pk,
            'reason': 'missing_information'
        })
        self.assertEquals(resp.status_code, 200)
        application.refresh_from_db()
        # application should now be discardable
        self.assertTrue(application.is_discardable)
        # but not deletable
        self.assertFalse(application.is_deletable)

        # discard
        self.client.logout()
        clear_mailbox()
        self.client.login(self.applicant.email)
        self.assertTrue(is_client_authenticated(self.client))
        url = reverse('wl_applications:discard_application', args=[application.pk])
        # the get should not discard but return a confirm page
        previous_processing_status = application.processing_status
        previous_customer_status = application.customer_status
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)
        # test that there's a cancel_url in the context of the response and an action_url that is set to the proper url
        self.assertTrue('cancel_url' in resp.context)
        self.assertEqual(resp.context['cancel_url'], reverse('wl_dashboard:home'))
        self.assertTrue('action_url' in resp.context)
        self.assertEquals(resp.context['action_url'], url)
        application.refresh_from_db()
        # status should be unchanged
        self.assertNotEqual(application.processing_status, 'discarded')
        self.assertNotEqual(application.customer_status, 'discarded')
        self.assertEqual(application.processing_status, previous_processing_status)
        self.assertEqual(application.customer_status, previous_customer_status)

        # actual discard
        resp = self.client.post(url, data=None, follow=True)
        self.assertEquals(resp.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.processing_status, 'discarded')
        self.assertEqual(application.customer_status, 'discarded')
        # there should be a message
        self.assertTrue(has_response_messages(resp))
        self.assertFalse(has_response_error_messages(resp))

    def test_not_submitted_draft_are_deleted(self):
        """
        This is the happy path and the only use case where the application can be deleted.
        User create application, save as draft and delete it
        """
        self.client.login(self.applicant.email)
        application = helpers.create_application(self.applicant)
        self.assertEquals(application.customer_status, 'temp')
        self.assertFalse(application.is_discardable)

        # save application as a draft
        helpers.set_application_session(self.client, application)
        pk = self.client.session['application_id']
        self.assertEqual(application.pk, pk)
        url = reverse('wl_applications:enter_details')
        data = {
            'draft': 'draft'
        }
        resp = self.client.post(url, data=data, follow=True)
        self.assertEqual(resp.status_code, 200)
        application.refresh_from_db()
        self.assertEquals(application.customer_status, 'draft')

        # application should now be discardable
        self.assertTrue(application.is_discardable)
        # and deletable
        self.assertTrue(application.is_deletable)

        # discard
        url = reverse('wl_applications:discard_application', args=[application.pk])
        # the get should not delete but return a confirm page
        previous_processing_status = application.processing_status
        previous_customer_status = application.customer_status
        resp = self.client.get(url, follow=True)
        self.assertEquals(resp.status_code, 200)
        # test that there's a cancel_url in the context of the response and an action_url that is set to the proper url
        self.assertTrue('cancel_url' in resp.context)
        self.assertEqual(resp.context['cancel_url'], reverse('wl_dashboard:home'))
        self.assertTrue('action_url' in resp.context)
        self.assertEquals(resp.context['action_url'], url)
        # Application should not be deleted
        application = Application.objects.filter(pk=application.pk).first()
        self.assertIsNotNone(application)
        # status should be unchanged
        self.assertEqual(application.processing_status, previous_processing_status)
        self.assertEqual(application.customer_status, previous_customer_status)

        # actual discard
        resp = self.client.post(url, data=None, follow=True)
        self.assertEquals(resp.status_code, 200)
        # Application should now be deleted
        application = Application.objects.filter(pk=application.pk).first()
        self.assertIsNone(application)

    def test_submitted_draft_cannot_be_deleted(self):
        """
        Use case:
        Applicant lodge an application.
        Officer send it back to him with amendments requested
        Applicant reopen it and save it as a draft
        At this stage the user should not be able to delete it because it has already been lodged
        """
        # lodge application
        application = helpers.create_and_lodge_application(self.applicant)
        # application should not be discardable
        self.assertFalse(application.is_discardable)
        # and not deletable
        self.assertFalse(application.is_deletable)

        # officer request amendment
        url = reverse('wl_applications:amendment_request')
        self.client.login(self.officer.email)
        resp = self.client.post(url, data={
            'application': application.pk,
            'officer': self.officer.pk,
            'reason': 'missing_information'
        })
        self.assertEquals(resp.status_code, 200)
        application.refresh_from_db()
        self.client.logout()

        self.client.login(self.applicant.email)
        url = reverse('wl_applications:edit_application', args=[application.pk])
        self.client.get(url, follow=True)
        # save as draft
        data = {
            'draft': 'draft',
            'data': application.data
        }
        url = reverse('wl_applications:enter_details')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.customer_status, 'draft')
        # application should now be discardable
        self.assertTrue(application.is_discardable)
        # and not deletable
        self.assertFalse(application.is_deletable)

        # actual discard
        url = reverse('wl_applications:discard_application', args=[application.pk])
        resp = self.client.post(url, follow=True)
        # application should not be deleted
        application = Application.objects.filter(pk=application.pk).first()
        self.assertIsNotNone(application)
        # but in a discarded state
        self.assertEqual(application.processing_status, 'discarded')
        self.assertEqual(application.customer_status, 'discarded')
        # there should be a message
        self.assertTrue(has_response_messages(resp))
        self.assertFalse(has_response_error_messages(resp))
