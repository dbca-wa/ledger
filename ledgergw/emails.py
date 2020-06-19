from io import BytesIO

from django.conf import settings

from ledger.payments.models import Invoice
from ledgergw import settings 
from django.core.mail import EmailMessage, EmailMultiAlternatives

from ledger.emails.emails import EmailBase
from django.template.loader import render_to_string, get_template
from confy import env
from django.template import Context
from ledger.accounts.models import Document
from django.contrib.auth.models import Group
from ledger.accounts.models import EmailUser

import datetime
import hashlib

default_from_email = settings.DEFAULT_FROM_EMAIL
default_campground_email = settings.CAMPGROUNDS_EMAIL
default_rottnest_email = settings.ROTTNEST_EMAIL

class TemplateEmailBase(EmailBase):
    subject = ''
    html_template = 'ledgergw/email/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'ledgergw/email/base_email.txt'

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

    context['version'] = settings.VERSION_NO
    # Custom Email Body Template
    context['body'] = get_template(template).render(context)
    # Main Email Template Style ( body template is populated in the center
    if template_group == 'system-oim':
        main_template = get_template('ledgergw/email/base_email-oim.html').render(context)
    else:
        main_template = get_template('ledgergw/email/base_email-oim.html').render(context)
   
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


def email_log(line):
     dt = datetime.datetime.now()
     f= open(settings.BASE_DIR+"/logs/email.log","a+")
     f.write(str(dt.strftime('%Y-%m-%d %H:%M:%S'))+': '+line+"\r\n")
     f.close()  


