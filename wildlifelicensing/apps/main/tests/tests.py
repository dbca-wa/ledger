from __future__ import unicode_literals

import os

from django.core.urlresolvers import reverse
from django.test import TestCase
from social.apps.django_app.default.models import UserSocialAuth

from ledger.accounts.models import EmailUser, Address, Persona

from helpers import SocialClient, add_to_group

TEST_ID_PATH = os.path.join('wildlifelicensing', 'apps', 'main', 'test_data', 'test_id.jpg')


class AccountsTestCase(TestCase):
    def setUp(self):
        self.customer = EmailUser.objects.create(email='customer@test.net')
        UserSocialAuth.create_social_auth(self.customer, self.customer.email, 'email')

        self.officer = EmailUser.objects.create(email='officer@test.net')
        UserSocialAuth.create_social_auth(self.officer, self.officer.email, 'email')
        add_to_group(self.officer, 'Officers')

        self.client = SocialClient()

    def test_persona_list(self):
        """Testing that a user can display the persona list if they are a customer"""
        self.client.login(self.customer.email)

        # check that client can access the persona list
        response = self.client.get(reverse('main:list_personas'))
        self.assertEqual(200, response.status_code)

    def test_persona_list_non_customer(self):
        """Testing that a user cannot display the persona list if they are not a customer"""
        self.client.login(self.officer.email)

        # check that client gets redirected if they try to access the persona list
        response = self.client.get(reverse('main:list_personas'))
        self.assertEqual(302, response.status_code)

    def test_create_persona(self):
        """Testing that a user can create a persona"""
        self.client.login(self.customer.email)

        original_persona_count = Persona.objects.filter(user=self.customer).count()

        # check that client can access the create persona page
        response = self.client.get(reverse('main:create_persona'))
        self.assertEqual(200, response.status_code)

        post_params = {
            'name': 'Test Persona',
            'email': 'test@testplace.net.au',
            'institution': 'Test Institution',
            'line1': '1 Test Street',
            'locality': 'Test Suburb',
            'state': 'WA',
            'postcode': '0001'
        }

        response = self.client.post(reverse('main:create_persona'), post_params)
        self.assertEqual(302, response.status_code)

        # check that a new persona has been created
        self.assertEquals(Persona.objects.filter(user=self.customer).count(), original_persona_count + 1)

    def test_edit_persona(self):
        """Testing that a user can edit an existing persona"""
        self.client.login(self.customer.email)

        # create original persona
        address = Address.objects.create(line1='1 Test Street', locality='Test Suburb', state='WA', postcode='0001')
        persona = Persona.objects.create(user=self.customer, name='Test Persona', email='test@testplace.net.au',
                                         institution='Test Institution', postal_address=address)

        # check that client can access the edit persona page
        response = self.client.get(reverse('main:edit_persona', args=(persona.pk,)))
        self.assertEqual(200, response.status_code)

        post_params = {
            'name': 'Test Persona 2',
            'email': persona.email,
            'institution': persona.institution,
            'line1': '2 Test Street',
            'locality': address.locality,
            'state': address.state,
            'postcode': address.postcode
        }

        response = self.client.post(reverse('main:edit_persona', args=(persona.pk,)), post_params)
        self.assertEqual(302, response.status_code)

        # get updated persona
        persona = Persona.objects.get(pk=persona.pk)

        # check that the persona has been edited
        self.assertEquals(persona.name, 'Test Persona 2')
        self.assertEquals(persona.postal_address.line1, '2 Test Street')

    def test_manage_id(self):
        """Testing that a user can access the manage identification page"""
        self.client.login(self.customer.email)

        # check that client can access the manage identification page
        response = self.client.get(reverse('main:identification'))
        self.assertEqual(200, response.status_code)

    def test_upload_id(self):
        """Testing that a user can upload an ID image"""
        self.client.login(self.customer.email)

        response = self.client.get(reverse('main:identification'))
        self.assertEqual(200, response.status_code)

        try:
            with open(TEST_ID_PATH) as fp:
                post_params = {
                    'identification_file': fp
                }

                response = self.client.post(reverse('main:identification'), post_params, follow=True)
                self.assertEqual(200, response.status_code)

                # update customer
                self.customer = EmailUser.objects.get(email=self.customer.email)

                # assert customer's ID is the uploaded file
                self.assertEqual(self.customer.identification.filename, 'test_id.jpg')

                # assert image url is the customer ID's url path
                self.assertEqual(response.context['existing_id_image_url'], self.customer.identification.file.url)
        finally:
            # remove uploaded file
            os.remove(self.customer.identification.path)
