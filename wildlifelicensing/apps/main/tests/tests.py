from __future__ import unicode_literals

import os

from django.core.urlresolvers import reverse
from django.test import TestCase

from ledger.accounts.models import EmailUser, Profile
from wildlifelicensing.apps.main.tests.helpers import SocialClient, get_or_create_default_customer, \
    get_or_create_default_officer, TestData, upload_id

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
            'user': self.customer.pk,
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

        # check no profile
        self.assertEquals(0, Profile.objects.filter(user=self.customer).count())
        # create original profile
        # address = Address.objects.create(line1='1 Test Street', locality='Test Suburb', state='WA', postcode='0001')
        # profile = Profile.objects.create(user=self.customer, name='Test Profile', email='test@testplace.net.au',
        #                                  institution='Test Institution', postal_address=address)

        post_params = {
            'user': self.customer.pk,
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

        # check that one profile has been created
        self.assertEquals(1, Profile.objects.filter(user=self.customer).count())

        profile = Profile.objects.filter(user=self.customer).first()
        # check that client can access the edit profile page
        response = self.client.get(reverse('wl_main:edit_profile', args=(profile.pk,)))
        self.assertEqual(200, response.status_code)

        # updated profile
        post_params['name'] = 'Updated Profile'
        post_params['line1'] = 'New Line 1'
        response = self.client.post(reverse('wl_main:edit_profile', args=(profile.pk,)), post_params)
        self.assertEqual(302, response.status_code)

        # get updated profile
        self.assertEquals(1, Profile.objects.filter(user=self.customer).count())

        profile = Profile.objects.filter(user=self.customer).first()

        # check that the profile has been edited
        self.assertEquals(profile.name, 'Updated Profile')
        self.assertEquals(profile.postal_address.line1, 'New Line 1')

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
        response = upload_id(self.customer)
        self.assertEqual(200, response.status_code)

        # update customer
        self.customer = EmailUser.objects.get(email=self.customer.email)

        self.assertIsNotNone(self.customer.identification)

        # assert image url is the customer ID's url path
        self.assertEqual(response.context['existing_id_image_url'], self.customer.identification.file.url)
