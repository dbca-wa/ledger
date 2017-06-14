from __future__ import unicode_literals

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy

from wildlifelicensing.apps.main.helpers import is_customer, is_officer, is_assessor


class BaseAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    The main goal of this base mixin is to handle the 'no permission'.
    If the user is authenticated it should throw a PermissionDenied (status 403), but if the user is not authenticated
    it should return to the login page.
    """
    login_url = reverse_lazy('home')
    permission_denied_message = "You don't have the permission to access this resource."
    raise_exception = True

    def handle_no_permission(self):
        user = self.request.user
        if not user.is_authenticated():
            self.raise_exception = False
        return super(BaseAccessMixin, self).handle_no_permission()

    def test_func(self):
        """
        Override this method for access.
        Must return True if the current user can access the view.
        """
        return False


class CustomerRequiredMixin(BaseAccessMixin):
    """
    An AccessMixin that check for user being a customer.
    See rules in 'is_customer' function
    """

    def test_func(self):
        return is_customer(self.request.user)


class OfficerRequiredMixin(BaseAccessMixin):
    """
    An AccessMixin that check for user being a WL Officer.
    See rules in 'is_officer' function
    """

    def test_func(self):
        return is_officer(self.request.user)


class AssessorRequiredMixin(BaseAccessMixin):
    """
    An AccessMixin that check for user being a WL Assessor.
    See rules in 'is_assessor' function
    """

    def test_func(self):
        return is_assessor(self.request.user)


class OfficerOrCustomerRequiredMixin(BaseAccessMixin):
    """
    An AccessMixin that check for user being a WL Officer or a customer.
    See rules in 'is_officer' and 'is_customer' functions
    """

    def test_func(self):
        user = self.request.user
        return is_officer(user) or is_customer(user)


class OfficerOrAssessorRequiredMixin(BaseAccessMixin):
    """
    An AccessMixin that check for user being a WL Officer or WL Assessor.
    See rules in 'is_officer' and 'is_assessor' functions
    """

    def test_func(self):
        user = self.request.user
        return is_officer(user) or is_assessor(user)
