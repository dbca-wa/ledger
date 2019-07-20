from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.http import urlquote_plus

import re
import datetime

from django.http import HttpResponseRedirect
from django.utils import timezone
from commercialoperator.components.bookings.models import ApplicationFee


CHECKOUT_PATH = re.compile('^/ledger/checkout/checkout')

class FirstTimeNagScreenMiddleware(object):
    def process_request(self, request):
        #print ("FirstTimeNagScreenMiddleware: REQUEST SESSION")
        if request.user.is_authenticated() and request.method == 'GET' and 'api' not in request.path and 'admin' not in request.path:
            #print('DEBUG: {}: {} == {}, {} == {}, {} == {}'.format(request.user, request.user.first_name, (not request.user.first_name), request.user.last_name, (not request.user.last_name), request.user.dob, (not request.user.dob) ))
            if (not request.user.first_name) or (not request.user.last_name):# or (not request.user.dob):
                path_ft = reverse('first_time')
                path_logout = reverse('accounts:logout')
                if request.path not in (path_ft, path_logout):
                    return redirect(reverse('first_time')+"?next="+urlquote_plus(request.get_full_path()))
                    

class BookingTimerMiddleware(object):
    def process_request(self, request):
        #print ("BookingTimerMiddleware: REQUEST SESSION")
        #print request.session['ps_booking']
        if 'cols_app_invoice' in request.session:
            #print ("BOOKING SESSION : "+str(request.session['ps_booking']))
            try:
                application_fee = ApplicationFee.objects.get(pk=request.session['cols_app_invoice'])
            except:
                # no idea what object is in self.request.session['ps_booking'], ditch it
                del request.session['cols_app_invoice']
                return
            if application_fee.payment_type != 3:
                # booking in the session is not a temporary type, ditch it
                del request.session['cols_app_invoice']
        return
