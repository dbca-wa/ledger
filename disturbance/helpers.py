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


def is_officer(user):
    return user.is_authenticated() and (belongs_to(user, 'Disturbance Officers') or user.is_superuser)

def is_departmentUser(user):
    domain = user.email.split('@')[1]
    return user.is_authenticated() and (domain == 'dpaw.wa.gov.au' or domain == 'dbca.wa.gov.au')

def is_customer(user):
    """
    Test if the user is a customer
    Rules:
        Not an officer
    :param user:
    :return:
    """
    return user.is_authenticated() and not is_officer(user)


def get_all_officers():
    return EmailUser.objects.filter(groups__name='Disturbance Officers')
