from django.core.serializers import serialize
from django.db.models.query import QuerySet
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from django.utils.safestring import mark_safe
from django.template import Library

from ..serializers import WildlifeLicensingJSONEncoder

register = Library()


@register.filter
def jsonify(obj):
    if isinstance(obj, QuerySet):
        return mark_safe(serialize('json', obj))
    return mark_safe(json.dumps(obj, cls=WildlifeLicensingJSONEncoder))
