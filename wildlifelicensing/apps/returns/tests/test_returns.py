import os
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from wildlifelicensing.apps.applications.tests import helpers as app_helpers
from wildlifelicensing.apps.main.tests.helpers import SocialClient, get_or_create_default_customer, \
    get_or_create_default_officer, create_licence, create_random_customer, get_or_create_default_assessor, \
    get_or_create_licence_type, clear_mailbox
from wildlifelicensing.apps.returns.models import Return
from wildlifelicensing.apps.returns.tests.helpers import create_return, get_or_create_return_type
from wildlifelicensing.apps.returns.utils import create_returns_due_dates

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
        allowed = [self.officer, self.not_allowed_customer, self.assessor, self.customer]
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


class TestLifeCycle(TestCase):
    fixtures = ['licences.json', 'countries.json', 'catalogue.json', 'partner.json', 'returns.json']

    def setUp(self):
        self.customer = get_or_create_default_customer(include_default_profile=True)
        self.officer = get_or_create_default_officer()
        self.assessor = get_or_create_default_assessor()
        self.not_allowed_customer = create_random_customer()
        self.assertNotEqual(self.not_allowed_customer, self.customer)

        self.client = SocialClient()
        self.licence_type = get_or_create_licence_type('regulation-17')
        self.return_type = get_or_create_return_type(self.licence_type)

    def tearDown(self):
        self.client.logout()

    def _issue_licence(self, licence_data, **kwargs):
        application = app_helpers.create_and_lodge_application(self.customer, **{
            'applicant': kwargs.get('applicant', self.customer),
            'licence_type': kwargs.get('licence_type', self.licence_type)
        })
        self.assertIsNotNone(application)
        self.assertEqual(application.applicant, self.customer)
        self.assertIsNone(application.proxy_applicant)
        licence = app_helpers.issue_licence(
            application,
            kwargs.get('issuer', self.officer),
            licence_data=licence_data
        )
        self.assertEqual(licence.holder, self.customer)
        self.assertIsNotNone(licence)
        return licence

    def _lodge_reg17_return(self, ret, data=None):
        post_params = {
            'lodge': True,
        }
        data = data or TEST_VALUES
        for key, value in data.items():
            post_params['regulation-17::{}'.format(key)] = value

        holder = ret.licence.holder
        self.client.login(holder.email)
        response = self.client.post(reverse('wl_returns:enter_return', args=(ret.pk,)), post_params)
        self.assertRedirects(response, reverse('home'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)
        ret.refresh_from_db()
        self.client.logout()
        return data

    def _create_and_lodge_return(self):
        start_date = date.today()
        end_date = start_date + relativedelta(months=2)  # 2 months licence
        licence_data = {
            'return_frequency': -1,  # one off
            'start_date': str(start_date),
            'end_date': str(end_date)
        }
        licence = self._issue_licence(licence_data)
        self.assertIsNotNone(licence)

        ret = Return.objects.first()
        expected_status = 'current'
        self.assertEqual(ret.status, expected_status)
        data = self._lodge_reg17_return(ret)
        expected_status = 'submitted'
        self.assertEqual(ret.status, expected_status)
        return ret, data

    def _create_lodge_and_amend_return(self):
        ret, data = self._create_and_lodge_return()
        expected_status = 'submitted'
        self.assertEqual(ret.status, expected_status)

        url = reverse('wl_returns:amendment_request')
        curator = self.officer
        self.client.login(curator.email)
        payload = {
            'ret': ret.pk,
            'officer': curator.pk,
            'reason': 'Chubby bat is not a valid species'
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        ret.refresh_from_db()
        expected_status = 'amendment_required'
        self.assertEqual(ret.status, expected_status)
        self.assertEqual(ret.pending_amendments_qs.count(), 1)
        self.client.logout()
        return ret

    def test_initial_states_with_future(self):
        """
        Test that after the licence has been created some returns has been created according to the return frequency
        and the licence end date
        """
        # issue licence
        # use a one year licence with a monthly return
        start_date = today = date.today()
        end_date = start_date + timedelta(days=365)
        licence_data = {
            'return_frequency': 1,
            'start_date': str(start_date),
            'end_date': str(end_date)
        }
        licence = self._issue_licence(licence_data)
        self.assertIsNotNone(licence)

        # 12 returns should have been created
        rets = Return.objects.all().order_by('due_date')
        self.assertEqual(rets.count(), 12)
        # the first one should be in a month with status 'current'
        current = rets.first()
        self.assertEqual(current.status, 'current')
        next_month = today + relativedelta(months=1)
        self.assertEqual(current.due_date, next_month)
        # the next ones should have the status 'future'
        futures = rets[1:]
        for i, future in enumerate(futures, start=1):
            self.assertEqual(future.status, 'future')
            expected_due_date = next_month + relativedelta(months=i)
            self.assertEqual(future.due_date, expected_due_date)

    def test_initial_one_off(self):
        """
        Test one off. One return due at the licence end date
        """
        start_date = date.today()
        end_date = start_date + relativedelta(months=2)  # 2 months licence
        licence_data = {
            'return_frequency': -1,  # one off
            'start_date': str(start_date),
            'end_date': str(end_date)
        }
        licence = self._issue_licence(licence_data)
        self.assertIsNotNone(licence)
        rets = Return.objects.all()
        self.assertEqual(rets.count(), 1)
        # the first one should be in a month with status 'current'
        current = rets.first()
        self.assertEqual(current.status, 'current')
        # due date should match the licence end date
        expected_due_date = end_date
        self.assertEqual(current.due_date, expected_due_date)

    def test_enter_return_happy_path(self):
        start_date = date.today()
        end_date = start_date + relativedelta(months=2)  # 2 months licence
        licence_data = {
            'return_frequency': -1,  # one off
            'start_date': str(start_date),
            'end_date': str(end_date)
        }
        licence = self._issue_licence(licence_data)
        self.assertIsNotNone(licence)

        ret = Return.objects.first()
        expected_status = 'current'
        self.assertEqual(ret.status, expected_status)
        self._lodge_reg17_return(ret)
        expected_status = 'submitted'
        self.assertEqual(ret.status, expected_status)

    def test_curate_happy_path(self):
        ret, data = self._create_and_lodge_return()
        expected_status = 'submitted'
        self.assertEqual(ret.status, expected_status)

        url = reverse('wl_returns:curate_return', args=(ret.pk,))
        curator = self.officer
        self.client.login(curator.email)

        # get method
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # the return data is in a 'tables' context (one per return type).
        ctx = response.context
        self.assertTrue('tables' in ctx)
        # this return (reg-17) has only one table.
        tables = ctx['tables']
        self.assertEqual(len(tables), 1)
        table = tables[0]
        self.assertIsInstance(table, dict)
        self.assertEqual(sorted(['headers', 'data', 'name', 'title']), sorted(table.keys()))

        # verify data
        sent_data = table['data']
        # should be a list of rows
        self.assertIsInstance(sent_data, list)
        # we expect only one row
        self.assertEqual(len(sent_data), 1)
        sent_first_row = sent_data[0]
        self.assertIsInstance(sent_first_row, dict)
        # the values should match what the customer submitted
        expected_data = TEST_VALUES
        for expected_key, expected_value in expected_data.items():
            self.assertTrue(expected_key in sent_first_row, "{} not in sent data".format(expected_key))
            # each returned 'cell' contains the value and an error
            sent_cell = sent_first_row.get(expected_key)
            self.assertTrue('value' in sent_cell)
            self.assertTrue('error' in sent_cell)
            sent_value = sent_cell.get('value')
            sent_error = sent_cell.get('error')
            # we don't expect any error
            self.assertIsNone(sent_error)
            # all sent values are string
            expected_value = str(expected_value)
            self.assertEqual(sent_value, expected_value)

        # post method
        # changed the species name
        new_species = 'Chubby bat'
        data = TEST_VALUES
        data['SPECIES_NAME'] = new_species
        payload = {
            'accept': True
        }
        for key, value in data.items():
            payload['regulation-17::{}'.format(key)] = value
        response = self.client.post(url, data=payload)
        self.assertRedirects(response, reverse('home'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)
        ret.refresh_from_db()
        expected_status = 'accepted'
        self.assertEqual(ret.status, expected_status)

        # check value
        data = ret.returntable_set.first().returnrow_set.first().data
        self.assertEqual(data.get('SPECIES_NAME'), new_species)

    def test_curate_request_amendments(self):
        """
        Test workflow when an officer requests a amendment to a return, especially the status change and verify that
        an email is sent to the user.
        """
        ret, data = self._create_and_lodge_return()
        expected_status = 'submitted'
        self.assertEqual(ret.status, expected_status)

        pending_amendments = ret.pending_amendments_qs
        self.assertEqual(pending_amendments.count(), 0)

        url = reverse('wl_returns:amendment_request')
        curator = self.officer
        self.client.login(curator.email)
        # important clear mailbox
        clear_mailbox()
        self.assertEqual(len(mail.outbox), 0)

        payload = {
            'ret': ret.pk,
            'officer': curator.pk,
            'reason': 'Chubby bat is not a valid species'
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        # expect a json response with the return amendment serialized
        resp_data = resp.json()
        self.assertTrue('amendment_request' in resp_data)
        # the reason should be returned
        self.assertEqual(resp_data['amendment_request'].get('reason'), payload['reason'])

        ret.refresh_from_db()
        expected_status = 'amendment_required'
        self.assertEqual(ret.status, expected_status)

        # we should have a pending amendment
        pending_amendments = ret.pending_amendments_qs
        self.assertEqual(pending_amendments.count(), 1)
        pending_amendment = pending_amendments.first()
        self.assertEqual(pending_amendment.status, 'requested')
        self.assertEqual(pending_amendment.officer, curator)
        self.assertEqual(pending_amendment.reason, payload['reason'])
        self.assertEqual(pending_amendment.ret, ret)

        # an email must have been sent to the applicant
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(len(email.to), 1)
        expected_address = ret.licence.profile.email
        self.assertEqual(email.to[0], expected_address)
        # the email body should contain a link to the edit return page
        # due to test environment we cannot use reverse or even host_reverse
        expected_url = "/returns/enter-return/{}".format(ret.pk)
        self.assertTrue(str(email.body).find(expected_url) > 0)

    def test_user_edit_after_amendments(self):
        """
        The user can edit and loge (amend) the return
        :return:
        """
        ret = self._create_lodge_and_amend_return()
        self._lodge_reg17_return(ret)
        expected_status = 'amended'
        self.assertEqual(ret.status, expected_status)
        self.assertEqual(ret.pending_amendments_qs.count(), 0)

    def test_curate_amended(self):
        """
        The officer can curate and accept an amended return
        :return:
        """
        # create/amend ...
        ret = self._create_lodge_and_amend_return()
        self._lodge_reg17_return(ret)
        expected_status = 'amended'
        self.assertEqual(ret.status, expected_status)
        self.assertEqual(ret.pending_amendments_qs.count(), 0)

        # officer curates: changed the species name
        url = reverse('wl_returns:curate_return', args=(ret.pk,))
        curator = self.officer
        self.client.login(curator.email)
        new_species = 'Chubby bat'
        data = TEST_VALUES
        data['SPECIES_NAME'] = new_species
        payload = {
            'accept': True
        }
        for key, value in data.items():
            payload['regulation-17::{}'.format(key)] = value
        response = self.client.post(url, data=payload)
        self.assertRedirects(response, reverse('home'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)
        ret.refresh_from_db()
        expected_status = 'accepted'
        self.assertEqual(ret.status, expected_status)

    def test_declined_amended(self):
        """
        Test decline an amended return
        """
        # create/amend ...
        ret = self._create_lodge_and_amend_return()
        self._lodge_reg17_return(ret)
        expected_status = 'amended'
        self.assertEqual(ret.status, expected_status)
        self.assertEqual(ret.pending_amendments_qs.count(), 0)

        url = reverse('wl_returns:curate_return', args=(ret.pk,))
        curator = self.officer
        self.client.login(curator.email)
        payload = {
            'decline': True
        }
        response = self.client.post(url, data=payload)
        self.assertRedirects(response, reverse('home'),
                             status_code=302, target_status_code=200, fetch_redirect_response=False)
        ret.refresh_from_db()
        expected_status = 'declined'
        self.assertEqual(ret.status, expected_status)


class TestUtils(TestCase):

    def test_create_returns_due_dates(self):
        # one year with 1 month period
        start_date = date(2017, 6, 30)
        end_date = date(2018, 6, 30)
        monthly_frequency = 1
        due_dates = create_returns_due_dates(start_date, end_date, monthly_frequency)
        expected_due_dates = [
            date(2017, 7, 30),
            date(2017, 8, 30),
            date(2017, 9, 30),
            date(2017, 10, 30),
            date(2017, 11, 30),
            date(2017, 12, 30),
            date(2018, 1, 30),
            date(2018, 2, 28),
            date(2018, 3, 30),
            date(2018, 4, 30),
            date(2018, 5, 30),
            date(2018, 6, 30)
        ]
        self.assertEqual(due_dates, expected_due_dates)

        # one year with 4 months period
        start_date = date(2017, 6, 30)
        end_date = date(2018, 6, 30)
        monthly_frequency = 4
        due_dates = create_returns_due_dates(start_date, end_date, monthly_frequency)
        expected_due_dates = [
            date(2017, 10, 30),
            date(2018, 2, 28),
            date(2018, 6, 30)
        ]
        self.assertEqual(due_dates, expected_due_dates)

        # two years with 6 months period
        start_date = date(2017, 6, 30)
        end_date = date(2019, 6, 30)
        monthly_frequency = 6
        due_dates = create_returns_due_dates(start_date, end_date, monthly_frequency)
        expected_due_dates = [
            date(2017, 12, 30),
            date(2018, 6, 30),
            date(2018, 12, 30),
            date(2019, 6, 30)
        ]
        self.assertEqual(due_dates, expected_due_dates)

        # case where monthly period exceed the end date, should return the end_date
        start_date = date(2017, 6, 30)
        end_date = date(2017, 7, 15)
        monthly_frequency = 1
        due_dates = create_returns_due_dates(start_date, end_date, monthly_frequency)
        expected_due_dates = [
            end_date,
        ]
        self.assertEqual(due_dates, expected_due_dates)

        # negative monthly frequency = one off
        start_date = date(2017, 6, 30)
        end_date = date(2019, 6, 30)
        monthly_frequency = -1
        due_dates = create_returns_due_dates(start_date, end_date, monthly_frequency)
        expected_due_dates = [
            end_date
        ]
        self.assertEqual(due_dates, expected_due_dates)
