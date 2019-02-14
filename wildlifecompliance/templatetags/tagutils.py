from django.template import Library
from wildlifecompliance import settings

register = Library()

@register.simple_tag(takes_context=False)
def get_instance_type():
    return settings.EMAIL_INSTANCE
