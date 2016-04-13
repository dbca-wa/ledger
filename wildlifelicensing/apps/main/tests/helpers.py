from __future__ import unicode_literals
import re

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.contrib.auth.models import Group
from social.apps.django_app.default.models import UserSocialAuth

from ledger.accounts.models import EmailUser
from wildlifelicensing.apps.main import helpers as accounts_helpers


class TestData(object):
    DEFAULT_CUSTOMER = {
        'email': 'customer@test.com',
        'first_name': 'Homer',
        'last_name': 'Cust',
        'dob': '1989-08-12',
    }
    DEFAULT_OFFICER = {
        'email': 'officer@test.com',
        'first_name': 'Offy',
        'last_name': 'Sir',
        'dob': '1979-12-13',
    }
    DEFAULT_ASSESSOR = {
        'email': 'assessor@test.com',
        'first_name': 'Assess',
        'last_name': 'Ore',
        'dob': '1979-10-05',
    }


class SocialClient(Client):
    """
    A django Client for authenticating with the social auth password-less framework.
    """

    def login(self, email):
        self.post(reverse('social:complete', kwargs={'backend': "email"}), {'email': email})
        if len(mail.outbox) == 0:
            raise Exception("Email not received")
        else:
            login_url = re.search('(?P<url>https?://[^\s]+)', mail.outbox[0].body).group('url')
            response = self.get(login_url, follow=True)
        return response


def is_client_authenticated(client):
    return '_auth_user_id' in client.session


def belongs_to(user, group_name):
    return accounts_helpers.belongs_to(user, group_name)


def add_to_group(user, group_name):
    if not belongs_to(user, group_name):
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        user.save()
    return user


def create_user(**kwargs):
    user = EmailUser.objects.create(**kwargs)
    UserSocialAuth.create_social_auth(user, user.email, 'email')
    return user


def create_default_customer():
    return create_user(**TestData.DEFAULT_CUSTOMER)


def create_default_officer():
    user = create_user(**TestData.DEFAULT_OFFICER)
    add_to_group(user, 'Officers')
    return user


def create_default_assessor():
    user = create_user(**TestData.DEFAULT_ASSESSOR)
    add_to_group(user, 'Assessors')
    return user


class HelpersTest(TestCase):
    def setUp(self):
        self.client = SocialClient()

    def test_create_customer(self):
        user = create_default_customer()
        self.assertIsNotNone(user)
        self.assertTrue(isinstance(user, EmailUser))
        self.assertEqual(TestData.DEFAULT_CUSTOMER['email'], user.email)
        # test that we can login
        self.client.login(user.email)
        is_client_authenticated(self.client)

    def test_create_officer(self):
        user = create_default_officer()
        self.assertIsNotNone(user)
        self.assertTrue(isinstance(user, EmailUser))
        self.assertEqual(TestData.DEFAULT_OFFICER['email'], user.email)
        self.assertTrue(accounts_helpers.is_officer(user))
        # test that we can login
        self.client.login(user.email)
        is_client_authenticated(self.client)

    def test_create_assessor(self):
        user = create_default_assessor()
        self.assertIsNotNone(user)
        self.assertTrue(isinstance(user, EmailUser))
        self.assertEqual(TestData.DEFAULT_ASSESSOR['email'], user.email)
        self.assertTrue(accounts_helpers.is_assessor(user))
        # test that we can login
        self.client.login(user.email)
        is_client_authenticated(self.client)
