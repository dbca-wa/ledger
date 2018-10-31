# -*- coding: utf8 -*-

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import Group
from django.core import mail
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.test import TransactionTestCase, TestCase, Client

from ledger.accounts.models import EmailUser, Country

from parkstay import utils, models as ps
from parkstay.exceptions import BookingRangeWithinException

import mock
import json
import itertools

import datetime
from decimal import Decimal as D
import re

class SocialClient(Client):
    """
    A django Client for authenticating with the social auth password-less framework.
    """

    def login(self, email):
        # important clear the mail box before
        mail.outbox = []
        self.post(reverse('social:complete', kwargs={'backend': "email"}), {'email': email})
        if len(mail.outbox) == 0:
            raise Exception("Email not received")
        else:
            login_url = re.search('(?P<url>https?://[^\s]+)', mail.outbox[0].body).group('url')
            response = self.get(login_url, follow=True)
            mail.outbox = []
        return response

    def logout(self):
        self.get(reverse('accounts:logout'))


ADMIN_USER_EMAIL = 'admin@test.net'
NEW_USER_EMAIL = 'new_user@test.net'
ANONYMOUS_USER_EMAIL = 'anonymous@test.net'
ANONYMOUS_USER = {
    'email': ANONYMOUS_USER_EMAIL,
    'first_name': u'Anonymous',
    'last_name': u'user 🤦',
    'phone': '1234',
    'postcode': '1234',
    'country': 'AU',
}

def create_fixtures():
    au, _ = Country.objects.get_or_create(iso_3166_1_a2=u'AU', iso_3166_1_a3=u'AUS', iso_3166_1_numeric=u'036', printable_name=u'Australia')

    pog = Group.objects.create(name='Parkstay Officers')
    
    new_user = EmailUser.objects.create(email=NEW_USER_EMAIL, first_name=u'New', last_name=u'user 🤦')

    admin_user = EmailUser.objects.create(email=ADMIN_USER_EMAIL, first_name=u'Admin', last_name=u'user 🤦')
    admin_user.is_superuser = True
    admin_user.groups.add(pog)
    admin_user.save()

    ar = ps.Region.objects.create(name='Region')
    ad = ps.District.objects.create(name='District', region=ar)
    ap = ps.Park.objects.create(name='Park', district=ad,entry_fee_required=True, oracle_code='pk1')

    c1 = ps.Campground.objects.create(name='Campground 1', park=ap, oracle_code='cg1', site_type=0, campground_type=0)
    c2 = ps.Campground.objects.create(name='Campground 2', park=ap, oracle_code='cg2', site_type=1, campground_type=0)
    cg = ps.CampgroundGroup.objects.create(name='All campgrounds')
    cg.campgrounds.add(c1, c2)

    csc1 = ps.CampsiteClass.objects.create(name='Class 1')
    csc2a = ps.CampsiteClass.objects.create(name='Class 2a')
    csc2b = ps.CampsiteClass.objects.create(name='Class 2b')

    cs1a = ps.Campsite.objects.create(name='Campsite 1a', campground=c1, campsite_class=csc1)
    cs1b = ps.Campsite.objects.create(name='Campsite 1b', campground=c1, campsite_class=csc1)
    cs2a = ps.Campsite.objects.create(name='Campsite 2a', campground=c2, campsite_class=csc2a)
    cs2b = ps.Campsite.objects.create(name='Campsite 2b', campground=c2, campsite_class=csc2a)
    cs2c = ps.Campsite.objects.create(name='Campsite 2c', campground=c2, campsite_class=csc2b)

    prso = ps.PriceReason.objects.create(text='Other', editable=False)
    prsd = ps.PriceReason.objects.create(text='Default fees', editable=True)
    pr = ps.ParkEntryRate.objects.create(period_start=datetime.date.today(), vehicle=D('3.00'), motorbike=D('2.00'), concession=D('1.00'), reason=prsd)

    r1 = ps.Rate.objects.create(adult=D(11.00), child=D(3.00), concession=D(7.00), infant=D(0.00))
    r2 = ps.Rate.objects.create(adult=D(13.00), child=D(4.00), concession=D(9.00), infant=D(0.00))

    cs1ar1 = ps.CampsiteRate.objects.create(campsite_id=cs1a.id, rate_id=r1.id, date_start=datetime.date.today(), price_model=0, rate_type=0, reason_id=prsd.id, update_level=0)
    cs1br2 = ps.CampsiteRate.objects.create(campsite_id=cs1b.id, rate_id=r2.id, date_start=datetime.date.today(), price_model=0, rate_type=0, reason_id=prso.id, update_level=0)
    cs2ar1 = ps.CampsiteRate.objects.create(campsite_id=cs2a.id, rate_id=r1.id, date_start=datetime.date.today(), price_model=0, rate_type=0, reason_id=prsd.id, update_level=0)
    cs2br2 = ps.CampsiteRate.objects.create(campsite_id=cs2b.id, rate_id=r2.id, date_start=datetime.date.today(), price_model=0, rate_type=0, reason_id=prsd.id, update_level=0)
    cs2cr2 = ps.CampsiteRate.objects.create(campsite_id=cs2c.id, rate_id=r2.id, date_start=datetime.date.today(), price_model=0, rate_type=0, reason_id=prso.id, update_level=0)


