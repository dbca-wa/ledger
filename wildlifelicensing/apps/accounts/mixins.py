from __future__ import unicode_literals
from braces.views import UserPassesTestMixin

from .models import Customer


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
        Must have a Customer object linked to this user
        and
        Must belong to group Customers
    :param user:
    :return:
    """
    return Customer.objects.filter(user=user).exists() and belongs_to(user, 'Customers')


def is_officer(user):
    """
    Test if user is an WL Officer
    Rules:
        Must belongs to group Officers
    :param user:
    :return:
    """
    return belongs_to(user, 'Officers')


class CustomerRequiredMixin(UserPassesTestMixin):
    """
    A Django braces Access mixin that check for user being a customer.
    See rules in 'is_customer' function
    """

    def test_func(self, user):
        return is_customer(user)


class OfficerRequiredMixin(UserPassesTestMixin):
    """
    A Django braces Access mixin that check for user being a WL Officer.
    See rules in 'is_officer' function
    """

    def test_func(self, user):
        return is_officer(user)
