from django.core.serializers.json import DjangoJSONEncoder  # to handle the datetime serialization
from django.db.models.fields.files import FieldFile


class WildlifeLicensingJSONEncoder(DjangoJSONEncoder):
    """
    DjangoJSONEncoder subclass that encode fiel file object as its URL
    """
    def default(self, o):
        if isinstance(o, FieldFile):
            return o.url
        else:
            return super(WildlifeLicensingJSONEncoder, self).default(o)
