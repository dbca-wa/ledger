from __future__ import unicode_literals
from braces.views import UserPassesTestMixin

from .helpers import is_customer, is_officer, is_assessor


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


class AssessorRequiredMixin(UserPassesTestMixin):
    """
    A Django braces Access mixin that check for user being a WL Assessor.
    See rules in 'is_assessor' function
    """

    def test_func(self, user):
        return is_assessor(user)


class OfficerOrAssessorRequiredMixin(UserPassesTestMixin):
    """
    A Django braces Access mixin that check for user being a WL Assessor.
    See rules in 'is_assessor' function
    """

    def test_func(self, user):
        return is_officer(user) or is_assessor(user)
