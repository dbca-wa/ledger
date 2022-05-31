from ledger.payments.utils import oracle_parser_on_invoice,update_payments
from ledger.payments import models as ledger_payment_models #OracleInterfaceSystem
from ledgergw import utils as ledgergw_utils

def oracle_integration(date,override, system):
    oracle_codes = oracle_parser_on_invoice(date,system,'Mooring Booking',override=override)


def generate_oracle_receipts(date, override, system):

    #today = datetime.today()
    #yesterday = today - timedelta(days=1)
    #print (yesterday.date().strftime('%Y-%m-%d'))
    ois = ledger_payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api', enabled=True)
    for s in ois:
        print (s.system_id)
        ledgergw_utils.oracle_integration(date, False, s.system_id)

