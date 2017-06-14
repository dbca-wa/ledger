from __future__ import unicode_literals

import os
import datetime
import re

from rest_framework import status

from django.contrib.auth.models import Group
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.utils.encoding import smart_text
from django.contrib.messages import constants as message_constants
from django_dynamic_fixture import G

from ledger.accounts.models import EmailUser, Profile, Address, Country
from wildlifelicensing.apps.main import helpers as accounts_helpers
from wildlifelicensing.apps.main.models import WildlifeLicenceType, WildlifeLicence, AssessorGroup


class TestData(object):
    TEST_ID_PATH = os.path.join('wildlifelicensing', 'apps', 'main', 'test_data', 'test_id.jpg')

    DEFAULT_CUSTOMER = {
        'email': 'customer@test.com',
        'first_name': 'Homer',
        'last_name': 'Cust',
        'dob': datetime.date(1989, 8, 12),
    }
    DEFAULT_PROFILE = {
        'email': 'customer@test.com',
    }
    DEFAULT_ADDRESS = {
        'line1': '1 Test Street',
        'locality': 'Testland',
        'postcode': '7777',
    }
    DEFAULT_OFFICER = {
        'email': 'officer@test.com',
        'first_name': 'Offy',
        'last_name': 'Sir',
        'dob': datetime.date(1979, 12, 13),
    }
    DEFAULT_ASSESSOR = {
        'email': 'assessor@test.com',
        'first_name': 'Assess',
        'last_name': 'Ore',
        'dob': datetime.date(1979, 10, 5),
    }
    DEFAULT_ASSESSOR_GROUP = {
        'name': 'ass group',
        'email': 'assessor@test.com',
    }
    DEFAULT_API_USER = {
        'email': 'apir@test.com',
        'first_name': 'api',
        'last_name': 'user',
        'dob': '1979-12-13',
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
            clear_mailbox()
        return response

    def logout(self):
        self.get(reverse('accounts:logout'))


def create_default_country():
    return G(Country, iso_3166_1_a2='AU')


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


def get_or_create_user(params):
    user, created = EmailUser.objects.get_or_create(**params)
    return user, created


def create_random_user():
    return G(EmailUser, dob='1970-01-01')


def create_random_customer():
    return create_random_user()


def get_or_create_default_customer(include_default_profile=False):
    user, created = get_or_create_user(TestData.DEFAULT_CUSTOMER)

    if include_default_profile:
        create_default_country()
        address = Address.objects.create(user=user, **TestData.DEFAULT_ADDRESS)
        profile = Profile.objects.create(user=user, postal_address=address, **TestData.DEFAULT_PROFILE)
        profile.user = user

    return user


def get_or_create_default_officer():
    user, created = get_or_create_user(TestData.DEFAULT_OFFICER)
    if created:
        add_to_group(user, 'Officers')
    return user


def get_or_create_api_user():
    user, created = get_or_create_user(TestData.DEFAULT_API_USER)
    if created:
        add_to_group(user, 'API')
    return user


def get_or_create_licence_type(product_title='regulation-17'):
    return WildlifeLicenceType.objects.get_or_create(product_title=product_title)[0]


def create_licence(holder, issuer, product_title='regulation-17'):
    licence_type = get_or_create_licence_type(product_title)
    return WildlifeLicence.objects.create(licence_type=licence_type, holder=holder, issuer=issuer,
                                          profile=holder.profiles.first())


def get_or_create_default_assessor():
    user, created = get_or_create_user(TestData.DEFAULT_ASSESSOR)
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
        content = smart_text(response)
    return content.find(b'<div id="wl-login-container">') > 0


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
    with open(TestData.TEST_ID_PATH, 'rb') as fp:
        post_params = {
            'identification': True,
            'identification_file': fp
        }
        client = SocialClient()
        client.login(user.email)
        response = client.post(reverse('wl_main:identification'), post_params, follow=True)
        client.logout()
        return response


def clear_id_file(user):
    if user.identification:
        os.remove(user.identification.path)


def clear_all_id_files():
    for user in EmailUser.objects.all():
        clear_id_file(user)


def get_user_home_url(user):
    if accounts_helpers.is_officer(user):
        return '/dashboard/officer'
    elif accounts_helpers.is_assessor(user):
        return '/dashboard/tables/assessor'

    return '/dashboard/tables/customer'


def get_response_messages(response):
    if 'messages' in response.context:
        return list(response.context['messages'])
    return []


def has_response_messages(response):
    return len(get_response_messages(response)) > 0


def get_response_error_messages(response):
    return [m for m in get_response_messages(response) if m.level == message_constants.ERROR]


def has_response_error_messages(response):
    return len(get_response_error_messages(response)) > 0


class BaseUserTestCase(TestCase):
    """
    A test case that provides some users
    """
    client_class = SocialClient

    def _pre_setup(self):
        super(BaseUserTestCase, self)._pre_setup()
        self.customer = get_or_create_default_customer(include_default_profile=True)
        self.officer = get_or_create_default_officer()
        self.assessor = get_or_create_default_assessor()
        self.all_users = [
            self.officer,
            self.assessor,
            self.customer
        ]

    def _post_teardown(self):
        super(BaseUserTestCase, self)._post_teardown()
        self.client.logout()


class BasePermissionViewTestCase(BaseUserTestCase):
    view_url = None

    @property
    def permissions(self):
        """
        Override this method to define permissions for relevant method.
        Example:
        {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
                'kwargs': {}
            }
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor]
                'kwargs': {
                    'data': {}
                }
            },
        }
        Note: the kwargs are passed to the request method. Useful for post data
        """
        return None

    def test_permissions(self):
        if not self.view_url:
            return
        permissions = self.permissions or {}
        verbs = ['get', 'post', 'put', 'patch', 'delete']
        for verb in verbs:
            method = getattr(self.client, verb)
            if callable(method):
                if verb in permissions:
                    allowed = permissions[verb].get('allowed', [])
                    forbidden = permissions[verb].get('forbidden', self.all_users)
                    kwargs = permissions[verb].get('kwargs', {})
                    for user in allowed:
                        self.client.login(user.email)
                        response = method(self.view_url, **kwargs)
                        expected_status = status.HTTP_200_OK
                        self.assertEqual(
                            response.status_code, expected_status,
                            msg="{got} != {expected} for user {user} with method {verb} at {url} with params {kwargs}".format(
                                got=response.status_code,
                                expected=expected_status,
                                user=user.email,
                                verb=verb,
                                url=self.view_url,
                                kwargs=kwargs,
                            )
                        )
                        self.client.logout()

                    for user in forbidden:
                        self.client.login(user.email)
                        response = method(self.view_url, **kwargs)
                        expected_status = status.HTTP_403_FORBIDDEN
                        self.assertEqual(
                            response.status_code, expected_status,
                            msg="{got} != {expected} for user {user} with method {verb} at {url} with params {kwargs}".format(
                                got=response.status_code,
                                expected=expected_status,
                                user=user.email,
                                verb=verb,
                                url=self.view_url,
                                kwargs=kwargs,
                            )
                        )
                        self.client.logout()
                else:
                    # method not in the permissions list should return 405 (or 403)
                    for user in self.all_users:
                        self.client.login(user.email)
                        response = method(self.view_url, **kwargs)
                        expected_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
                        self.assertIn(
                            response.status_code, expected_statuses,
                            msg="{got} != {expected} for user {user} with method {verb} at {url} with params {kwargs}".format(
                                got=response.status_code,
                                expected=expected_statuses,
                                user=user.email,
                                verb=verb,
                                url=self.view_url,
                                kwargs=kwargs,
                            )
                        )
                        self.client.logout()
            else:
                self.fail('Method {} is not supported by client.'.format(verb))


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
        self.assertEqual(smart_text(user.pk), client.session.get('_auth_user_id'))
        client.logout()
        officer = get_or_create_default_officer()
        client.login(officer.email)
        self.assertTrue(is_client_authenticated(client))
        self.assertEqual(smart_text(officer.pk), client.session.get('_auth_user_id'))
        client.logout()
        client.login(user.email)
        self.assertTrue(is_client_authenticated(client))
        self.assertEqual(smart_text(user.pk), client.session.get('_auth_user_id'))
