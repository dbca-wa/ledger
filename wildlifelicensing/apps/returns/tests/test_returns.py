import os

from django.core.urlresolvers import reverse
from django.test import TestCase

from wildlifelicensing.apps.main.tests.helpers import SocialClient, get_or_create_default_customer, \
    get_or_create_default_officer, create_licence
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

        self.licence = create_licence(self.customer, self.officer, product_code='regulation-17')
        self.ret = create_return(self.licence)

    def tearDown(self):
        self.client.logout()

    def test_returns_lodgement_page(self):
        """Testing that a user can access the returns lodgement page"""

        self.client.login(self.customer.email)

        # check that client can access the licence type selection list
        response = self.client.get(reverse('wl_returns:enter_return', args=(self.ret.pk,)))
        self.assertEqual(200, response.status_code)

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
        for key, value in response.context['tables'][0]['data'][0].iteritems():
            self.assertEqual(value['value'], TEST_VALUES[key])

    def test_lodge_return(self):
        """Testing that a user can lodge a return"""
        self.client.login(self.customer.email)

        # check return status is intially 'current'
        self.assertEqual(self.ret.status, 'current')

        post_params = {
            'lodge': True,
        }

        for key, value in TEST_VALUES.iteritems():
            post_params['regulation-17::{}'.format(key)] = value

        response = self.client.post(reverse('wl_returns:enter_return', args=(self.ret.pk,)), post_params)

        self.assertRedirects(response, reverse('home'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)

        self.ret.refresh_from_db()

        # check return status is 'submitted'
        self.assertEqual(self.ret.status, 'submitted')

        # assert values in the return is what is expected
        for key, value in self.ret.returntable_set.first().returnrow_set.first().data.iteritems():
            self.assertEqual(value, unicode(TEST_VALUES[key]))
