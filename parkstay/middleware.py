from django.utils import timezone
from parkstay.models import Booking

class BookingTimerMiddleware(object):
    def process_request(self, request):
        if 'ps_booking' in request.session:
            try:
                booking = Booking.objects.get(pk=request.session['ps_booking'])
            except:
                # no idea what object is in self.request.session['ps_booking'], ditch it
                del request.session['ps_booking']
                return
            if booking.booking_type != 3:
                # booking in the session is not a temporary type, ditch it
                del request.session['ps_booking']
            elif timezone.now() > booking.expiry_time:
                # expiry time has been hit, destroy the Booking then ditch it
                booking.delete()
                del request.session['ps_booking']
        return
