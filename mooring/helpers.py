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
    return user.is_authenticated() and user.is_staff

def is_inventory(user):
    return user.is_authenticated() and belongs_to(user, "Mooring Inventory")

def is_admin(user):
    return user.is_authenticated() and belongs_to(user, "Mooring Admin")

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
    return EmailUser.objects.filter(is_staff=True)

def can_view_campground(user,campground):
    for g in campground.mooringareagroup_set.all():
        if user in g.members.all():
            return True
    return False
