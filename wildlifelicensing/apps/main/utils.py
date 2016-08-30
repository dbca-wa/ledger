from preserialize.serialize import serialize

from wildlifelicensing.apps.main.models import CommunicationsLogEntry


COMMUNCATION_TYPES = dict(CommunicationsLogEntry.TYPE_CHOICES)


def format_communications_log_entry(instance, attrs):
    attrs['type'] = COMMUNCATION_TYPES[attrs['type']]
    attrs['documents'] = [(str(document), document.file.url) for document in instance.documents.all()]

    return attrs
