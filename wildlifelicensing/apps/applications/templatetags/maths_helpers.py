from django.template.defaulttags import register


@register.filter
def divide_into(denominator, numerator):
    if numerator == 0:
        return 0
    elif denominator > numerator:
        return 1
    else:
        return numerator / denominator
