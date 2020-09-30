import logging
import mimetypes

import six
import django
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import loader, Template, Context
from django.utils.html import strip_tags
from ledger.accounts.models import Document

logger = logging.getLogger('log')


def _render(template, context):
    if isinstance(context, dict):
        context = Context(context)
    if isinstance(template, six.string_types):
        template = Template(template)
    return template.render(context)

def _render2(template, context):
    if isinstance(context, dict):
        context = context
    if isinstance(template, six.string_types):
        template = Template(template)
    return template.render(context)

class EmailBase(object):
    subject = ''
    html_template = 'email/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'email/base-email.txt'

    def send_to_user(self, user, context=None):
        return self.send(user.email, context=context)

    def send(self, to_addresses, from_address=None, context=None, attachments=None, cc=None, bcc=None, reply_to=None):
        """
        Send an email using EmailMultiAlternatives with text and html.
        :param to_addresses: a string or a list of addresses
        :param from_address: if None the settings.DEFAULT_FROM_EMAIL is used
        :param context: a dictionary or a Context object used for rendering the templates.
        :param attachments: a list of (filepath, content, mimetype) triples
               (see https://docs.djangoproject.com/en/1.9/topics/email/)
               or Documents
        :param bcc:
        :param cc:
        :param reply_to:
        :return:
        """
        # The next line will throw a TemplateDoesNotExist if html template cannot be found
        html_template = loader.get_template(self.html_template)
        # render html
        html_body = _render(html_template, context)
        if self.txt_template is not None:
            txt_template = loader.get_template(self.txt_template)
            txt_body = _render(txt_template, context)
        else:
            txt_body = strip_tags(html_body)

        # build message
        if isinstance(to_addresses, six.string_types):
            to_addresses = [to_addresses]
        if isinstance(reply_to, six.string_types):
            reply_to = [reply_to]
        if attachments is None:
            attachments = []
        if attachments is not None and not isinstance(attachments, list):
            attachments = list(attachments)

        if attachments is None:
            attachments = []

        # Convert Documents to (filename, content, mime) attachment
        _attachments = []
        for attachment in attachments:
            if isinstance(attachment, Document):
                filename = str(attachment)
                content = attachment.file.read()
                mime = mimetypes.guess_type(attachment.filename)[0]
                _attachments.append((filename, content, mime))
            else:
                _attachments.append(attachment)
        msg = EmailMultiAlternatives(self.subject, txt_body, from_email=from_address, to=to_addresses,
                                     attachments=_attachments, cc=cc, bcc=bcc, reply_to=reply_to)
        msg.attach_alternative(html_body, 'text/html')
        try:
            msg.send(fail_silently=False)
            return msg
        except Exception as e:
            logger.exception("Error while sending email to {}: {}".format(to_addresses, e))
            return None



class EmailBase2(object):
    subject = ''
    html_template = 'email/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'email/base-email.txt'

    def send_to_user(self, user, context=None):
        return self.send(user.email, context=context)

    def send(self, to_addresses, from_address=None, context=None, attachments=None, cc=None, bcc=None, reply_to=None):
        """
        Send an email using EmailMultiAlternatives with text and html.
        :param to_addresses: a string or a list of addresses
        :param from_address: if None the settings.DEFAULT_FROM_EMAIL is used
        :param context: a dictionary or a Context object used for rendering the templates.
        :param attachments: a list of (filepath, content, mimetype) triples
               (see https://docs.djangoproject.com/en/1.9/topics/email/)
               or Documents
        :param bcc:
        :param cc:
        :param reply_to:
        :return:
        """
        # The next line will throw a TemplateDoesNotExist if html template cannot be found
        html_template = loader.get_template(self.html_template)
        # render html
        html_body = _render2(html_template, context)
        if self.txt_template is not None:
            txt_template = loader.get_template(self.txt_template)
            txt_body = _render2(txt_template, context)
        else:
            txt_body = strip_tags(html_body)

        # build message
        if isinstance(to_addresses, six.string_types):
            to_addresses = [to_addresses]
        if isinstance(reply_to, six.string_types):
            reply_to = [reply_to]
        if attachments is None:
            attachments = []
        if attachments is not None and not isinstance(attachments, list):
            attachments = list(attachments)

        if attachments is None:
            attachments = []

        # Convert Documents to (filename, content, mime) attachment
        _attachments = []
        for attachment in attachments:
            if isinstance(attachment, Document):
                filename = str(attachment)
                content = attachment.file.read()
                mime = mimetypes.guess_type(attachment.filename)[0]
                _attachments.append((filename, content, mime))
            else:
                _attachments.append(attachment)
        msg = EmailMultiAlternatives(self.subject, txt_body, from_email=from_address, to=to_addresses,
                                     attachments=_attachments, cc=cc, bcc=bcc, reply_to=reply_to)
        msg.attach_alternative(html_body, 'text/html')
        try:
            msg.send(fail_silently=False)
            return msg
        except Exception as e:
            logger.exception("Error while sending email to {}: {}".format(to_addresses, e))
            return None



