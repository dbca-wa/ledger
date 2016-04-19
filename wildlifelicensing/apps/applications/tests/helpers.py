from django.test import TestCase
from mixer.backend.django import mixer

from ledger.accounts.models import Profile
from ledger.licence.models import LicenceType
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.main.tests.helpers import create_user, create_random_customer, create_licence_type


def create_profile(user):
    return mixer.blend(Profile, user=user)


def create_application(user=None, **kwargs):
    if 'applicant_profile' not in kwargs:
        if user is None:
            user = create_random_customer()
        kwargs['applicant_profile'] = create_profile(user)
    if 'licence_type' not in kwargs:
        kwargs['licence_type'] = create_licence_type()
    if 'data' not in kwargs:
        kwargs['data'] = {}
    application = mixer.blend(Application, **kwargs)
    return application


class HelpersTest(TestCase):
    def test_create_profile(self):
        user = create_random_customer()
        profile = create_profile(user)
        self.assertIsNotNone(profile)
        self.assertEquals(user, profile.user)
        self.assertEquals(profile, user.profile_set.first())

    def test_create_application(self):
        application = create_application()
        self.assertIsNotNone(application)
