from datetime import date, timedelta, datetime
from django_cron import CronJobBase, Schedule
from ledgergw import utils as ledgergw_utils
from ledger.payments import models as ledger_payment_models 
from django.core import management
from ledgergw import models as ledgergw_models
from datetime import datetime
import json
import traceback

class OracleReceipts(CronJobBase):
    RUN_AT_TIMES = ['01:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'ledgergw.oraclereceipts'

    def do(self):
        print ("running OracleReceipts")
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        cron_response = "Success"
        try:
            ledgergw_utils.generate_oracle_receipts(yesterday.date().strftime('%Y-%m-%d'), False, None)
        except Exception as e:
            print (e)
            tb = traceback.format_exc()
            cron_response = str(tb)
        
        return cron_response



class JobQueue(CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    schedule = Schedule(run_every_mins=5)
    code = "ledgergw.ledger_job"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Run Management Command
        cron_response = ""
        job_queue = ledgergw_models.JobQueue.objects.filter(status=0)[:3]
        for jq in job_queue:
            print (jq.job_cmd)
            jq.status = 1
            jq.save()
            params_array = []
            try:
                params_array = json.loads(jq.parameters_json)
            except Exception as e:
                print (e)
            print (params_array)   
            try:             
                management.call_command(jq.job_cmd, params_array[0], params_array[1])
                print ("HERE")
                jq.processed_dt = datetime.now()
                jq.status = 2
                jq.save()
            except Exception as e:                
                print (e)
                tb = traceback.format_exc()
                cron_response = cron_response + str(tb)
        
        return cron_response


