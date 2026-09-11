from django.core.management.base import BaseCommand
from django.db.models import F
from django.db.models.functions import Abs
from django.utils import timezone

from datetime import timedelta
from decimal import Decimal

from ledger.payments.emails import send_discrepency_report
from ledger.payments.models import OracleInterfaceSystem, PaymentTotal, OracleInterfaceReportReceipient

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ""

    def add_arguments(self, parser):
        parser.add_argument(
            '--for_week',
            action='store_true',
            help='Only process discrepancies updated in the last 7 days.'
        )
        parser.add_argument(
            '--discrepancy_range',
            type=str,
            default='0',
            help='Minimum difference between payment totals for a discrepancy to occur.'
        )
        parser.add_argument(
            '--system_number',
            type=str,
            help='Specify System Interface Number to only send report to that System.'
        )
        

    def handle(self, *args, **options):
        logger.info('Running command {}'.format(__name__))
        print('Running command {}'.format(__name__))
        
        systems = OracleInterfaceSystem.objects.filter(enabled=True)

        discrepancy_range = Decimal('0')
        for_week = False

        # Validate for_week
        if options.get('for_week'):
            for_week = True
            
        # Validate discrepancy_range
        raw_range = options.get('discrepancy_range')
        try:
            discrepancy_range = Decimal(raw_range)
            if discrepancy_range < 0:
                discrepancy_range = Decimal('0')
        except:
            discrepancy_range = Decimal('0')

        if options.get('system_number'):
            systems = systems.filter(system_id=options.get('system_number'))

        for system in systems:
            try:
                logger.info('Checking discrepancies for {} {}'.format(system.system_id, system.system_name))
                print('Checking discrepancies for {} {}'.format(system.system_id, system.system_name))

                discrepancies = PaymentTotal.objects.filter(
                    oracle_system=system,
                ).annotate(
                    diff=Abs(F('bpoint_gateway_total') - F('oracle_receipt_total'))
                ).exclude(
                    diff__lte=discrepancy_range
                ).order_by('-settlement_date')

                if for_week:
                    discrepancies = discrepancies.filter(updated__gte=timezone.now() - timedelta(days=7))

                logger.info('{} discrepancies found for {} {}'.format(discrepancies.count(), system.system_id, system.system_name))
                print('{} discrepancies found for {} {}'.format(discrepancies.count(), system.system_id, system.system_name))

                #format
                discrepancies_formatted = []
                for discrepancy in discrepancies:
                    row = {}
                    row['id'] = discrepancy.id
                    row['oracle_system_id'] = discrepancy.oracle_system_id
                    row['oracle_system_id_code'] = discrepancy.oracle_system.system_id
                    row['settlement_date'] = discrepancy.settlement_date.strftime('%d %b %Y')  
                    row['bpoint_gateway_total'] = str(discrepancy.bpoint_gateway_total)
                    row['ledger_bpoint_total'] = str(discrepancy.ledger_bpoint_total)
                    row['oracle_parser_total'] = str(discrepancy.oracle_parser_total)
                    row['oracle_receipt_total'] = str(discrepancy.oracle_receipt_total)
                    row['cash_total'] = str(discrepancy.cash_total)
                    row['bpay_total'] = str(discrepancy.bpay_total)
                    row['total_diff'] = str(discrepancy.diff)
                    row['updated'] = discrepancy.updated.strftime('%d/%m/%Y %H:%M:%S')

                    discrepancies_formatted.append(row)

                #send email
                recipients = list(OracleInterfaceReportReceipient.objects.filter(system=system).values_list('email', flat=True))
                send_discrepency_report(system, discrepancies_formatted, recipients)

            except Exception as e:
                logger.error("Failed to send discrepancy report with error:", e)
