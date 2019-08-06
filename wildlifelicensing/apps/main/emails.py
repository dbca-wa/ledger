from wildlifelicensing.apps.emails.emails import TemplateEmailBase, host_reverse


class LicenceRenewalNotificationEmail(TemplateEmailBase):
    subject = 'Your wildlife licence is due for renewal.'
    html_template = 'wl/emails/renew_licence_notification.html'
    txt_template = 'wl/emails/renew_licence_notification.txt'


def send_licence_renewal_email_notification(licence):
    email = LicenceRenewalNotificationEmail()
    url = host_reverse('wl_home')

    context = {
        'url': url,
        'licence': licence
    }

    return email.send(licence.profile.email, context=context) is not None
