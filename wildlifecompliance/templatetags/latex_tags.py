from django import template
from django.utils.safestring import mark_safe

import os

register = template.Library()


@register.simple_tag(takes_context=True)
def base_dir(context):
    """ Hack for getting the base_dir for uWSGI config. settings.BASE_DIR returns '' in latex templates when using uWSGI """
    return '{}'.format(os.getcwd())

@register.filter()
def latex(value,args):
    """
    convert some special characters
    """
    if not value:
        return ""
    elif not args:
        return mark_safe(value)
    else:
        args = unicode(args)
        for c in args:
            if c == '&':
                value = value.replace(c,'\&')
            elif c == u'\xB0':
                value = value.replace(c,'$^\circ$')
        return mark_safe(value)
