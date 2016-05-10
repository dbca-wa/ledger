from __future__ import unicode_literals
import re
import os

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.contrib.auth.models import Group
from mixer.backend.django import mixer
from social.apps.django_app.default.models import UserSocialAuth

from ledger.accounts.models import EmailUser
from wildlifelicensing.apps.main.models import WildlifeLicenceType, AssessorGroup
from wildlifelicensing.apps.main import helpers as accounts_helpers


class TestData(object):
    TEST_ID_PATH = os.path.join('wildlifelicensing', 'apps', 'main', 'test_data', 'test_id.jpg')

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
    DEFAULT_ASSESSOR_GROUP = {
        'name': 'ass group',
        'email': 'assessor@test.com',
    }


class SocialClient(Client):
    """
    A django Client for authenticating with the social auth password-less framework.
    """

    def login(self, email):
        # important clear the mail box before
        clear_mailbox()
        self.post(reverse('social:complete', kwargs={'backend': "email"}), {'email': email})
        if len(mail.outbox) == 0:
            raise Exception("Email not received")
        else:
            login_url = re.search('(?P<url>https?://[^\s]+)', mail.outbox[0].body).group('url')
            response = self.get(login_url, follow=True)
        return response

    def logout(self):
        self.get(reverse('accounts:logout'))


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


def get_or_create_user(email, defaults):
    user, created = EmailUser.objects.get_or_create(defaults=defaults, email=email)
    if created:
        UserSocialAuth.create_social_auth(user, user.email, 'email')
    return user, created


def create_random_user():
    return mixer.blend(EmailUser)


def create_random_customer():
    return create_random_user()


def get_or_create_default_customer():
    user, created = get_or_create_user(TestData.DEFAULT_CUSTOMER['email'], TestData.DEFAULT_CUSTOMER)
    return user


def get_or_create_default_officer():
    user, created = get_or_create_user(TestData.DEFAULT_OFFICER['email'], TestData.DEFAULT_OFFICER)
    if created:
        add_to_group(user, 'Officers')
    return user


def create_licence_type(code='regulation17'):
    return WildlifeLicenceType.objects.get_or_create(code=code)[0]


def get_or_create_default_assessor():
    user, created = get_or_create_user(TestData.DEFAULT_ASSESSOR['email'], TestData.DEFAULT_ASSESSOR)
    if created:
        add_to_group(user, 'Assessors')
    return user


def get_or_create_default_assessor_group():
    return AssessorGroup.objects.get_or_create(defaults=TestData.DEFAULT_ASSESSOR_GROUP,
                                               name=TestData.DEFAULT_ASSESSOR_GROUP['name'])[0]


def add_assessor_to_assessor_group(assessor, group):
    group.members.add(assessor)
    group.save()


def is_login_page(response):
    if hasattr(response, 'content'):
        content = response.content
    else:
        content = str(response)
    return content.find('<div id="wl-login-container">') > 0


def get_emails():
    return mail.outbox


def get_email():
    emails = get_emails()
    return emails[0] if len(emails) > 0 else None


def is_email():
    return len(get_emails()) > 0


def clear_mailbox():
    mail.outbox = []


def upload_id(user):
    with open(TestData.TEST_ID_PATH) as fp:
        post_params = {
            'identification_file': fp
        }
        client = SocialClient()
        client.login(user.email)
        response = client.post(reverse('main:identification'), post_params, follow=True)
        client.logout()
        return response


def clear_id_file(user):
    # clean id file
    if user.identification:
        os.remove(user.identification.path)


def clear_all_id_files():
    for user in EmailUser.objects.all():
        clear_id_file(user)


class HelpersTest(TestCase):
    def setUp(self):
        self.client = SocialClient()

    def test_create_default_customer(self):
        user = get_or_create_default_customer()
        self.assertIsNotNone(user)
        self.assertTrue(isinstance(user, EmailUser))
        self.assertEqual(TestData.DEFAULT_CUSTOMER['email'], user.email)
        self.assertTrue(accounts_helpers.is_customer(user))
        # test that we can login
        self.client.login(user.email)
        is_client_authenticated(self.client)

    def test_create_default_officer(self):
        user = get_or_create_default_officer()
        self.assertIsNotNone(user)
        self.assertTrue(isinstance(user, EmailUser))
        self.assertEqual(TestData.DEFAULT_OFFICER['email'], user.email)
        self.assertTrue(accounts_helpers.is_officer(user))
        # test that we can login
        self.client.login(user.email)
        is_client_authenticated(self.client)

    def test_create_default_assessor(self):
        user = get_or_create_default_assessor()
        self.assertIsNotNone(user)
        self.assertTrue(isinstance(user, EmailUser))
        self.assertEqual(TestData.DEFAULT_ASSESSOR['email'], user.email)
        self.assertTrue(accounts_helpers.is_assessor(user))
        # test that we can login
        self.client.login(user.email)
        is_client_authenticated(self.client)

    def create_random_user(self):
        user = create_random_user()
        self.assertIsNotNone(user)
        self.assertTrue(isinstance(user, EmailUser))
        self.assertEqual(TestData.DEFAULT_CUSTOMER['email'], user.email)
        # test that we can login
        self.client.login(user.email)
        is_client_authenticated(self.client)

    def create_random_customer(self):
        user = create_random_customer()
        self.assertIsNotNone(user)
        self.assertTrue(isinstance(user, EmailUser))
        self.assertEqual(TestData.DEFAULT_CUSTOMER['email'], user.email)
        self.assertTrue(accounts_helpers.is_customer(user))
        # test that we can login
        self.client.login(user.email)
        is_client_authenticated(self.client)


class TestClient(TestCase):
    def test_login_logout_login(self):
        user = get_or_create_default_customer()
        client = SocialClient()
        self.assertFalse(is_client_authenticated(client))
        client.login(user.email)
        self.assertTrue(is_client_authenticated(client))
        client.logout()
        self.assertFalse(is_client_authenticated(client))
        client.login(user.email)
        self.assertTrue(is_client_authenticated(client))
        self.assertEqual(unicode(user.pk), client.session.get('_auth_user_id'))
        client.logout()
        officer = get_or_create_default_officer()
        client.login(officer.email)
        self.assertTrue(is_client_authenticated(client))
        self.assertEqual(unicode(officer.pk), client.session.get('_auth_user_id'))
        client.logout()
        client.login(user.email)
        self.assertTrue(is_client_authenticated(client))
        self.assertEqual(unicode(user.pk), client.session.get('_auth_user_id'))
