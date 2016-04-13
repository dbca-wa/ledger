from django.test import TestCase
from mixer.backend.django import mixer

from ledger.accounts.models import Profile
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.main.tests.helpers import create_user, create_random_customer


def create_random_profile(user):
    return mixer.blend(Profile, user=user)


def create_random_application(user=None, profile=None):
    if user is None:
        user = create_random_customer()
    if profile is None:
        profile = create_random_profile(user)
    data = {}
    application = mixer.blend(Application, applicant_profile=profile, data={})
    return application


class HelpersTest(TestCase):
    def test_create_profile(self):
        user = create_random_customer()
        profile = create_random_profile(user)
        self.assertIsNotNone(profile)
        self.assertEquals(user, profile.user)
        self.assertEquals(profile, user.profile_set.first())

    def test_create_application(self):
        application = create_random_application()
        self.assertIsNotNone(application)
