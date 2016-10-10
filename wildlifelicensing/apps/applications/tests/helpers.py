from datetime import datetime

from django.test import TestCase
from django_dynamic_fixture import get as get_ddf

from django.core.urlresolvers import reverse, reverse_lazy

from ledger.accounts.models import Profile

from wildlifelicensing.apps.applications.views.entry import LICENCE_TYPE_NUM_CHARS, LODGEMENT_NUMBER_NUM_CHARS
from wildlifelicensing.apps.applications.models import Application, Assessment, Condition
from wildlifelicensing.apps.main.tests.helpers import create_random_customer, get_or_create_licence_type, \
    SocialClient, get_or_create_default_assessor_group, get_or_create_default_officer


def create_profile(user):
    return get_ddf(Profile, user=user)


def create_application(user=None, **kwargs):
    if user is None:
        user = create_random_customer()
    if 'applicant' not in kwargs:
        kwargs['applicant'] = user
    if 'applicant_profile' not in kwargs:
        kwargs['applicant_profile'] = create_profile(user)
    if 'licence_type' not in kwargs:
        kwargs['licence_type'] = get_or_create_licence_type()
    if 'data' not in kwargs:
        kwargs['data'] = {}
    application = get_ddf(Application, **kwargs)
    return application


def lodge_application(application):
    """
    :param application:
    """
    client = SocialClient()
    client.login(application.applicant.email)
    client.get(reverse('wl_applications:edit_application', args=[application.pk]))
    url = reverse_lazy('wl_applications:preview')
    client.post(url)
    application.refresh_from_db()
    client.logout()
    return application


def create_and_lodge_application(user=None, **kwargs):
    application = create_application(user, **kwargs)
    application.processing_status = 'new'
    application.customer_status = 'under_review'
    application.lodgement_sequence += 1
    application.lodgement_date = datetime.now().date()
    application.lodgement_number = '%s-%s' % (str(application.licence_type.pk).zfill(LICENCE_TYPE_NUM_CHARS),
                                              str(application.pk).zfill(LODGEMENT_NUMBER_NUM_CHARS))
    application.save()

    return application


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
                                               officer=get_or_create_default_officer())
    return assessment


def get_or_create_condition(code, defaults):
    return Condition.objects.get_or_create(code=code, defaults=defaults)[0]


class HelpersTest(TestCase):
    def test_create_profile(self):
        user = create_random_customer()
        profile = create_profile(user)
        self.assertIsNotNone(profile)
        self.assertEquals(user, profile.user)
        self.assertEquals(profile, user.profiles.first())

    def test_create_application(self):
        application = create_application()
        self.assertIsNotNone(application)
