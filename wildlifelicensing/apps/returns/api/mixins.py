from django.contrib.auth.mixins import UserPassesTestMixin

from wildlifelicensing.apps.main.helpers import belongs_to


def is_api_user(user):
    return belongs_to(user, 'API') or user.is_superuser


class APIUserRequiredMixin(UserPassesTestMixin):
    """
    Mixin uses for API view.
    """
    # we don't want to be redirected to login page.
    raise_exception = True

    def test_func(self):
        return is_api_user(self.request.user)
