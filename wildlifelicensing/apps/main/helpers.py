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
    return user.is_authenticated() and not is_officer(user) and not is_assessor(user)


def is_officer(user):
    """
    Test if user is an WL Officer
    Rules:
        Must belongs to group Officers
    :param user:
    :return:
    """
    return belongs_to(user, 'Officers')


def is_assessor(user):
    """
    Test if user is an WL Assessors
    Rules:
        Must belongs to group Assessors
    :param user:
    :return:
    """
    return belongs_to(user, 'Assessors')


def get_all_officers():
    return EmailUser.objects.filter(groups__name='Officers')


def get_all_assessors():
    return EmailUser.objects.filter(groups__name='Assessors')


def get_user_assessor_groups(user):
    return user.assessorgroup_set.all()

def render_user_name(user, first_name_first=True):
    """
    Last name, Given name(s) or Last name, Given name(s) or just email if there are no given or last name
    :param first_name_first:
    :param user:
    :return:
    """
    result = ''
    if user is not None:
        if user.last_name or user.first_name:
            format_ = u'{first} {last}' if first_name_first else '{last}, {first}'
            result = format_.format(
                first=user.first_name,
                last=user.last_name
            )
        else:
            result = '{email}'.format(
                email=user.email
            )
    return result
