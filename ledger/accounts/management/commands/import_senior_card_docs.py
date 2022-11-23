from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import datetime
from zipfile import ZipFile
import os
from pathlib import Path
import time
import calendar
from django.core.files.base import ContentFile
from ledger.accounts.models import Document, EmailUser, PrivateDocument
import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import Senior card of EmailUser from temporary folder'

    def handle(self, *args, **options):
        #The script assumes that files to be imported are in temp folder
        errors=[]
        updates=[]
        TEMP_DIR ='/temp'

        import os
        from ledger.settings_base import BASE_DIR
        save_dir =BASE_DIR + TEMP_DIR

        logger.info('Running command {}'.format(__name__))
        entries_path=Path(save_dir)

        
        if os.path.exists(save_dir):
            for f in entries_path.iterdir():
                if f.is_file():
                    u_id, type_name =f.name.split('_')
                    try:
                        #for f in entries_path.iterdir():
                        #u_id, type_name =f.name.split('_')[0]
                        if u_id and type_name.startswith('seniorcard'):
                            usr=EmailUser.objects.get(id=u_id)
                            ts=calendar.timegm(time.gmtime())
                            if f.is_file() and not usr.senior_card2:
                                rb=f.read_bytes()
                                id_file_name='{0}_{1}'.format(str(ts), f.name)
                                p=PrivateDocument.objects.create(name=id_file_name)
                                p.upload.save(id_file_name, ContentFile(rb))
                                p.save()
                                usr.senior_card2=p
                                usr.save()
                                updates.append(usr.id)
                    except Exception as e:
                        err_msg = 'Error copying Senior card doc for EmailUser {}'.format(u_id)
                        logger.error('{}\n{}'.format(err_msg, str(e)))
                        errors.append(err_msg)
                else:
                    continue
        
        cmd_name = __name__.split('.')[-1].replace('_', ' ').upper()
        err_str = '<strong style="color: red;">Errors: {}</strong>'.format(len(errors)) if len(errors)>0 else '<strong style="color: green;">Errors: 0</strong>'
        msg = '<p>{} completed. {}. IDs updated: {}.</p>'.format(cmd_name, err_str, updates)
        logger.info(msg)
        print(msg) # will redirect to cron_tasks.log file, by the parent script




