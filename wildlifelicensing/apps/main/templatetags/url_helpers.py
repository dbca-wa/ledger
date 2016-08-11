from django.template.defaulttags import register


@register.filter
def get_url_filename(url):
    return url[url.rfind('/') + 1:]
