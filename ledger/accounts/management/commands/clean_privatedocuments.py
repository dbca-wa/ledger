from ledger.address.models import UserAddress
from ledger.accounts.models import PrivateDocument,EmailUser

class Command(BaseCommand):
    help = 'Cleans up private documents table.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            pd = PrivateDocument.objects.filter(extension='')
            print (pd.count())
            for p  in pd:

                print (p.id)
                print (p.upload.path)
                ext = ''
                if p.upload.path[-4] == '.':
                    ext = p.upload.path[-4:]
                if p.upload.path[-5] == '.':
                    ext = p.upload.path[-5:]

                print (ext)
                if len(ext) > 0:
                    p.extension = ext
                    p.name = 'file'+ext
                    eu = EmailUser.objects.filter(identification2=p.id)
                    print (eu)
                    if eu.count() > 0:
                        p.file_group=1
                    p.save()
        except Exception as e:
            raise CommandError(e)
