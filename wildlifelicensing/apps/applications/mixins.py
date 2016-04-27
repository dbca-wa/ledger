from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from wildlifelicensing.apps.main.helpers import is_officer, is_assessor
from wildlifelicensing.apps.applications.models import Application


class UserCanEditApplicationMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    CBV mixin that check that the user is the applicant and that the status of the application is
    in editable mode.
    This mixin assume that the url contains the pk of the application.
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
        application = self.get_application()
        if application is not None:
            return application.applicant_profile.user == user and application.customer_status in ['draft',
                                                                                                  'amendment_required']
        else:
            return True