def sendHtmlEmail(to,subject,context,template,cc,bcc,from_email,template_group,attachments=None):
    email_delivery = env('EMAIL_DELIVERY', 'off')
    override_email = env('OVERRIDE_EMAIL', None)
    context['default_url'] = env('DEFAULT_HOST', '')
    context['default_url_internal'] = env('DEFAULT_URL_INTERNAL', '')
    log_hash = int(hashlib.sha1(str(datetime.datetime.now()).encode('utf-8')).hexdigest(), 16) % (10 ** 8)
    email_log(str(log_hash)+' '+subject+":"+str(to)+":"+template_group)
    if email_delivery != 'on':
        print ("EMAIL DELIVERY IS OFF NO EMAIL SENT -- email.py ")
        return False

    if template is None:
        raise ValidationError('Invalid Template')
    if to is None:
        raise ValidationError('Invalid Email')
    if subject is None:
        raise ValidationError('Invalid Subject')

    if from_email is None:
        if settings.DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_email = 'no-reply@dbca.wa.gov.au'


    #django_version = int(str(django.VERSION[0])+''+str(django.VERSION[1]))
    #if django_version > 110:
    #   email_obj = TemplateEmailBase2()
    #else:
    #   email_obj = TemplateEmailBase()


    context['version'] = settings.VERSION_NO
    # Custom Email Body Template
    context['body'] = get_template(template).render(Context(context))
    # Main Email Template Style ( body template is populated in the center
    if template_group == 'system-oim':
        main_template = get_template('email/base_email-oim.html').render(Context(context))

    reply_to=None

    if attachments is None:
        attachments = []

    # Convert Documents to (filename, content, mime) attachment
    _attachments = []
    for attachment in attachments:
        if isinstance(attachment, Document):
             filename = str(attachment)
             content = attachment.file.read()
             mime = mimetypes.guess_type(attachment.filename)[0]
             _attachments.append((filename, content, mime))
        else:
             _attachments.append(attachment)


    if override_email is not None:
        to = override_email.split(",")
        if cc:
            cc = override_email.split(",")
        if bcc:
            bcc = override_email.split(",")

    if len(to) > 1:
        msg = EmailMultiAlternatives(subject, "Please open with a compatible html email client.", from_email=from_email, to=to, attachments=_attachments, cc=cc, bcc=bcc, reply_to=reply_to)
        msg.attach_alternative(main_template, 'text/html')

        #msg = EmailMessage(subject, main_template, to=[to_email],cc=cc, from_email=from_email)
        #msg.content_subtype = 'html'
        #if attachment1:
        #    for a in attachment1:
        #        msg.attach(a)
        try:
             email_log(str(log_hash)+' '+subject)
             msg.send()
             email_log(str(log_hash)+' Successfully sent to mail gateway')
        except Exception as e:
                email_log(str(log_hash)+' Error Sending - '+str(e))
    else:
          msg = EmailMultiAlternatives(subject, "Please open with a compatible html email client.", from_email=from_email, to=to, attachments=_attachments, cc=cc, bcc=bcc, reply_to=reply_to)
          msg.attach_alternative(main_template, 'text/html')

          #msg = EmailMessage(subject, main_template, to=to,cc=cc, from_email=from_email)
          #msg.content_subtype = 'html'
          #if attachment1:
          #    for a in attachment1:
          #        msg.attach(a)
          try:
               email_log(str(log_hash)+' '+subject)
               msg.send()
               email_log(str(log_hash)+' Successfully sent to mail gateway')
          except Exception as e:
               email_log(str(log_hash)+' Error Sending - '+str(e))


    return True

