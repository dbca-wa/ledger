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
        Not an officer
    :param user:
    :return:
    """
    return not is_officer(user)


def is_officer(user):
    """
    Test if user is an WL Officer
    Rules:
        Must belongs to group Officers
    :param user:
    :return:
    """
    return belongs_to(user, 'Officers')


def get_all_officers():
    return EmailUser.objects.filter(groups__name='Officers')


def get_all_assessors():
    return EmailUser.objects.filter(groups__name='Assessors')
