from datetime import date, timedelta, datetime
from django_cron import CronJobBase, Schedule
from ledgergw import utils as ledgergw_utils
from ledger.payments import models as ledger_payment_models 

class OracleReceipts(CronJobBase):
    RUN_AT_TIMES = ['01:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'ledgergw.oraclereceipts'

    def do(self):
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        ledgergw_utils.generate_oracle_receipts(yesterday.date().strftime('%Y-%m-%d'), False, None)

