import requests
import json
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission

def retrieve_department_users():
    try:
        res = requests.get('{}/api/users/fast/?compact'.format(settings.EXT_USER_API_ROOT_URL), auth=(settings.LEDGER_USER,settings.LEDGER_PASS))
        res.raise_for_status()
        cache.set('department_users',json.loads(res.content).get('objects'),10800)
    except:
        raise

def get_department_user(email):
    try:
        res = requests.get('{}/api/users?email={}'.format(settings.EXT_USER_API_ROOT_URL,email), auth=(settings.LEDGER_USER,settings.LEDGER_PASS))
        res.raise_for_status()
        data = json.loads(res.content).get('objects')
        if len(data) > 0:
            return data[0]
        else:
            return None
    except:
        raise


def checkout(request, application, lines=[], invoice_text=None, vouchers=[], internal=False):
    lines.append({
                'ledger_description': '{}'.format(application.licence_type_name),
                'quantity': 1,
                'price_incl_tax': str(application.application_fee),
                'oracle_code': ''
    })
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
        'return_url': request.build_absolute_uri(reverse('external-application-success')),
        'return_preload_url': request.build_absolute_uri(reverse('external-application-success')),
        # 'fallback_url': 'https://wildlifecompliance-uat.dpaw.wa.gov.au',
        # 'return_url': 'https://wildlifecompliance-uat.dpaw.wa.gov.au',
        # 'return_preload_url': 'https://wildlifecompliance-uat.dpaw.wa.gov.au',
        'force_redirect': True,
        'proxy': True if internal else False,
        'invoice_text': invoice_text,
    }
    # if not internal:
    #     checkout_params['check_url'] = request.build_absolute_uri(
    #         '/api/applications/{}/application_checkout_status.json'.format(application.id))
    # if internal or request.user.is_anonymous():
    #     checkout_params['basket_owner'] = application.submitter.id
    # checkout_params['check_url'] = 'http://google.com/'
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


def bind_application_to_invoice(request, application, invoice_ref):
    try:
        inv = Invoice.objects.get(reference=invoice_ref)
    except Invoice.DoesNotExist:
        logger.error(u'{} tried making an application with an incorrect invoice'.format(u'User {} with id {}'.format(application.submitter.get_full_name(),application.submitter.id) if application.submitter else u'An anonymous user'))
        raise BindApplicationException

    if inv.system not in ['0999']:
        logger.error(u'{} tried making an application with an invoice from another system with reference number {}'.format(u'User {} with id {}'.format(application.submitter.get_full_name(),application.submitter.id) if application.submitter else u'An anonymous user',inv.reference))
        raise BindApplicationException

    try:
        a = ApplicationInvoice.objects.get(invoice_reference=invoice_ref)
        logger.error(u'{} tried making an application with an already used invoice with reference number {}'.format(u'User {} with id {}'.format(application.submitter.get_full_name(),application.submitter.id) if application.submitter else u'An anonymous user',a.invoice_reference))
        raise BindApplicationException
    except ApplicationInvoice.DoesNotExist:
        logger.info(u'{} submitted application {}, creating new ApplicationInvoice with reference {}'.format(u'User {} with id {}'.format(application.submitter.get_full_name(),application.submitter.id) if application.submitter else u'An anonymous user',application.id, invoice_ref))
        app_inv, created = ApplicationInvoice.objects.get_or_create(application=application, invoice_reference=invoice_ref)
        application.save()

        request.session['wc_last_application'] = application.id

        # send out the invoice before the confirmation is sent
        #send_application_invoice(application)
        # for fully paid applications, fire off confirmation email
        #if application.paid:
        #    send_application_confirmation(application, request)