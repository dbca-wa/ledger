from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

from wildlifelicensing.apps.main.helpers import is_officer
from wildlifelicensing.apps.main.mixins import BaseAccessMixin
from wildlifelicensing.apps.returns.models import Return


class UserCanEditReturnMixin(BaseAccessMixin):
    """
    CBV mixin that check that the user is the applicant and that the status of the return is
    in editable mode.
    Officers can edit a return
    """
    def get_return(self):
        if self.args:
            return Return.objects.filter(pk=self.args[0]).first()
        else:
            return None

    def test_func(self):
        """
        implementation of the UserPassesTestMixin test_func
        """
        user = self.request.user
        if is_officer(user):
            return True
        ret = self.get_return()
        if ret is not None:
            return ret.licence.holder == user and ret.can_user_edit
        else:
            return True


class UserCanViewReturnMixin(BaseAccessMixin):
    """
    Applicant + officer can view the return in read only mode
    """

    def get_return(self):
        if self.args:
            return Return.objects.filter(pk=self.args[0]).first()
        else:
            return None

    def test_func(self):
        """
        implementation of the UserPassesTestMixin test_func
        """
        user = self.request.user
        if is_officer(user):
            return True
        ret = self.get_return()
        if ret is not None:
            return ret.licence.holder == user
        else:
            return True


class UserCanCurateReturnMixin(BaseAccessMixin):
    """
    Only officer
    """

    def test_func(self):
        """
        implementation of the UserPassesTestMixin test_func
        """
        user = self.request.user
        return is_officer(user)


