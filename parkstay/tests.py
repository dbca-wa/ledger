# -*- coding: utf8 -*-

from django.conf import settings
from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.shortcuts import reverse

from ledger.accounts.models import EmailUser

from parkstay import utils, models as ps
from parkstay.exceptions import BookingRangeWithinException

import datetime

ADMIN_USER_EMAIL = 'admin@test.net'
NEW_USER_EMAIL = 'new_user@test.net'
ANONYMOUS_USER_EMAIL = 'anonymous@test.net'

def create_fixtures():
    new_user = EmailUser.objects.create(email=NEW_USER_EMAIL, first_name=u'New', last_name=u'user 🤦')
    
    admin_user = EmailUser.objects.create(email=ADMIN_USER_EMAIL, first_name=u'Admin', last_name=u'user 🤦')
    admin_user.is_superuser = True
    admin_user.save()
    

    ar = ps.Region.objects.create(name='Region')
    ad = ps.District.objects.create(name='District', region=ar)
    ap = ps.Park.objects.create(name='Park', district=ad,entry_fee_required=True, oracle_code='pk1')
    c1 = ps.Campground.objects.create(name='Campground 1', park=ap, oracle_code='cg1')
    c2 = ps.Campground.objects.create(name='Campground 2', park=ap)
    cg = ps.CampgroundGroup.objects.create(name='All campgrounds')
    cg.campgrounds.add(c1, c2)
    
    cs1a = ps.Campsite.objects.create(name='Campsite 1a', campground=c1)
    cs1b = ps.Campsite.objects.create(name='Campsite 1b', campground=c1)
    cs2a = ps.Campsite.objects.create(name='Campsite 2a', campground=c2)
    cs2b = ps.Campsite.objects.create(name='Campsite 2b', campground=c2)


class ClientBookingTestCase(TestCase):
    client = Client()
    create_booking_url = reverse('create_booking')
    booking_url = reverse('public_make_booking')
    success_url = reverse('public_booking_success')

    def setUp(self):
        create_fixtures()

    def test_booking_external_anonymous(self):
        base_date = datetime.date.today()
        ext_date = lambda x: base_date+datetime.timedelta(days=x)

        # create a temporary booking
        response = self.client.post(self.create_booking_url, {
            'arrival': ext_date(1).strftime('%Y/%m/%d'),
            'departure': ext_date(10).strftime('%Y/%m/%d'),
            'campsite': ps.Campsite.objects.get(name='Campsite 1a').id,
            'num_adult': 1,
            'num_child': 2,
            'num_concession': 3,
            'num_infant': 4
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')



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
        cs1a= ps.Campsite.objects.get(name='Campsite 1a')
        cs1b= ps.Campsite.objects.get(name='Campsite 1b')
        cs2a= ps.Campsite.objects.get(name='Campsite 2a')
        cs2b= ps.Campsite.objects.get(name='Campsite 2b')

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
        cb3 = ps.CampsiteBookingRange.objects.create(
            campsite=cs2b,
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
            self.assertEqual(tuple(av1[cs1a.pk][d]), ('closed',))
            self.assertEqual(tuple(av1[cs1b.pk][d]), ('closed',))

        for d in [ext_date(x) for x in range(12, 15)]:
            self.assertEqual(tuple(av1[cs2a.pk][d]), ('closed',))

        for d in [ext_date(x) for x in range(14, 15)]:
            self.assertEqual(tuple(av1[cs2b.pk][d]), ('closed',))
        
        # check for earlier-than-today cutoff
        for cs in cs_qs:
            self.assertEqual(tuple(av1[cs.pk][ext_date(-1)]), ('tooearly',))

        # check for far future cutoff
        max_adv = cg2.max_advance_booking
        av2 = utils.get_campsite_availability(ps.Campsite.objects.filter(id=cs2b.pk), ext_date(max_adv+1), ext_date(max_adv+3))
        print(av2[cs2b.pk])
        for i in range(max_adv+1, max_adv+3):
            self.assertEqual(tuple(av2[cs2b.pk][ext_date(i)]), ('toofar',) if i > max_adv else ('open',))

