from __future__ import unicode_literals
import re

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client
from django.contrib.auth.models import Group

from ledger.customers.models import Customer
from wildlifelicensing.apps.main import helpers as accounts_helpers


class TestData(object):
    DEFAULT_CUSTOMER = {
        'email': 'custromer@utest.com',
        'data': {
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
    }
    DEFAULT_OFFICER = {
        'email': 'officer@utest.com',
        'data': {}
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


def create_default_customer():
    client = SocialClient()
    client.login(TestData.DEFAULT_CUSTOMER['email'])
    response = client.post(reverse('accounts:customer_create'), data=TestData.DEFAULT_CUSTOMER['data'])
    customer = Customer.objects.filter(user__email=TestData.DEFAULT_CUSTOMER['email']).first()
    is_ok = customer is not None and (response.status_code == 200 or response.status_code == 302)
    if is_ok:
        return customer
    else:
        raise Exception("could not create the default customer")


def create_default_officer():
    data = TestData.DEFAULT_OFFICER
    client = SocialClient()
    response = client.login(data['email'])
    officer = add_to_group(response.context['user'], 'Officers')
    return officer
