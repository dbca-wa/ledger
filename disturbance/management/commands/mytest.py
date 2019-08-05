from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from disturbance.components.proposals.models import ProposalType
import datetime



import itertools

class Command(BaseCommand):
    help = 'Change the status of Compliances from future to due when they are close to due date'

    def handle(self, *args, **options):
        proposal_type = ProposalType.objects.filter(name='Disturbance').latest('version')
        print 'latest version {}'.format(proposal_type)
