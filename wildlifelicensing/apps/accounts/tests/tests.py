from __future__ import unicode_literals
import re

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from social.apps.django_app.default.models import UserSocialAuth

from rollcall.models import EmailUser

from wildlifelicensing.apps.accounts.models import Customer
from .utils_test import is_client_authenticated, login, belongs_to

REGISTERED_USER_EMAIL = 'registered_user@test.net'
NEW_USER_EMAIL = 'new_user@test.net'


class AccountsTestCase(TestCase):
    def setUp(self):
        user = EmailUser.objects.create(email=REGISTERED_USER_EMAIL)
        UserSocialAuth.create_social_auth(user, user.email, 'email')

        self.client = Client()

    def test_login(self):
        """Testing that a registered user can login"""
        # we will check that another user hasn't been created at the end of the process
        original_user_count = EmailUser.objects.count()

        # check user is not logged in at this point
        self.assertFalse(is_client_authenticated(self.client))

        response = self.client.post(reverse('social:complete', kwargs={'backend': "email"}),
                                    {'email': REGISTERED_USER_EMAIL})

        # check response status is 302 - REDIRECT and redirects to validation complete which in turn redirects to home
        self.assertRedirects(response, reverse('accounts:validation_sent'), status_code=302, target_status_code=302)

        # check user is not logged in at this point
        self.assertFalse(is_client_authenticated(self.client))

        # check that a login token has been emailed to the user
        self.assertEqual(len(mail.outbox), 1)

        received_email = mail.outbox[0]

        # check the email is from the system
        self.assertEqual(received_email.from_email, settings.EMAIL_FROM)

        # check that the content contains a link
        self.assertIn('http', received_email.body)

        login_verification_url = re.search('(?P<url>https?://[^\s]+)', received_email.body).group('url')

        response = self.client.get(login_verification_url, follow=True)

        # check response status is 302 - REDIRECT and redirects to validation complete which in turn redirects to home
        self.assertRedirects(response, reverse('home'), status_code=302, target_status_code=200)

        # check user is logged in
        self.assertTrue(is_client_authenticated(self.client))

        # check that the another user wasn't created
        self.assertEqual(EmailUser.objects.count(), original_user_count)

    def test_logout(self):
        """Testing that a user can logout"""
        self.client.force_login(EmailUser.objects.first(), backend=settings.AUTHENTICATION_BACKENDS[0])

        response = self.client.get(reverse('accounts:logout'))

        # check response status is 302 - REDIRECT 
        self.assertRedirects(response, reverse('home'), status_code=302, target_status_code=200)

        # check user is not logged in
        self.assertFalse(is_client_authenticated(self.client))

    def test_register(self):
        """Testing the registration process"""
        # we will check that another user has been created at the end of the process
        original_user_count = EmailUser.objects.count()

        # check user is not logged in at this point
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.post(reverse('social:complete', kwargs={'backend': "email"}), {'email': NEW_USER_EMAIL})

        # check response status is 302 - REDIRECT and redirects to validation complete which in turn redirects to home
        self.assertRedirects(response, reverse('accounts:validation_sent'), status_code=302, target_status_code=302)

        # check user is not logged in at this point
        self.assertFalse(is_client_authenticated(self.client))

        # check that a login token has been emailed to the user
        self.assertEqual(len(mail.outbox), 1)

        received_email = mail.outbox[0]

        # check the email is from the system
        self.assertEqual(received_email.from_email, settings.EMAIL_FROM)

        # check that the content contains a link
        self.assertIn('http', received_email.body)

        login_verification_url = re.search('(?P<url>https?://[^\s]+)', received_email.body).group('url')

        response = self.client.get(login_verification_url, follow=True)

        # check response status is 302 - REDIRECT and redirects to validation complete which in turn redirects to home
        self.assertRedirects(response, reverse('accounts:customer_create'), status_code=302, target_status_code=200)

        # check user is logged in
        self.assertTrue(is_client_authenticated(self.client))

        # check that the another user wasn't created
        self.assertEqual(EmailUser.objects.count(), original_user_count + 1)


class CustomerRegistrationTest(TestCase):
    DEFAULT_CUSTOMER_DATA = {
        'first_name': 'Mark',
        'last_name': 'Test',
        'title': 'Dr',
        'dob': '01/08/1989',
        'phone_number': '123456',
        'mobile_number': '67890',
        'fax_number': '27362',
        'organisation': 'Spectre',
        'line1': '123 Lorre Avenue',
        'locality': 'Perth',
        'state': 'WA',
        'postcode': 6000
    }

    def setUp(self):
        self.url = reverse('accounts:customer_create')

    def test_anonymous_access(self):
        """
        Test that an non auth cannot access the view should redirect LOGIN_URL
        """
        client = Client()
        self.assertFalse(is_client_authenticated(client))
        response = client.get(self.url, follow=True)
        expected_url = settings.LOGIN_URL + '?next=' + self.url
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)

    def test_authenticated_user_success(self):
        """
        A new authenticated user should see the page
        """
        client = login('user@test.com')
        self.assertTrue(is_client_authenticated(client))
        response = client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_customer_creation_happy_path(self):
        self.assertFalse(Customer.objects.exists())
        client = login('user@test.com')
        response = client.get(self.url)
        self.assertEqual(200, response.status_code)
        form_data = self.DEFAULT_CUSTOMER_DATA
        response = client.post(self.url, data=form_data, follow=True)
        # a successful submission should redirect to the customer dashboard
        self.assertRedirects(response, reverse('customers:dashboard'), status_code=302, target_status_code=200)
        self.assertEqual(1, Customer.objects.count())
        customer = Customer.objects.first()
        # auth user details verifications
        self.assertIsNotNone(customer.user)
        self.assertEqual(form_data['first_name'], customer.user.first_name)
        self.assertEqual(form_data['last_name'], customer.user.last_name)
        # customer details verifications
        self.assertEqual(form_data['title'], customer.title)
        self.assertEqual(form_data['dob'], customer.dob.strftime("%d/%m/%Y"))
        self.assertEqual(form_data['phone_number'], customer.phone_number)
        self.assertEqual(form_data['mobile_number'], customer.mobile_number)
        self.assertEqual(form_data['fax_number'], customer.fax_number)
        self.assertEqual(form_data['organisation'], customer.organisation)
        # address details
        self.assertIsNotNone(customer.residential_address)
        address = customer.residential_address
        self.assertEqual(form_data['line1'], address.line1)
        self.assertEqual(form_data['locality'], address.locality)
        self.assertEqual(form_data['state'], address.state)
        self.assertEqual(form_data['postcode'], address.postcode)

        # postal and billing address should be set to the residential
        self.assertEqual(customer.residential_address, customer.postal_address)
        self.assertEqual(customer.residential_address, customer.postal_address)

        # test that the user belongs to the Customers group
        self.assertTrue(belongs_to(customer.user, 'Customers'))
