import csv
import datetime
from six.moves import StringIO
from wsgiref.util import FileWrapper
from django.core.mail import EmailMessage 
from django.conf import settings
from parkstay.models import Booking


def outstanding_bookings():
    try:
        outstanding = []
        for b in Booking.objects.all():
            if not b.paid:
                outstanding.append(b)


        strIO = StringIO()
        fieldnames = ['Confirmation Number','Customer','Campground','Arrival','Departure']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)
        for o in outstanding:
            writer.writerow([o.confirmation_number,o.customer.get_full_name(),o.campground.name,o.arrival.strftime('%d/%m/%Y'),o.departure.strftime('%d/%m/%Y')])
        strIO.flush()
        strIO.seek(0)
        _file = strIO

        dt = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        recipients = []
        email = EmailMessage(
            'Unpaid Bookings Summary as at {}'.format(dt),
            'Unpaid Bookings as at {}'.format(dt),
            settings.DEFAULT_FROM_EMAIL,
            to=[r.email for r in recipients]if recipients else [settings.NOTIFICATION_EMAIL]
        )
        email.attach('OustandingBookings_{}.csv'.format(dt), _file.getvalue(), 'text/csv')
        email.send()
    except:
        raise
