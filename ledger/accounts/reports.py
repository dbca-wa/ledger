import csv
from six.moves import StringIO
from django.db import connection
from ledger.accounts.models import EmailUserReport

def user_report():
    strIO = None
    # Create or update view
    cursor = connection.cursor()
    sql = 'CREATE OR REPLACE VIEW accounts_emailuser_report_v AS \
            select md5(CAST((first_name,last_name,dob)AS text)) as hash,count(*) as occurence, first_name,last_name,\
            dob from accounts_emailuser group by first_name,last_name,dob;'
    cursor.execute(sql)

    users = EmailUserReport.objects.filter(occurence__gt=1)
    if users:
        strIO = StringIO()
        fieldnames = ['Occurence', 'Given Name(s)','Last Name','DOB']
        writer = csv.DictWriter(strIO, fieldnames=fieldnames)
        writer.writeheader()

        for u in users:
            info = {
                'Occurence': u.occurence,
                'Given Name(s)': u.first_name,
                'Last Name': u.last_name,
                'DOB': u.dob
            }
            writer.writerow(info)
        strIO.flush()
        strIO.seek(0)
    return strIO
