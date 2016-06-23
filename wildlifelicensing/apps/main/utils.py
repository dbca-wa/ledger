from preserialize.serialize import serialize

from wildlifelicensing.apps.main.models import CommunicationsLogEntry


COMMUNCATION_TYPES = dict(CommunicationsLogEntry.TYPE_CHOICES)


def format_communications_log_entry(instance, attrs):
    attrs['type'] = COMMUNCATION_TYPES[attrs['type']]
    attrs['document'] = instance.document.file.url if instance.document else None

    return attrs
