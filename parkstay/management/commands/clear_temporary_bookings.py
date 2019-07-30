from django.core.management.base import BaseCommand
from django.utils import timezone
from parkstay.models import Booking

from datetime import timedelta

class Command(BaseCommand):
    help = 'Clear out any expired temporary bookings that have been abandoned by the user'

    def handle(self, *args, **options):
        query = Booking.objects.filter(
            booking_type=3, 
            expiry_time__lt=timezone.now()-timedelta(minutes=5)
        )
        print(query.delete())
        
