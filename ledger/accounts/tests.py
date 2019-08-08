import re

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from social_django.models import UserSocialAuth

from ledger.accounts.models import EmailUser

REGISTERED_USER_EMAIL = 'registered_user@test.net'
NEW_USER_EMAIL = 'new_user@test.net'

# TODO: Handle multi app redirections and creations from ledger accounts views. Until then some tests have been commented out.


class AccountsTestCase(TestCase):

    def setUp(self):
        user = EmailUser.objects.create(email=REGISTERED_USER_EMAIL)
        # UserSocialAuth.create_social_auth(user, user.email, 'email')

        self.client = Client()

    def test_login(self):
        """Testing that a registered user can login"""
        # we will check that another user hasn't been created at the end of the process
        original_user_count = EmailUser.objects.count()

        # check user is not logged in at this point
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.post(reverse('social:complete', kwargs={'backend': "email"}), {'email': REGISTERED_USER_EMAIL}, follow=True)

        # check response status is 302 - REDIRECT and redirects to validation complete
        # self.assertRedirects(response, reverse('home'), status_code=302, target_status_code=200)
        self.assertEqual(200, response.status_code)

        # check user is not logged in at this point
        self.assertNotIn('_auth_user_id', self.client.session)

        # check that a login token has been emailed to the user
        self.assertEqual(len(mail.outbox), 1)

        received_email = mail.outbox[0]

        # check the email is from the system
        self.assertEqual(received_email.from_email, settings.EMAIL_FROM)

        # check that the content contains a link
        self.assertIn('http', received_email.body)

        login_verification_url = re.search('(?P<url>https?://[^\s]+)', received_email.body).group('url')

        response = self.client.get(login_verification_url, follow=True)

        # check response status is 302 - REDIRECT and redirects to validation complete
        # self.assertRedirects(response, reverse('accounts:done'), status_code=302, target_status_code=200)

        # check user is logged in
        # self.assertIn('_auth_user_id', self.client.session)

        # check that the another user wasn't created
        self.assertEqual(EmailUser.objects.count(), original_user_count)

    def test_logout(self):
        """Testing that a user can logout"""
        self.client.force_login(EmailUser.objects.first(), backend=settings.AUTHENTICATION_BACKENDS[0])

        response = self.client.get(reverse('accounts:logout'))

        # check response status is 302 - REDIRECT
        self.assertRedirects(response, settings.SOCIAL_AUTH_LOGIN_REDIRECT_URL, status_code=302, target_status_code=200)

        # check user is not logged out
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_register(self):
        """Testing the registration process"""
        # we will check that another user has been created at the end of the process
        # original_user_count = EmailUser.objects.count()
        #
        # # check user is not logged in at this point
        # self.assertNotIn('_auth_user_id', self.client.session)
        #
        # response = self.client.post(reverse('social:complete', kwargs={'backend': "email"}), {'email': NEW_USER_EMAIL})
        #
        # # check response status is 302 - REDIRECT and redirects to validation complete
        # # self.assertRedirects(response, reverse('accounts:validation_sent'), status_code=302, target_status_code=200)
        #
        # # check user is not logged in at this point
        # self.assertNotIn('_auth_user_id', self.client.session)
        #
        # # check that a login token has been emailed to the user
        # self.assertEqual(len(mail.outbox), 1)
        #
        # received_email = mail.outbox[0]
        #
        # # check the email is from the system
        # self.assertEqual(received_email.from_email, settings.EMAIL_FROM)
        #
        # # check that the content contains a link
        # self.assertIn('http', received_email.body)
        #
        # login_verification_url = re.search('(?P<url>https?://[^\s]+)', received_email.body).group('url')
        #
        # response = self.client.get(login_verification_url, follow=True)

        # check response status is 302 - REDIRECT and redirects to validation complete
        #self.assertRedirects(response, reverse('accounts:customer_create'), status_code=302, target_status_code=200)

        # check user is logged in
        #self.assertIn('_auth_user_id', self.client.session)

        # check that the another user wasn't created
        #self.assertEqual(EmailUser.objects.count(), original_user_count + 1)
