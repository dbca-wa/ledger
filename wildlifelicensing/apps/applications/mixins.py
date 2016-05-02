from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from wildlifelicensing.apps.applications.models import Application


class UserCanEditApplicationMixin(UserPassesTestMixin):
    """
    CBV mixin that check that the user is the applicant and that the status of the application is
    in editable mode.
    This mixin assume that the url contains the pk of the application on 2nd position.
    If the user is not logged-in it redirects to the login, else throw a 403
    """
    login_url = reverse_lazy('home')
    permission_denied_message = "You don't have the permission to access this resource."
    raise_exception = True

    def get_application(self):
        if len(self.args) > 1:
            return Application.objects.filter(pk=self.args[1]).first()
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
        self.raise_exception = True
        application = self.get_application()
        if application is not None:
            return application.applicant_profile.user == user and application.can_user_edit
        else:
            return True
