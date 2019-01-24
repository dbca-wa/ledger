from django.template.defaultfilters import stringfilter, register
from django.utils.safestring import mark_safe

REPLACEMENTS = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '<': r'\textless{}',
    '>': r'\textgreater',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum',
    '\n': r'\newline ',
    '\r': r'',
}


@register.filter
@stringfilter
def texify(value):
    """
    Escapes special LaTeX characters.
    """
    for k, v in REPLACEMENTS.items():
        value = value.replace(k, v)
    return mark_safe(value)