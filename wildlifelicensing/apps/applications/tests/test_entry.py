import os

from django.core.urlresolvers import reverse
from django.core.files import File
from django.test import TestCase, TransactionTestCase

from ledger.accounts.models import EmailUser, Document, Address, Profile

from wildlifelicensing.apps.main.models import WildlifeLicenceType
from wildlifelicensing.apps.main.tests.helpers import SocialClient, get_or_create_default_customer, create_random_customer, \
    is_login_page
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.applications.tests import helpers

TEST_ID_PATH = os.path.join('wildlifelicensing', 'apps', 'main', 'test_data', 'test_id.jpg')


class ApplicationEntryTestCase(TestCase):
    fixtures = ['licences.json', 'countries.json',  'catalogue.json', 'partner.json']

    def setUp(self):
        self.customer = get_or_create_default_customer()

        self.client = SocialClient()

        licence_type = WildlifeLicenceType.objects.get(code_slug='regulation-17')
        licence_type.identification_required = True
        licence_type.save()

    def tearDown(self):
        self.client.logout()
        # clean id file
        if self.customer.identification:
            os.remove(self.customer.identification.path)

    def test_new_application(self):
        """Testing that a user begin the process of creating an application"""
        self.client.login(self.customer.email)

        original_application_count = Application.objects.count()

        # check that client can access the licence type selection list
        response = self.client.get(reverse('wl_applications:new_application'))

        self.assertRedirects(response, reverse('wl_applications:select_licence_type'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        self.assertEquals(Application.objects.count(), original_application_count + 1)

        self.assertEqual(self.client.session['application_id'], Application.objects.first().id)

    def test_select_licence_type(self):
        """Testing that a user can display the licence type selection list"""
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))

        # check that client can access the licence type selection list
        response = self.client.get(reverse('wl_applications:select_licence_type'))
        self.assertEqual(200, response.status_code)

        # check that client can select a licence type the licence type selection list
        response = self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

        self.assertRedirects(response, reverse('wl_applications:check_identification'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

    def test_check_identification_required_no_current_id(self):
        """Testing that a user can display the identification required page in the case the user has no
        current identification, and upload an ID.
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

        # check that client can access the identification required page
        response = self.client.get(reverse('wl_applications:check_identification'))
        self.assertEqual(200, response.status_code)

        with open(TEST_ID_PATH, 'rb') as fp:
            post_params = {
                'identification_file': fp
            }
            response = self.client.post(reverse('wl_applications:check_identification'),
                                        post_params)

            self.assertRedirects(response, reverse('wl_applications:create_select_profile'),
                                 status_code=302, target_status_code=200, fetch_redirect_response=False)

            # update customer
            self.customer = EmailUser.objects.get(email=self.customer.email)

    def test_check_identification_required_current_id(self):
        """Testing that a user can display the identification required page in the case the user has a
        current identification.
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))
        self.client.get(reverse('wl_applications:check_identification'))

        with open(TEST_ID_PATH, 'rb') as fp:
            self.customer.identification = Document.objects.create(name='test_id')
            self.customer.identification.file.save('test_id.jpg', File(fp), save=True)
            self.customer.save()

        # check that client is redirected to profile creation / selection page
        response = self.client.get(reverse('wl_applications:check_identification'))
        self.assertRedirects(response, reverse('wl_applications:create_select_profile'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

    def test_create_select_profile_create(self):
        """Testing that a user can display the create / select profile page and create a profile
        in the case the user has no profile
        """
        self.client.login(self.customer.email)

        original_profile_count = self.customer.profile_set.count()

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

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
        self.assertEqual(self.customer.profile_set.count(), original_profile_count + 1)

        # check the created profile has been set in the application
        self.assertEquals(self.customer.profile_set.first(), Application.objects.first().applicant_profile)

    def test_create_select_profile_select(self):
        """Testing that a user can display the create / select profile page and select a profile
        in the case the user has one or more existing profiles
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

        # create profiles
        address1 = Address.objects.create(line1='1 Test Street', locality='Test Suburb', state='WA', postcode='0001')
        profile1 = Profile.objects.create(user=self.customer, name='Test Profile', email='test@testplace.net.au',
                                          institution='Test Institution', postal_address=address1)

        address2 = Address.objects.create(line1='2 Test Street', locality='Test Suburb', state='WA', postcode='0001')
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
        """Testing that a user can enter the details of an application form and save as a draft
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

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
        """Testing that a user can enter the details of an application form and save as a draft
        and continue editing"""
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

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
        """Testing that a user can enter the details of an application form and that the data is
        saved in the session for previewing
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

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
        """Testing that a user can preview the details of an application form then lodge the application
        """
        self.client.login(self.customer.email)

        self.client.get(reverse('wl_applications:new_application'))
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

        application = Application.objects.first()

        # check that the state of the application is temp
        self.assertEqual(application.processing_status, 'temp')

        response = self.client.post(reverse('wl_applications:preview'))

        # check that client is redirected to complete
        self.assertRedirects(response, reverse('wl_applications:complete'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        application.refresh_from_db()

        # check that the state of the application is new
        self.assertEqual(application.processing_status, 'new')


class ApplicationEntrySecurity(TransactionTestCase):
    fixtures = ['licences.json']

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
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

        application = Application.objects.first()

        # check that the state of the application is temp
        self.assertEqual(application.processing_status, 'temp')

        response = self.client.post(reverse('wl_applications:preview'))

        # check that client is redirected to home
        self.assertRedirects(response, reverse('wl_dashboard:home'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

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
        self.client.get(reverse('wl_applications:select_licence_type', args=('regulation-17',)))

        application = Application.objects.first()

        # check that the state of the application is temp
        self.assertEqual(application.processing_status, 'temp')

        response = self.client.post(reverse('wl_applications:preview'))

        # check that client is redirected to home
        self.assertRedirects(response, reverse('wl_dashboard:home'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        application.refresh_from_db()

        # check that the state of the application is new/underreview
        self.assertEqual(application.processing_status, 'new')
        self.assertEqual('under_review', application.customer_status)

        # logout
        self.client.logout()

        response = self.client.get(reverse('wl_applications:edit_application', args=[application.pk]), follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue(is_login_page(response))
