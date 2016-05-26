from __future__ import unicode_literals

import os

from django.core.urlresolvers import reverse
from django.test import TestCase
from social.apps.django_app.default.models import UserSocialAuth

from ledger.accounts.models import EmailUser, Address, Profile, Document

from helpers import SocialClient, get_or_create_default_customer, get_or_create_default_officer, TestData

TEST_ID_PATH = TestData.TEST_ID_PATH


class AccountsTestCase(TestCase):
    def setUp(self):
        self.customer = get_or_create_default_customer()

        self.officer = get_or_create_default_officer()

        self.client = SocialClient()

    def tearDown(self):
        self.client.logout()
        # clean id file
        if self.customer.identification:
            os.remove(self.customer.identification.path)

    def test_profile_list(self):
        """Testing that a user can display the profile list if they are a customer"""
        self.client.login(self.customer.email)

        # check that client can access the profile list
        response = self.client.get(reverse('wl_main:list_profiles'))
        self.assertEqual(200, response.status_code)

    def test_profile_list_non_customer(self):
        """Testing that a user cannot display the profile list if they are not a customer"""
        self.client.login(self.officer.email)

        # check that client gets redirected if they try to access the profile list
        response = self.client.get(reverse('wl_main:list_profiles'))
        self.assertEqual(302, response.status_code)

    def test_create_profile(self):
        """Testing that a user can create a profile"""
        self.client.login(self.customer.email)

        original_profile_count = Profile.objects.filter(user=self.customer).count()

        # check that client can access the create profile page
        response = self.client.get(reverse('wl_main:create_profile'))
        self.assertEqual(200, response.status_code)

        post_params = {
            'name': 'Test Profile',
            'email': 'test@testplace.net.au',
            'institution': 'Test Institution',
            'line1': '1 Test Street',
            'locality': 'Test Suburb',
            'state': 'WA',
            'country': 'AU',
            'postcode': '0001'
        }

        response = self.client.post(reverse('wl_main:create_profile'), post_params)
        self.assertEqual(302, response.status_code)

        # check that a new profile has been created
        self.assertEquals(Profile.objects.filter(user=self.customer).count(), original_profile_count + 1)

    def test_edit_profile(self):
        """Testing that a user can edit an existing profile"""
        self.client.login(self.customer.email)

        # create original profile
        address = Address.objects.create(line1='1 Test Street', locality='Test Suburb', state='WA', postcode='0001')
        profile = Profile.objects.create(user=self.customer, name='Test Profile', email='test@testplace.net.au',
                                         institution='Test Institution', postal_address=address)

        # check that client can access the edit profile page
        response = self.client.get(reverse('wl_main:edit_profile', args=(profile.pk,)))
        self.assertEqual(200, response.status_code)

        post_params = {
            'name': 'Test Profile 2',
            'email': profile.email,
            'institution': profile.institution,
            'line1': '2 Test Street',
            'locality': address.locality,
            'state': address.state,
            'country': 'AU',
            'postcode': address.postcode
        }

        response = self.client.post(reverse('wl_main:edit_profile', args=(profile.pk,)), post_params)
        self.assertEqual(302, response.status_code)

        # get updated profile
        profile = Profile.objects.get(pk=profile.pk)

        # check that the profile has been edited
        self.assertEquals(profile.name, 'Test Profile 2')
        self.assertEquals(profile.postal_address.line1, '2 Test Street')

    def test_manage_id(self):
        """Testing that a user can access the manage identification page"""
        self.client.login(self.customer.email)

        # check that client can access the manage identification page
        response = self.client.get(reverse('wl_main:identification'))
        self.assertEqual(200, response.status_code)

    def test_upload_id(self):
        """Testing that a user can upload an ID image"""
        self.client.login(self.customer.email)
        self.assertIsNone(self.customer.identification)
        response = self.client.get(reverse('wl_main:identification'))
        self.assertEqual(200, response.status_code)

        with open(TEST_ID_PATH) as fp:
            post_params = {
                'identification_file': fp
            }
            self.client.login(self.customer.email)
            response = self.client.post(reverse('wl_main:identification'), post_params, follow=True)
            self.assertEqual(200, response.status_code)

            # update customer
            self.customer = EmailUser.objects.get(email=self.customer.email)

            self.assertIsNotNone(self.customer.identification)
            # assert customer's ID is the uploaded file
            self.assertEqual(self.customer.identification.filename, 'test_id.jpg')

            # assert image url is the customer ID's url path
            self.assertEqual(response.context['existing_id_image_url'], self.customer.identification.file.url)
