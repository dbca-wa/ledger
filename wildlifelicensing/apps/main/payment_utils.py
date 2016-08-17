import json
import requests
import datetime
from dateutil.relativedelta import relativedelta, FR
import pytz

from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.http import urlencode
from django.views.generic.base import RedirectView, View
from django import forms
from django.contrib import messages
from django.utils import timezone

from ledger.catalogue.models import Product
from ledger.payments.invoice.models import Invoice
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder

PAYMENT_SYSTEM_ID = 'S369'

PAYMENT_STATUS_PAID = 'paid'
PAYMENT_STATUS_CC_READY = 'cc_ready'
PAYMENT_STATUS_AWAITING = 'awaiting'
PAYMENT_STATUS_NOT_REQUIRED = 'not_required'

PAYMENT_STATUSES = {
    PAYMENT_STATUS_PAID: 'Paid',
    PAYMENT_STATUS_CC_READY: 'Credit Card Ready',
    PAYMENT_STATUS_AWAITING: 'Awaiting Payment',
    PAYMENT_STATUS_NOT_REQUIRED: 'Payment Not Required',
}

JSON_REQUEST_HEADER_PARAMS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def to_json(data):
    return json.dumps(data, cls=WildlifeLicensingJSONEncoder)


def get_product(application):
    try:
        return Product.objects.get(title=application.licence_type.code_slug)
    except Product.DoesNotExist:
        return None


def get_application_payment_status(application):
    """

    :param application:
    :return: One of PAYMENT_STATUS_PAID, PAYMENT_STATUS_CC_READY, PAYMENT_STATUS_AWAITING or PAYMENT_STATUS_NOT_REQUIRED
    """
    if not application.invoice_reference:
        return PAYMENT_STATUS_NOT_REQUIRED

    invoice = get_object_or_404(Invoice, reference=application.invoice_reference)

    if invoice.amount > 0:
        payment_status = invoice.payment_status

        if payment_status == 'paid' or payment_status == 'over_paid':
            return PAYMENT_STATUS_PAID
        elif invoice.token:
            return PAYMENT_STATUS_CC_READY
        else:
            return PAYMENT_STATUS_AWAITING
    else:
        return PAYMENT_STATUS_NOT_REQUIRED


def invoke_credit_card_payment(application):
    invoice = get_object_or_404(Invoice, reference=application.invoice_reference)

    if not invoice.token:
        raise Exception('Application invoice does have a credit payment token')

    invoice.make_payment()


class CheckoutApplicationView(RedirectView):
    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[0])
        product = get_product(application)
        user = application.applicant_profile.user.id

        error_url = request.build_absolute_uri(
            reverse('wl_applications:preview', args=(application.licence_type.code_slug, application.id,)))
        success_url = request.build_absolute_uri(
            reverse('wl_applications:complete', args=(application.licence_type.code_slug, application.id,)))

        parameters = {
            'system': PAYMENT_SYSTEM_ID,
            'basket_owner': user,
            'associateInvoiceWithToken': True,
            'checkoutWithToken': True,
            'fallback_url': error_url,
            'return_url': success_url,
            'forceRedirect': True,
            "products": [
                {"id": product.id}
            ]
        }

        url = request.build_absolute_uri(
            reverse('payments:ledger-initial-checkout')
        )

        response = requests.post(url, headers=JSON_REQUEST_HEADER_PARAMS, cookies=request.COOKIES,
                                 data=json.dumps(parameters))

        return HttpResponse(response.content)


class ManualPaymentView(RedirectView):
    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[0])

        url = reverse('payments:invoice-payment', args=(application.invoice_reference,))

        params = {
            'redirect_url': request.GET.get('redirect_url', reverse('wl_home'))
        }

        return redirect('{}?{}'.format(url, urlencode(params)))


class PaymentsReportForm(forms.Form):
    date_format = '%d/%m/%Y %H:%M:%S'
    start = forms.DateTimeField(required=True, widget=forms.DateTimeInput(
        format=date_format
    ))
    end = forms.DateTimeField(required=True, widget=forms.DateTimeInput(
        format=date_format
    ))

    def __init__(self, *args, **kwargs):
        super(PaymentsReportForm, self).__init__(*args, **kwargs)
        # initial datetime spec:
        # end set to be the last Friday at 10:00 pm AEST even if it is a Friday
        # start exactly one week before end

        now = timezone.localtime(timezone.now())
        # create a timezone aware datetime at 10:00 pm AEST
        today_ten_pm_aest = timezone.make_aware(
            datetime.datetime(now.year, now.month, now.day, 22, 0),
            timezone=pytz.timezone('Australia/Sydney'))
        # convert to local
        today_ten_pm_aest_local = timezone.localtime(today_ten_pm_aest)
        # back to previous friday (even if we are friday)
        delta = relativedelta(weekday=FR(-1)) \
            if today_ten_pm_aest_local.weekday() != FR.weekday else relativedelta(weekday=FR(-2))
        end = today_ten_pm_aest_local + delta
        start = end + relativedelta(weeks=-1)

        self.fields['start'].initial = start
        self.fields['end'].initial = end


class PaymentsReportView(View):
    success_url = reverse_lazy('wl_reports:reports')
    error_url = success_url

    def get(self, request):
        form = PaymentsReportForm(request.GET)
        if form.is_valid():
            start = form.cleaned_data.get('start')
            end = form.cleaned_data.get('end')
            # here start and end should be timezone aware (with the settings.TIME_ZONE
            start = timezone.make_aware(start) if not timezone.is_aware(start) else start
            end = timezone.make_aware(end) if not timezone.is_aware(end) else end
            url = request.build_absolute_uri(
                reverse('payments:ledger-report')
            )
            data = {
                'system': PAYMENT_SYSTEM_ID,
                'start': start,
                'end': end
            }
            response = requests.post(url,
                                     headers=JSON_REQUEST_HEADER_PARAMS,
                                     cookies=request.COOKIES,
                                     data=to_json(data))
            if response.status_code == 200:
                filename = 'wl_payments-{}_{}'.format(
                    str(start.date()),
                    str(end.date())
                )
                response = HttpResponse(response, content_type='text/csv; charset=utf-8')
                response['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
                return response
            else:
                messages.error(request,
                               "There was an error while generating the payment report:<br>{}".format(response.content))
                return redirect(self.error_url)
        else:
            messages.error(request, form.errors)
            return redirect(self.error_url)
