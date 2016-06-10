from __future__ import unicode_literals
from django.contrib.auth.mixins import UserPassesTestMixin

from wildlifelicensing.apps.main.helpers import is_customer, is_officer, is_assessor


class CustomerRequiredMixin(UserPassesTestMixin):
    """
    An AccessMixin that check for user being a customer.
    See rules in 'is_customer' function
    """

    def test_func(self):
        return is_customer(self.request.user)


class OfficerRequiredMixin(UserPassesTestMixin):
    """
    An AccessMixin that check for user being a WL Officer.
    See rules in 'is_officer' function
    """

    def test_func(self):
        return is_officer(self.request.user)


class AssessorRequiredMixin(UserPassesTestMixin):
    """
    An AccessMixin that check for user being a WL Assessor.
    See rules in 'is_assessor' function
    """

    def test_func(self):
        return is_assessor(self.request.user)


class OfficerOrCustomerRequiredMixin(UserPassesTestMixin):
    """
    An AccessMixin that check for user being a WL Officer or WL Assessor.
    See rules in 'is_officer' and 'is_customer' functions
    """

    def test_func(self):
        user = self.request.user
        return is_officer(user) or is_customer(user)


class OfficerOrAssessorRequiredMixin(UserPassesTestMixin):
    """
    An AccessMixin that check for user being a WL Officer or WL Assessor.
    See rules in 'is_officer' and 'is_assessor' functions
    """

    def test_func(self):
        user = self.request.user
        return is_officer(user) or is_assessor(user)
