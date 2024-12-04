from django.core.management.base import BaseCommand, CommandError
from ledger.address.models import UserAddress
from ledger.accounts.models import PrivateDocument,EmailUser
from django.db.models import Q

class Command(BaseCommand):
    help = 'Cleans up private documents table.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            query_string = Q(extension='') | Q(extension=None)
            pd = PrivateDocument.objects.filter(query_string)
            print ("Total Results: "+str(pd.count()))
            for p  in pd:


                ext = ''
                if p.upload.path[-4] == '.':
                    ext = p.upload.path[-4:]
                if p.upload.path[-5] == '.':
                    ext = p.upload.path[-5:]

                
                if len(ext) > 0:
                    print (p.id)
                    print (p.upload.path)                    
                    p.extension = ext
                    p.name = 'file'+ext
                    eu = EmailUser.objects.filter(identification2=p.id)
                    print (eu)
                    if eu.count() > 0:
                        p.file_group=1
                    p.save()
        except Exception as e:
            raise CommandError(e)
