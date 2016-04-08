import os

from django.core.urlresolvers import reverse
from django.core.files import File
from django.test import TestCase
from social.apps.django_app.default.models import UserSocialAuth

from ledger.accounts.models import EmailUser, Document, Persona

from wildlifelicensing.apps.main.models import WildlifeLicenceType
from wildlifelicensing.apps.main.tests.helpers import SocialClient

TEST_ID_PATH = os.path.join('wildlifelicensing', 'apps', 'main', 'test_data', 'test_id.jpg')


class ApplicationEntryTestCase(TestCase):
    def setUp(self):
        self.customer = EmailUser.objects.create(email='customer@test.net')
        UserSocialAuth.create_social_auth(self.customer, self.customer.email, 'email')

        self.client = SocialClient()

        licence_type = WildlifeLicenceType.objects.get(code='regulation17')
        licence_type.identification_required = True
        licence_type.save()

    def test_select_licence_type(self):
        """Testing that a user can display the licence type selection list"""
        self.client.login(self.customer.email)

        # check that client can access the licence type selection list
        response = self.client.get(reverse('applications:select_licence_type'))
        self.assertEqual(200, response.status_code)

    def test_check_identification_required_no_current_id(self):
        """Testing that a user can display the identification required page in the case the user has no
        current identification, and upload an ID.
        """
        self.client.login(self.customer.email)

        # check that client can access the identification required page
        response = self.client.get(reverse('applications:check_identification', args=('regulation17',)))
        self.assertEqual(200, response.status_code)

        try:
            with open(TEST_ID_PATH) as fp:
                post_params = {
                    'identification_file': fp
                }
                response = self.client.post(reverse('applications:check_identification', args=('regulation17',)), post_params)

                self.assertRedirects(response, reverse('applications:create_select_persona', args=('regulation17',)),
                                     status_code=302, target_status_code=200, fetch_redirect_response=False)

                # update customer
                self.customer = EmailUser.objects.get(email=self.customer.email)

                # assert customer's ID is the uploaded file
                self.assertEqual(self.customer.identification.filename, 'test_id.jpg')
        finally:
            # remove uploaded file
            os.remove(self.customer.identification.path)

    def test_check_identification_required_current_id(self):
        """Testing that a user can display the identification required page in the case the user has a
        current identification.
        """
        self.client.login(self.customer.email)

        with open(TEST_ID_PATH) as fp:
            self.customer.identification =  Document.objects.create(name='test_id')
            self.customer.identification.file.save('test_id', File(fp), save=True)
            self.customer.save()

        # check that client can access the identification required page
        response = self.client.get(reverse('applications:check_identification', args=('regulation17',)))
        self.assertRedirects(response, reverse('applications:create_select_persona', args=('regulation17',)),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        os.remove(self.customer.identification.path)

    def test_create_select_persona(self):
        """Testing that a user can display the identification required page in the case the user has a
        current identification.
        """
        self.client.login(self.customer.email)

        # create the application dict in the session first
        # the session must be stored in a variable in order to be modifyable
        s = self.client.session
        s['application'] = {}
        s.save()

        # check that client can access the persona create/select page
        response = self.client.get(reverse('applications:create_select_persona', args=('regulation17',)))
        self.assertEqual(200, response.status_code)

