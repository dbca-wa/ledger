import os

from django.core.urlresolvers import reverse
from django.test import TestCase

from wildlifelicensing.apps.main.tests.helpers import SocialClient, get_or_create_default_customer, \
    get_or_create_default_officer, create_licence, create_random_customer, get_or_create_default_assessor
from wildlifelicensing.apps.returns.tests.helpers import create_return

TEST_SPREADSHEET_PATH = os.path.join('wildlifelicensing', 'apps', 'returns', 'test_data', 'regulation17.xlsx')

TEST_VALUES = {
    'LOCATION': 'Test Location',
    'SITE': 'Test Site',
    'DATUM': 'WSG84',
    'LATITUDE': 35,
    'LONGITUDE': -45,
    'ZONE': 'Danger',
    'EASTING': 2,
    'NORTHING': 3,
    'ACCURACY': 'Very',
    'DATE': 'Today',
    'NAME_ID': 'Bird',
    'SPECIES_NAME': 'Biggus bird',
    'COMMON_NAME': 'Big Bird',
    'SPECIES_GROUP': 'Birds',
    'COUNT': 1,
    'IDENTIFIER': 'Colour',
    'CERTAINTY': 'Very',
    'METHOD': 'Trap',
    'FATE': 'School',
    'SAMPLES': 'None',
    'MARKING': 'None',
    'TRANSMITTER': 'Radio',
    'VOUCHER_REF': 'Free Whopper'
}


class ReturnsTestCase(TestCase):
    fixtures = ['licences.json', 'countries.json', 'catalogue.json', 'partner.json', 'returns.json']

    def setUp(self):
        self.customer = get_or_create_default_customer(include_default_profile=True)
        self.officer = get_or_create_default_officer()

        self.client = SocialClient()

        self.licence = create_licence(self.customer, self.officer, product_title='regulation-17')
        self.ret = create_return(self.licence)

    def tearDown(self):
        self.client.logout()

    def test_lodge_nil_return(self):
        """Testing that a user can log a nil return"""

        self.client.login(self.customer.email)

        post_params = {
            'nil': True,
            'comments': 'No survey taken'
        }
        response = self.client.post(reverse('wl_returns:enter_return', args=(self.ret.pk,)),
                                    post_params)

        self.assertRedirects(response, reverse('home'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

    def test_upload_return_spreadsheet(self):
        """Testing that a user can upload a return spreadsheet"""

        self.client.login(self.customer.email)

        with open(TEST_SPREADSHEET_PATH, 'rb') as fp:
            post_params = {
                'upload': True,
                'spreadsheet_file': fp
            }
            response = self.client.post(reverse('wl_returns:enter_return', args=(self.ret.pk,)),
                                        post_params)

        self.assertEqual(200, response.status_code)

        # assert values in the response context match those in the spreadsheet
        for key, value in response.context['tables'][0]['data'][0].items():
            self.assertEqual(value['value'], TEST_VALUES[key])

    def test_lodge_return(self):
        """Testing that a user can lodge a return"""
        self.client.login(self.customer.email)

        # check return status is intially 'current'
        self.assertEqual(self.ret.status, 'current')

        post_params = {
            'lodge': True,
        }

        for key, value in TEST_VALUES.items():
            post_params['regulation-17::{}'.format(key)] = value

        response = self.client.post(reverse('wl_returns:enter_return', args=(self.ret.pk,)), post_params)

        self.assertRedirects(response, reverse('home'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        self.ret.refresh_from_db()

        # check return status is 'submitted'
        self.assertEqual(self.ret.status, 'submitted')

        # assert values in the return is what is expected
        for key, value in self.ret.returntable_set.first().returnrow_set.first().data.items():
            self.assertEqual(value, str(TEST_VALUES[key]))


class TestPermissions(TestCase):
    fixtures = ['licences.json', 'countries.json', 'catalogue.json', 'partner.json', 'returns.json']

    def setUp(self):
        self.customer = get_or_create_default_customer(include_default_profile=True)
        self.officer = get_or_create_default_officer()
        self.assessor = get_or_create_default_assessor()
        self.not_allowed_customer = create_random_customer()
        self.assertNotEqual(self.not_allowed_customer, self.customer)

        self.client = SocialClient()
        self.licence = create_licence(self.customer, self.officer, product_title='regulation-17')
        self.ret = create_return(self.licence)

    def test_returns_lodgement_page(self):
        """
        Only officer or application owner can view returns
        """
        url = reverse('wl_returns:enter_return', args=(self.ret.pk,))
        allowed = [self.officer, self.customer]
        forbidden = [self.not_allowed_customer, self.assessor]

        for user in allowed:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
            self.client.logout()

        for user in forbidden:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(403, response.status_code)
            self.client.logout()

    def test_readonly_view(self):
        """
        Only officer or application owner can enter returns
        """
        url = reverse('wl_returns:view_return', args=(self.ret.pk,))
        allowed = [self.officer, self.customer]
        forbidden = [self.not_allowed_customer, self.assessor]

        for user in allowed:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
            self.client.logout()

        for user in forbidden:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(403, response.status_code)
            self.client.logout()

    def test_curate_view(self):
        """
        Only officer can curate returns
        """
        url = reverse('wl_returns:curate_return', args=(self.ret.pk,))
        allowed = [self.officer]
        forbidden = [self.not_allowed_customer, self.assessor, self.customer]

        for user in allowed:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
            self.client.logout()

        for user in forbidden:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(403, response.status_code)
            self.client.logout()

    def test_view_log(self):
        """
        Only officer can view log
        """
        url = reverse('wl_returns:log_list', args=(self.ret.pk,))
        allowed = [self.officer]
        forbidden = [self.not_allowed_customer, self.assessor, self.customer]

        for user in allowed:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
            self.client.logout()

        for user in forbidden:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(403, response.status_code)
            self.client.logout()

    def test_add_log(self):
        """
        Only officer can view log
        """
        url = reverse('wl_returns:add_log_entry', args=(self.ret.pk,))
        allowed = [self.officer]
        forbidden = [self.not_allowed_customer, self.assessor, self.customer]

        payload = {
            'to': 'user',
            'from': 'test',
            'type': 'email'
        }
        for user in allowed:
            self.client.login(user.email)
            response = self.client.post(url, data=payload)
            self.assertEqual(200, response.status_code)
            self.client.logout()

        for user in forbidden:
            self.client.login(user.email)
            response = self.client.post(url, data=payload)
            self.assertEqual(403, response.status_code)
            self.client.logout()

    def test_download_template(self):
        """
        Every authenticated user should be able to download a return template
        """
        return_type = self.ret.return_type
        url = reverse('wl_returns:download_return_template', args=(return_type.pk,))
        allowed = [self.officer,self.not_allowed_customer, self.assessor, self.customer]
        forbidden = []

        for user in allowed:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
            self.client.logout()

        for user in forbidden:
            self.client.login(user.email)
            response = self.client.get(url)
            self.assertEqual(403, response.status_code)
            self.client.logout()
