import requests
import json
import logging
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission, calculate_excl_gst
from ledger.payments.models import Invoice
from wildlifecompliance.exceptions import BindApplicationException


def get_department_user(email):
    try:
        res = requests.get(
            '{}/api/users?email={}'.format(
                settings.EXT_USER_API_ROOT_URL, email), auth=(
                settings.LEDGER_USER, settings.LEDGER_PASS))
        res.raise_for_status()
        data = json.loads(res.content).get('objects')
        if len(data) > 0:
            return data[0]
        else:
            return None
    except BaseException:
        raise


def checkout(
        request,
        application,
        lines=[],
        invoice_text=None,
        vouchers=[],
        internal=False):
    basket_params = {
        'products': lines,
        'vouchers': vouchers,
        'system': settings.WC_PAYMENT_SYSTEM_ID,
        'custom_basket': True,
    }
    basket, basket_hash = create_basket_session(request, basket_params)

    checkout_params = {
        'system': settings.WC_PAYMENT_SYSTEM_ID,
        'fallback_url': request.build_absolute_uri('/'),
        'return_url': request.build_absolute_uri(
            reverse('external-application-success-invoice')),
        'return_preload_url': request.build_absolute_uri('/'),
        'force_redirect': True,
        'proxy': True if internal else False,
        'invoice_text': invoice_text}
    print(' -------- main utils > checkout > checkout_params ---------- ')
    print(checkout_params)
    create_checkout_session(request, checkout_params)

    if internal:
        response = place_order_submission(request)
    else:
        response = HttpResponseRedirect(reverse('checkout:index'))
        # inject the current basket into the redirect response cookies
        # or else, anonymous users will be directionless
        response.set_cookie(
            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
        )

    return response


def internal_create_application_invoice(application, reference):
    from wildlifecompliance.components.applications.models import ApplicationInvoice
    try:
        Invoice.objects.get(reference=reference)
    except Invoice.DoesNotExist:
        raise Exception(
            "There was a problem attaching an invoice for this application")
    app_inv = ApplicationInvoice.objects.create(
        application=application, invoice_reference=reference)
    return app_inv


def set_session_application(session, application):
    print('setting session application')
    session['wc_application'] = application.id
    session.modified = True


def get_session_application(session):
    print('getting session application')
    from wildlifecompliance.components.applications.models import Application
    if 'wc_application' in session:
        application_id = session['wc_application']
    else:
        raise Exception('Application not in Session')

    try:
        return Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        raise Exception(
            'Application not found for application_id {}'.format(application_id))


def delete_session_application(session):
    print('deleting session application')
    if 'wc_application' in session:
        del session['wc_application']
        session.modified = True


def bind_application_to_invoice(request, application, invoice_ref):
    from wildlifecompliance.components.applications.models import ApplicationInvoice
    logger = logging.getLogger('application_checkout')
    try:
        inv = Invoice.objects.get(reference=invoice_ref)
    except Invoice.DoesNotExist:
        logger.error(
            u'{} tried making an application with an incorrect invoice'.format(
                u'User {} with id {}'.format(
                    application.submitter.get_full_name(),
                    application.submitter.id) if application.submitter else u'An anonymous user'))
        raise BindApplicationException

    if inv.system not in ['0999']:
        logger.error(
            u'{} tried making an application with an invoice from another system with reference number {}'.format(
                u'User {} with id {}'.format(
                    application.submitter.get_full_name(),
                    application.submitter.id) if application.submitter else u'An anonymous user',
                inv.reference))
        raise BindApplicationException

    try:
        a = ApplicationInvoice.objects.get(invoice_reference=invoice_ref)
        logger.error(
            u'{} tried making an application with an already used invoice with reference number {}'.format(
                u'User {} with id {}'.format(
                    application.submitter.get_full_name(),
                    application.submitter.id) if application.submitter else u'An anonymous user',
                a.invoice_reference))
        raise BindApplicationException
    except ApplicationInvoice.DoesNotExist:
        logger.info(
            u'{} submitted application {}, creating new ApplicationInvoice with reference {}'.format(
                u'User {} with id {}'.format(
                    application.submitter.get_full_name(),
                    application.submitter.id) if application.submitter else u'An anonymous user',
                application.id,
                invoice_ref))
        app_inv, created = ApplicationInvoice.objects.get_or_create(
            application=application, invoice_reference=invoice_ref)
        application.save()

        request.session['wc_last_application'] = application.id

        # send out the invoice before the confirmation is sent
        # send_application_invoice(application)
        # for fully paid applications, fire off confirmation email
        # if application.paid:
        #    send_application_confirmation(application, request)


def get_choice_value(key, choices):
    try:
        return [choice[1] for choice in choices if choice[0] == key][0]
    except IndexError:
        logger = logging.getLogger(__name__)
        logger.error("Key %s does not exist in choices: %s" % (key, choices))
        raise
