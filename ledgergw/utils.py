from ledger.payments.utils import oracle_parser_on_invoice,update_payments
from ledger.payments import models as ledger_payment_models #OracleInterfaceSystem
import re
#from ledgergw import utils as ledgergw_utils

def oracle_integration(date,override, system, system_name):
    oracle_codes = oracle_parser_on_invoice(date,system,system_name,override=override)

def generate_oracle_receipts(date, override, system):

    #today = datetime.today()
    #yesterday = today - timedelta(days=1)
    #print (yesterday.date().strftime('%Y-%m-%d'))
    ois = ledger_payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api', enabled=True)
    for s in ois:
        print (s.system_id)
        oracle_integration(date, False, s.system_id,s.system_name)
    
def remove_html_tags(text):
    HTML_TAGS_WRAPPED = re.compile(r'<[^>]+>.+</[^>]+>')
    HTML_TAGS_NO_WRAPPED = re.compile(r'<[^>]+>')

    text = HTML_TAGS_WRAPPED.sub('', text)
    text = HTML_TAGS_NO_WRAPPED.sub('', text)
    return text

