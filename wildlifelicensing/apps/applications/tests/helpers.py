from datetime import datetime, date, timedelta

from django.test import TestCase
from django_dynamic_fixture import G

from django.core.urlresolvers import reverse, reverse_lazy

from ledger.accounts.models import Profile, Address

from wildlifelicensing.apps.applications.views.entry import LICENCE_TYPE_NUM_CHARS, LODGEMENT_NUMBER_NUM_CHARS
from wildlifelicensing.apps.applications.models import Application, Assessment, Condition
from wildlifelicensing.apps.main.tests.helpers import create_random_customer, get_or_create_licence_type, \
    SocialClient, get_or_create_default_assessor_group, get_or_create_default_officer, create_default_country
from wildlifelicensing.apps.main.models import Region


def create_profile(user):
    create_default_country()
    address = G(Address, user=user, country='AU')
    return G(Profile, adress=address, user=user)


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
    application = G(Application, **kwargs)
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


def issue_licence(application=None, user=None, licence_data=None):
    if application is None:
        application = create_and_lodge_application(user)
    if user is None:
        user = get_or_create_default_officer()
    client = SocialClient()
    client.login(user.email)
    if licence_data is None:
        licence_data = {}
    data = get_minimum_data_for_issuing_licence()
    data.update(licence_data)
    url = reverse('wl_applications:issue_licence', args=[application.pk])
    client.post(url, data=data, follow=True)
    client.logout()
    application.refresh_from_db()
    assert application.licence
    return application.licence


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


def set_application_session(client, application):
    session = client.session
    session['application_id'] = application.pk
    session.save()


def delete_application_session(client):
    session = client.session
    del session['application_id']
    session.save()


def get_minimum_data_for_issuing_licence():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    return {
        'regions': [G(Region).pk],
        'return_frequency': -1,
        'issue_date': str(today),
        'start_date': str(today),
        'end_date': str(tomorrow)
    }


def get_communication_log(application):
    client = SocialClient()
    officer = get_or_create_default_officer()
    client.login(officer.email)
    url = reverse('wl_applications:log_list', args=[application.pk])
    resp = client.get(url)
    client.logout()
    return resp.json()['data']


def get_action_log(application):
    client = SocialClient()
    officer = get_or_create_default_officer()
    client.login(officer.email)
    url = reverse('wl_applications:action_list', args=[application.pk])
    resp = client.get(url)
    client.logout()
    return resp.json()['data']


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

    def test_communication_log(self):
        application = create_and_lodge_application()
        comm_log = get_communication_log(application)
        self.assertIsNotNone(comm_log)
        self.assertIsInstance(comm_log, list)

    def test_action_log(self):
        application = create_and_lodge_application()
        action_log = get_action_log(application)
        self.assertIsNotNone(action_log)
        self.assertIsInstance(action_log, list)