class ClientBookingTestCase(TransactionTestCase):
    create_booking_url = reverse('create_booking')
    booking_url = reverse('public_make_booking')
    success_url = reverse('public_booking_success')
    checkout_url = reverse('checkout:index')
    payment_details_url = reverse('checkout:payment-details')
    preview_url = reverse('checkout:preview')
    
    booking_api_url = '/api/booking/'

    def setUp(self):
        self.client = SocialClient(SERVER_NAME='parkstaytests.lan.fyi')
        create_fixtures()


    @mock.patch('ledger.checkout.views.PaymentDetailsView.handle_last_check')
    def test_booking_anonymous_sites(self, handle_last_check):
        base_date = datetime.date.today()
        ext_date = lambda x: base_date+datetime.timedelta(days=x)

        campsite = ps.Campsite.objects.get(name='Campsite 1a')

        # create a temporary booking
        temporary = {
            'arrival': ext_date(1).strftime('%Y/%m/%d'),
            'departure': ext_date(10).strftime('%Y/%m/%d'),
            'campsite': campsite.id,
            'num_adult': 1,
            'num_child': 2,
            'num_concession': 3,
            'num_infant': 4
        }

        # start a temporary booking
        response = self.client.post(self.create_booking_url, temporary)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # submit details, promote to a legitimate booking
        submission = {
            'num_adult': 1,
            'num_child': 2,
            'num_concession': 3,
            'num_infant': 4,
            'form-0-entry_fee': 'on',
            'form-0-vehicle_rego': 'REGO1',
            'form-0-vehicle_type': 0,
            'form-1-entry_fee': 'off',
            'form-1-vehicle_rego': 'REGO2',
            'form-1-vehicle_type': 1,
            'form-INITIAL_FORMS': 1,
            'form-MAX_NUM_FORMS': 8,
            'form-MIN_NUM_FORMS': 0,
            'form-TOTAL_FORMS': 2,
        }
        submission.update(ANONYMOUS_USER)
        submission['confirm_email'] = submission['email']
        response = self.client.post(self.booking_url, submission, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[-1][0], self.payment_details_url)

        # check that attempts to immediately jump to preview get knocked back
        response = self.client.get(self.preview_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[-1][0], self.payment_details_url)

        # attempt a BPAY payment
        response = self.client.post(self.preview_url, {
            'payment_method': 'bpay'
        })
        self.assertEqual(response.status_code, 200)

        # check that preview page works
        response = self.client.get(self.preview_url)
        self.assertEqual(response.status_code, 200)

        # submit the order
        response = self.client.post(self.preview_url, {
            'action': 'place_order'
        }, follow=True)

        # check booking exists
        booking = ps.Booking.objects.order_by('-created').first()
        self.assertIsNotNone(booking)
        # check booking is finalized
        self.assertEqual(booking.booking_type, 1)
        # check campsite blocks are reserved
        self.assertEqual(
            set(booking.campsites.values_list('campsite', 'date')),
            set([(campsite.id, ext_date(i)) for i in range(1, 10)])
        )


    @mock.patch('ledger.checkout.views.PaymentDetailsView.handle_last_check')
    def test_booking_anonymous_class(self, handle_last_check):
        base_date = datetime.date.today()
        ext_date = lambda x: base_date+datetime.timedelta(days=x)

        campground = ps.Campground.objects.get(name='Campground 2')
        campsite_class = ps.CampsiteClass.objects.get(name='Class 2a')
        # create a temporary booking
        temporary = {
            'arrival': ext_date(1).strftime('%Y/%m/%d'),
            'departure': ext_date(10).strftime('%Y/%m/%d'),
            'campground': campground.id,
            'campsite_class': campsite_class.id,
            'num_adult': 1,
            'num_child': 2,
            'num_concession': 3,
            'num_infant': 4
        }

        # start a temporary booking
        response = self.client.post(self.create_booking_url, temporary)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # submit details, promote to a legitimate booking
        submission = {
            'num_adult': 1,
            'num_child': 2,
            'num_concession': 3,
            'num_infant': 4,
            'form-0-entry_fee': 'on',
            'form-0-vehicle_rego': 'REGO1',
            'form-0-vehicle_type': 0,
            'form-1-entry_fee': 'off',
            'form-1-vehicle_rego': 'REGO2',
            'form-1-vehicle_type': 1,
            'form-INITIAL_FORMS': 1,
            'form-MAX_NUM_FORMS': 8,
            'form-MIN_NUM_FORMS': 0,
            'form-TOTAL_FORMS': 2,
        }
        submission.update(ANONYMOUS_USER)
        submission['confirm_email'] = submission['email']
        response = self.client.post(self.booking_url, submission, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[-1][0], self.payment_details_url)

        # attempt a BPAY payment
        response = self.client.post(self.preview_url, {
            'payment_method': 'bpay'
        })
        self.assertEqual(response.status_code, 200)

        # check that preview page works
        response = self.client.get(self.preview_url)
        self.assertEqual(response.status_code, 200)

        # submit the order
        response = self.client.post(self.preview_url, {
            'action': 'place_order'
        }, follow=True)

        # check booking exists
        booking = ps.Booking.objects.order_by('-created').first()
        self.assertIsNotNone(booking)
        # check booking is finalized
        self.assertEqual(booking.booking_type, 1)


    @mock.patch('ledger.checkout.views.PaymentDetailsView.handle_last_check')
    def test_booking_internal_sites(self, handle_last_check):
        base_date = datetime.date.today()
        ext_date = lambda x: base_date+datetime.timedelta(days=x)

        campsite_qs = ps.Campsite.objects.filter(campground__name='Campground 1')

        data = {
            'arrival': ext_date(1).strftime('%Y-%m-%d'),
            'departure': ext_date(10).strftime('%Y-%m-%d'),
            'guests': {
                'adult': 1,
                'concession': 2,
                'child': 3,
                'infant': 4,
            },
            'campsites': list(campsite_qs.values_list('id', flat=True)),
            'customer': ANONYMOUS_USER,
            'regos': [
                {'type': 'vehicle', 'rego': 'REGO1', 'entry_fee': True},
                {'type': 'motorbike', 'rego': 'REGO2', 'entry_fee': False},
            ],
            # FIXME: remove requirement for submitting cost
            'costs': {'total': 319 }
        }
        data_json = json.dumps(data)
        
        # attempt to use the admin booking API without authentcation
        response = self.client.post(self.booking_api_url, data_json, content_type='application/json')
        self.assertEqual(response.status_code, 403)
    
        # login as an admin and try to create a proxy booking
        self.client.login(ADMIN_USER_EMAIL)
        response = self.client.post(self.booking_api_url, data_json, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # check booking exists
        booking = ps.Booking.objects.order_by('-created').first()
        self.assertIsNotNone(booking)
        # check booking is finalized
        self.assertEqual(booking.booking_type, 0)
        # check campsite blocks are reserved
        self.assertEqual(
            set(booking.campsites.values_list('campsite', 'date')),
            set(itertools.chain(*[[(c.id, ext_date(i)) for i in range(1, 10)] for c in campsite_qs])),
        )


class BookingRangeTestCase(TestCase):
    def setUp(self):
        #import pdb; pdb.set_trace()
        create_fixtures()
        self.client = Client()

# NOTE: don't need these, change booking ranges to have allow overlapping, absence imply open
# keep as an example for new tests
    """
    def _range_overlap_check(self, model, target, kwargs):
        br1 = model.objects.create(range_start=datetime.date(2018, 1, 10), range_end=datetime.date(2018, 1, 15), **kwargs)

        DISALLOWED = [
            (datetime.date(2018, 1, 11), datetime.date(2018, 1, 13)),    # inside
            (datetime.date(2018, 1, 5), datetime.date(2018, 1, 11)),     # overlap left
            (datetime.date(2018, 1, 14), datetime.date(2018, 1, 18)),    # overlap right
            (datetime.date(2018, 1, 8), datetime.date(2018, 1, 17)),     # overlap all
            (datetime.date(2018, 1, 8), None),     # infinite overlap all
            (datetime.date(2018, 1, 14), None),     # infinite overlap right
        ]
        ALLOWED = [
            (datetime.date(2018, 1, 5), datetime.date(2018, 1, 10)),
            (datetime.date(2018, 1, 15), datetime.date(2018, 1, 20)),
            (datetime.date(2018, 1, 15), None),
        ]

        for d1, d2 in DISALLOWED:
            gbr = target.get_booking_ranges(d1, d2, overlap=True, endless=d2 is None)
            #print(d1, d2, gbr)
            assert gbr
            try:
                br2 = model.objects.create(range_start=d1, range_end=d2, **kwargs)
                raise ValidationError('Illegal {} created'.format(model.__name__))
            except BookingRangeWithinException:
                pass
        
        for d1, d2 in ALLOWED:
            gbr = target.get_booking_ranges(d1, d2, overlap=True, endless=d2 is None)
            #print(d1, d2, gbr)
            assert not gbr
            br3 = model.objects.create(range_start=d1, range_end=d2, **kwargs)
            br3.delete()

        
    def test_campground_range_overlap(self):
        cg = ps.Campground.objects.get(name='Campground 1')
        cg.booking_ranges.all().delete()
        self._range_overlap_check(ps.CampgroundBookingRange, cg, {'campground': cg})

    def test_campsite_range_overlap(self):
        cs = ps.Campsite.objects.get(name='Campsite 1a')
        cs.booking_ranges.all().delete()
        self._range_overlap_check(ps.CampsiteBookingRange, cs, {'campsite': cs})
    """

    def test_utils_availability(self):
        cg1 = ps.Campground.objects.get(name='Campground 1')
        cg2 = ps.Campground.objects.get(name='Campground 2')
        cs1a = ps.Campsite.objects.get(name='Campsite 1a')
        cs1b = ps.Campsite.objects.get(name='Campsite 1b')
        cs2a = ps.Campsite.objects.get(name='Campsite 2a')
        cs2b = ps.Campsite.objects.get(name='Campsite 2b')
        cs2c = ps.Campsite.objects.get(name='Campsite 2c')

        base_date = datetime.date.today()
        ext_date = lambda x: base_date+datetime.timedelta(days=x)

        cb1 = ps.CampgroundBookingRange.objects.create(
            campground=cg1,
            range_start=ext_date(10),
            range_end=None,
            status=1,
        )
        cb2 = ps.CampsiteBookingRange.objects.create(
            campsite=cs2a,
            range_start=ext_date(12),
            range_end=None,
            status=1
        )
        cb3b = ps.CampsiteBookingRange.objects.create(
            campsite=cs2b,
            range_start=ext_date(14),
            range_end=ext_date(20),
            status=1
        )
        cb3c = ps.CampsiteBookingRange.objects.create(
            campsite=cs2c,
            range_start=ext_date(14),
            range_end=ext_date(20),
            status=1
        )

        cs_qs = ps.Campsite.objects.all()
        # check for overlap of campground/campsite closures
        self.assertEqual(utils.get_open_campgrounds(cs_qs, ext_date(1), ext_date(8)), set((cg1.pk, cg2.pk)))
        self.assertEqual(utils.get_open_campgrounds(cs_qs, ext_date(8), ext_date(14)), set((cg2.pk,)))
        self.assertEqual(utils.get_open_campgrounds(cs_qs, ext_date(10), ext_date(14)), set((cg2.pk,)))
        self.assertEqual(utils.get_open_campgrounds(cs_qs, ext_date(10), ext_date(15)), set())
        # check for earlier-than-today cutoff
        self.assertEqual(utils.get_open_campgrounds(cs_qs, ext_date(-1), ext_date(8)), set())

        av1 = utils.get_campsite_availability(cs_qs, ext_date(-1), ext_date(15))
        # check for campsite closures
        for d in [ext_date(x) for x in range(10, 15)]:
            self.assertEqual(tuple(av1[cs1a.pk][d]), ('closed','Other'))
            self.assertEqual(tuple(av1[cs1b.pk][d]), ('closed','Other'))

        for d in [ext_date(x) for x in range(12, 15)]:
            self.assertEqual(tuple(av1[cs2a.pk][d]), ('closed','Other'))

        for d in [ext_date(x) for x in range(14, 15)]:
            self.assertEqual(tuple(av1[cs2b.pk][d]), ('closed','Other'))
        
        # check for earlier-than-today cutoff
        for cs in cs_qs:
            self.assertEqual(tuple(av1[cs.pk][ext_date(-1)]), ('tooearly',None))

        # check for far future cutoff
        max_adv = cg2.max_advance_booking
        av2 = utils.get_campsite_availability(ps.Campsite.objects.filter(id=cs2b.pk), ext_date(max_adv+1), ext_date(max_adv+3))
        print(av2[cs2b.pk])
        for i in range(max_adv+1, max_adv+3):
            self.assertEqual(tuple(av2[cs2b.pk][ext_date(i)]), ('toofar',None) if i > max_adv else ('open',None))

