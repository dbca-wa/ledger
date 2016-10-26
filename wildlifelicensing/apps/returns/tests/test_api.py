from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status

from wildlifelicensing.apps.returns.models import ReturnType
from wildlifelicensing.apps.main.tests import helpers
from wildlifelicensing.apps.returns.api.mixins import is_api_user


class TestExplorerView(TestCase):
    fixtures = [
        'countries',
        'groups',
        'licences',
        'conditions',
        'default-conditions',
        'returns'
    ]

    def test_authorisation(self):
        """
        Only superuser or API users
        :return:
        """
        url = reverse("wl_returns:api:explorer")
        customer = helpers.get_or_create_default_customer()
        officer = helpers.get_or_create_default_officer()
        assessor = helpers.get_or_create_default_assessor()

        api_user = helpers.get_or_create_api_user()
        self.assertTrue(is_api_user(api_user))

        admin = helpers.create_random_customer()
        admin.is_superuser = True
        admin.save()
        self.assertTrue(is_api_user(admin))

        client = helpers.SocialClient()
        forbidden = [customer, officer, assessor]
        for user in forbidden:
            client.login(user.email)
            self.assertEqual(client.get(url).status_code,
                             status.HTTP_403_FORBIDDEN)
            client.logout()

        allowed = [admin, api_user]
        for user in allowed:
            client.login(user.email)
            self.assertEqual(client.get(url).status_code,
                             status.HTTP_200_OK)
            client.logout()


class TestDataView(TestCase):
    fixtures = [
        'countries',
        'groups',
        'licences',
        'conditions',
        'default-conditions',
        'returns'
    ]

    def setUp(self):
        # should have at least on return type
        self.return_type = ReturnType.objects.first()
        self.assertIsNotNone(self.return_type)

    def test_authorisation(self):
        """
        Only superuser or API users
        :return:
        """
        url = reverse("wl_returns:api:data", kwargs={
            'return_type_pk': self.return_type.pk,
            'resource_number': 0
        })
        customer = helpers.get_or_create_default_customer()
        officer = helpers.get_or_create_default_officer()
        assessor = helpers.get_or_create_default_assessor()

        api_user = helpers.get_or_create_api_user()
        self.assertTrue(is_api_user(api_user))

        admin = helpers.create_random_customer()
        admin.is_superuser = True
        admin.save()
        self.assertTrue(is_api_user(admin))

        client = helpers.SocialClient()
        forbidden = [customer, officer, assessor]
        for user in forbidden:
            client.login(user.email)
            self.assertEqual(client.get(url).status_code,
                             status.HTTP_403_FORBIDDEN)
            client.logout()

        allowed = [admin, api_user]
        for user in allowed:
            client.login(user.email)
            self.assertEqual(client.get(url).status_code,
                             status.HTTP_200_OK)
            client.logout()
