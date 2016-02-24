from __future__ import unicode_literals
from braces.views import UserPassesTestMixin

from .helpers import is_customer, is_officer


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
