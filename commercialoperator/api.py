from datetime import datetime, timedelta, date
import traceback
from decimal import *
import json
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from ledger.payments.models import Invoice,OracleInterface,CashTransaction
from ledger.payments.utils import oracle_parser,update_payments
from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission, get_cookie_basket


class PaymentViewSet(viewsets.ModelViewSet):
    #import ipdb; ipdb.set_trace()
    #queryset = Proposal.objects.all()
    queryset = Proposal.objects.none()
    serializer_class = ProposalSerializer
    lookup_field = 'id'

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                request.data['proposal'] = u'{}'.format(instance.id)
                request.data['staff'] = u'{}'.format(request.user.id)
                serializer = ProposalLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def post(self, request, *args, **kwargs):

        try:
            with transaction.atomic():
                instance = self.get_object()
                self.create_lines(request):
                self.checkout(request, booking, lines):

                data = [dict(key='My Response')]
                return Response(data)
                #return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    def create_lines(self, request, invoice_text=None, vouchers=[], internal=False):
        """ Create the ledger lines - line items for invoice sent to payment system """

        lines = []
        for row in request.data.get('tbody'):
            park_id = row[0]['value']
            arrival = row[1]
            no_adults = int(row[2])
            no_children = int(row[3])
            park= Park.objects.get(id=park_id)
            ledger_description = row[1] + '. ' + park.name + ' (' + row[2] + ' Adults' + ')'
            oracle_code = 'ABC123 GST'
            price_incl_tax = str(park.adult * int(no_adults))
            quantity = 1

            if row[1]:
                llines.append(dict(
                    ledger_description = arrival + '. ' + park.name + ' (' + str(no_adults) + ' Adults' + ')',
                    oracle_code = 'ABC123 GST',
                    price_incl_tax = Decimal(park.adult * int(no_adults)),
                    quantity = 1
                ))
                print arrival + '. ' + park.name + '. Adults: ' + str(no_adults) + ', Price: ' + str(park.adult * int(no_adults))

            if row[2]:

                lines.append(dict(
                    ledger_description = arrival + '. ' + park.name + ' (' + str(no_children) + ' Children' + ')',
                    oracle_code = 'ABC123 GST',
                    price_incl_tax = Decimal(park.child * int(no_children)),
                    quantity = 1
                ))
                print arrival + '. ' + park.name + '. Children: ' + str(no_children) + ', Price: ' + str(park.child * int(no_children))


    def checkout(self, request, booking, lines, invoice_text=None, vouchers=[], internal=False):
        import ipdb; ipdb.set_trace()
        basket_params = {
            'products': lines,
            'vouchers': vouchers,
            'system': settings.PS_PAYMENT_SYSTEM_ID,
            'custom_basket': True,
        }

        basket, basket_hash = create_basket_session(request, basket_params)
        checkout_params = {
            'system': settings.PS_PAYMENT_SYSTEM_ID,
            'fallback_url': request.build_absolute_uri('/'),                                      # 'http://mooring-ria-jm.dbca.wa.gov.au/'
            'return_url': request.build_absolute_uri(reverse('public_booking_success')),          # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
            'return_preload_url': request.build_absolute_uri(reverse('public_booking_success')),  # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
            'force_redirect': True,
            'proxy': True if internal else False,
            'invoice_text': invoice_text,                                                         # 'Reservation for Jawaid Mushtaq from 2019-05-17 to 2019-05-19 at RIA 005'
        }
#    if not internal:
#        checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
        if internal or request.user.is_anonymous():
            checkout_params['basket_owner'] = booking.customer.id


        create_checkout_session(request, checkout_params)

#    if internal:
#        response = place_order_submission(request)
#    else:
        response = HttpResponseRedirect(reverse('checkout:index'))
        # inject the current basket into the redirect response cookies
        # or else, anonymous users will be directionless
        response.set_cookie(
                settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
                max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
                secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
        )

#    if booking.cost_total < 0:
#        response = HttpResponseRedirect('/refund-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )
#
#    # Zero booking costs
#    if booking.cost_total < 1 and booking.cost_total > -1:
#        response = HttpResponseRedirect('/no-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )

        return response

