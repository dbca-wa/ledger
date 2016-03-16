from __future__ import unicode_literals
from ledger.accounts.models import EmailUser


def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    return user.groups.filter(name=group_name).exists()


def is_customer(user):
    """
    Test if the user is a customer
    Rules:
        Must have a EmailUser object linked to this user
        and
        Must belong to group Customers
    :param user:
    :return:
    """
    return EmailUser.objects.filter(user=user).exists() and belongs_to(user, 'Customers')


def is_officer(user):
    """
    Test if user is an WL Officer
    Rules:
        Must belongs to group Officers
    :param user:
    :return:
    """
    return belongs_to(user, 'Officers')
