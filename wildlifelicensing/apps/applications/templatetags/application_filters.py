from django.template.defaulttags import register

from wildlifelicensing.apps.applications.models import Application


MAX_COLS = 12


@register.filter
def derive_col_width(num_cols):
    if num_cols == 0:
        return 0
    elif num_cols > MAX_COLS:
        return 1
    else:
        return int(MAX_COLS / num_cols)


@register.filter
def get_application_verb(application):
    if application.application_type == 'amendment':
        return 'Amend'
    elif application.application_type == 'renewal':
        return 'Renew'
    elif application.is_temporary:
        return 'New'
    else:
        return 'Edit'
