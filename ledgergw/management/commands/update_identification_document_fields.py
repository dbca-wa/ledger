from django.core.management.base import BaseCommand
from django.db.models import Q

import logging
import pathlib

from ledger.accounts.models import PrivateDocument

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updates all Identification document records to have all required fields populated.'

    def handle(self, *args, **options):
        try:
            logger.info('Running command {}'.format(__name__))

            private_docs = PrivateDocument.objects.filter(Q(name=None)|Q(name="")|Q(extension=None)|Q(file_group=None))

            for i in private_docs:
                i.name = pathlib.Path(i.upload.name).name
                i.extension = pathlib.Path(i.upload.name
                    ).suffix if (len(
                        pathlib.Path(
                            i.upload.name
                        ).suffix) <= PrivateDocument._meta.get_field('extension').max_length
                    ) else ""
                i.file_group = 1
                i.save(update_fields=["name","extension","file_group"])

            logger.info('Command {} finished'.format(__name__))

        except Exception as e:
            logger.error('Error command {0} : {1}'.format(
                __name__, e))
