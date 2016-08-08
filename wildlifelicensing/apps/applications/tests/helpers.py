from datetime import date

from django.test import TestCase
from mixer.backend.django import mixer

from django.core.urlresolvers import reverse_lazy

from ledger.accounts.models import Profile

from wildlifelicensing.apps.applications.models import Application, Assessment, Condition, AssessmentCondition
from wildlifelicensing.apps.main.tests.helpers import create_random_customer, create_licence_type, \
    SocialClient, get_or_create_default_assessor_group, get_or_create_default_officer


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


def lodge_application(application):
    """
    :param application:
    """
    client = SocialClient()
    client.login(application.applicant_profile.user.email)
    url = reverse_lazy('wl_applications:preview', args=[application.licence_type.code_slug, application.pk])
    session = client.session
    session['application'] = {
        'profile': application.applicant_profile.pk,
        'data': application.data
    }
    session.save()
    client.post(url)
    application.refresh_from_db()
    client.logout()
    return application


def create_and_lodge_application(user=None, **kwargs):
    return lodge_application(create_application(user, **kwargs))


def get_or_create_assessment(application):
    """
    First assessment for the given application or create one
    :param application:
    :return:
    """
    group = get_or_create_default_assessor_group()
    assessment = Assessment.objects.filter(application=application).first()
    if assessment is None:
        assessment = Assessment.objects.create(application=application, assessor_group=group,
                                               officer=get_or_create_default_officer(), date_last_reminded=date.today())
    return assessment


def get_or_create_condition(code, defaults):
    return Condition.objects.get_or_create(code=code, defaults=defaults)[0]


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
