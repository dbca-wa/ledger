from django.conf import settings
from django.core.urlresolvers import reverse
from ledger.emails.emails import EmailBase

def host_reverse(name, args=None, kwargs=None):
    return "{}{}".format(settings.DEFAULT_HOST, reverse(name, args=args, kwargs=kwargs))


class TemplateEmailBase(EmailBase):
    subject = ''
    html_template = 'wl/emails/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'wl/emails/base-email.txt'
