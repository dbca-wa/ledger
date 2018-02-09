from django.conf import settings
from django.test import TestCase, Client
from django.core.exceptions import ValidationError

from ledger.accounts.models import EmailUser

from parkstay import models as ps
from parkstay.exceptions import BookingRangeWithinException

import datetime

ADMIN_USER_EMAIL = 'admin@test.net'
NEW_USER_EMAIL = 'new_user@test.net'

def create_fixtures():
    new_user = EmailUser.objects.create(email=NEW_USER_EMAIL)
    
    admin_user = EmailUser.objects.create(email=ADMIN_USER_EMAIL)
    admin_user.is_superuser = True
    admin_user.save()
    

    ar = ps.Region.objects.create(name='Region')
    ad = ps.District.objects.create(name='District', region=ar)
    ap = ps.Park.objects.create(name='Park', district=ad, entry_fee_required=True, oracle_code='pk1')
    c1 = ps.Campground.objects.create(name='Campground 1', park=ap)
    c2 = ps.Campground.objects.create(name='Campground 2', park=ap)
    cg = ps.CampgroundGroup.objects.create(name='All campgrounds')
    cg.campgrounds.add(c1, c2)
    
    cs1a = ps.Campsite.objects.create(name='Campsite 1a', campground=c1)
    cs1b = ps.Campsite.objects.create(name='Campsite 1b', campground=c1)
    cs2a = ps.Campsite.objects.create(name='Campsite 2a', campground=c2)
    cs2b = ps.Campsite.objects.create(name='Campsite 2b', campground=c2)


class BookingRangeTestCase(TestCase):
    def setUp(self):
        #import pdb; pdb.set_trace()
        create_fixtures()
        self.client = Client()

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

    def test_campground_open_close(self):
        cg = ps.Campground.objects.get(name='Campground 1')
        cg.booking_ranges.all().delete()

        # create new baseline open range
        ps.CampgroundBookingRange.objects.create(campground=cg, range_start=datetime.date(2018, 1, 1), range_end=None, status=0)
        
        # create closed range 1
        cg.close({
            'range_start': datetime.date(2018, 1, 10), 
            'range_end': datetime.date(2018, 1, 15),            
        })

        # create infinite closed range 2
        cg.close({
            'range_start': datetime.date(2018, 1, 20)
        })
        
        print(cg.booking_ranges.all())
        
