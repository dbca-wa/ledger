from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from commercialoperator.components.approvals.models import Approval
from ledger.accounts.models import EmailUser
from datetime import date, timedelta
from commercialoperator.components.approvals.email import (
    send_approval_renewal_email_notification,)

import itertools

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send Approval renewal notice when approval is due to expire in 30 days'

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email='cron@dbca.wa.gov.au')
        except:
            user = EmailUser.objects.create(email='cron@dbca.wa.gov.au', password = '')

        today = timezone.localtime(timezone.now()).date()
        expiry_notification_date = today + timedelta(days=30)
        renewal_conditions = {
            'expiry_date__lte': expiry_notification_date,
            'renewal_sent': False,
            'replaced_by__isnull': True,
        }
        logger.info('Running command {}'.format(__name__))

        # 2 month licences cannot be renewed
        qs=Approval.objects.filter(**renewal_conditions).exclude(current_proposal__other_details__preferred_licence_period='2_months')
        print qs
        for a in Approval.objects.filter(**renewal_conditions):
            if a.status == 'current' or a.status == 'suspended':
                try:
                    a.generate_renewal_doc()
                    send_approval_renewal_email_notification(a)
                    a.renewal_sent = True
                    a.save()
                    logger.info('Renewal notice sent for Approval {}'.format(a.id))
                except:
                    logger.info('Error sending renewal notice for Approval {}'.format(a.id))

        logger.info('Command {} completed'.format(__name__))
