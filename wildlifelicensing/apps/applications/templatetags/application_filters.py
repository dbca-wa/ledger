from django.template.defaulttags import register

MAX_COLS = 12


@register.filter
def derive_col_width(num_cols):
    if num_cols == 0:
        return 0
    elif num_cols > MAX_COLS:
        return 1
    else:
        return int(MAX_COLS / num_cols)
