from __future__ import unicode_literals
import re

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client


def is_client_authenticated(client):
    return '_auth_user_id' in client.session


def login(email, client=None):
    """
    Return a 'logged-in' django Client.
    :param email: the user email
    :param client:
    :return:
    """
    if client is None:
        client = Client()
    client.post(
        reverse('social:complete', kwargs={'backend': "email"}),
        {'email': email}
    )
    if len(mail.outbox) == 0:
        raise Exception("Email not received")
    else:
        login_url = re.search('(?P<url>https?://[^\s]+)', mail.outbox[0].body).group('url')
        client.get(login_url, follow=True)
    return client


def belongs_to(user, group_name):
    return user.groups.filter(name__iexact=group_name).exists()
