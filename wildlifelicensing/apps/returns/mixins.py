from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

from wildlifelicensing.apps.main.helpers import is_officer
from wildlifelicensing.apps.returns.models import Return


class UserCanEditReturnMixin(UserPassesTestMixin):
    """
    CBV mixin that check that the user is the applicant and that the status of the application is
    in editable mode.
    This mixin assume that the url contains the pk of the application on 2nd position.
    If the user is not logged-in it redirects to the login page, else it throws a 403
    Officers can edit an application
    """
    login_url = reverse_lazy('home')
    permission_denied_message = "You don't have the permission to access this resource."
    raise_exception = True

    def get_return(self):
        if len(self.args) > 1:
            return Return.objects.filter(pk=self.args[1]).first()
        else:
            return None

    def test_func(self):
        """
        implementation of the UserPassesTestMixin test_func
        """
        user = self.request.user
        if not user.is_authenticated():
            self.raise_exception = False
            return False
        if is_officer(user):
            return True
        self.raise_exception = True
        ret = self.get_return()
        if ret is not None:
            return ret.licence.holder == user and ret.can_user_edit
        else:
            return True
