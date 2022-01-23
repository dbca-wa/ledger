import json
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from wsgiref.util import FileWrapper
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route,detail_route

from ledger.payments.bpay.models import BpayTransaction, BpayFile, BpayCollection
from ledger.payments.invoice.models import Invoice, InvoiceBPAY
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
from ledger.payments.cash.models import CashTransaction, Region, District, DISTRICT_CHOICES, REGION_CHOICES
from ledger.payments.models import TrackRefund, LinkedInvoice, OracleAccountCode, RefundFailed, OracleInterfaceSystem
from ledger.payments.utils import systemid_check, update_payments 
from ledger.payments.invoice import utils as invoice_utils
from ledger.payments.facade import bpoint_facade
from ledger.payments.reports import generate_items_csv, generate_trans_csv, generate_items_csv_allocated
from ledger.payments.emails import send_refund_email
from ledger.payments import helpers
from django.db.models import Q

from ledger.accounts.models import EmailUser
from ledger.order import models as order_model 
from oscar.apps.order.models import Order
from oscar.apps.payment import forms
from decimal import Decimal
from confy import env
from datetime import datetime
import traceback
import six

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
#######################################################
#                                                     #
#                        BPAY                         #
#                                                     #
#######################################################
class BpayTransactionSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    payment_instruction = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    entry_method = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    payment_date = serializers.DateTimeField(source='p_date', format='%Y-%m-%d %H:%M:%S')
    reason_for_refund_or_reversal = serializers.SerializerMethodField()
    class Meta:
        model = BpayTransaction
        fields = (
            "id",
            "created",
            "amount",
            "type",
            "cheque_num",
            "crn",
            "txn_ref",
            "service_code",
            "payment_instruction",
            "payment_method",
            "payment_date",
            "entry_method",
            "orig_ref_num",
            "reason_for_refund_or_reversal",
            "discretionary_data",
            "payer_name",
            "country",
            "state",
            "car",
            "discount_ref",
            "discount_method",
            "approved",
            "matched",
            "linked",
            "biller_code"
        )

    def get_type(self, obj):
        return dict(BpayTransaction.TRANSACTION_TYPE).get(obj.type)

    def get_payment_instruction(self, obj):
        return dict(BpayTransaction.PAYMENT_INSTRUCTION_CODES).get(obj.p_instruction_code)

    def get_payment_method(self, obj):
        return dict(BpayTransaction.PAYMENT_METHOD_CODES).get(obj.p_method_code)

    def get_entry_method(self, obj):
        return dict(BpayTransaction.ENTRY_METHODS).get(obj.entry_method)

    def get_reason_for_refund_or_reversal(self, obj):
        return dict(BpayTransaction.REF_REV_CODE).get(obj.ref_rev_code)

class BpayTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BpayTransaction.objects.all()
    serializer_class = BpayTransactionSerializer
    renderer_classes = (JSONRenderer,)
    search_fields = (
        '=crn',
    )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        sorting = request.GET.get('sorting',None)
        if sorting and sorting.lower() == 'unmatched':
            queryset = [q for q in queryset if not q.matched]
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)

class BpayFileSerializer(serializers.ModelSerializer):
    #date_modifier = serializers.SerializerMethodField()
    transactions = BpayTransactionSerializer(many=True)
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    #settled = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = BpayFile
        fields = (
            "id",
            "inserted",
            "created",
            "file_id",
            #"settled",
            #"date_modifier",
            #"credit_items",
            #"credit_amount",
            #"cheque_items",
            #"cheque_amount",
            #"debit_amount",
            #"debit_items",
            #"account_total",
            #"account_records",
            #"group_total",
            #"group_accounts",
            #"group_records",
            #"file_total",
            #"file_groups",
            #"file_records",
            "transactions"
        )

    def get_date_modifier(self, obj):
        return dict(BpayFile.DATE_MODIFIERS).get(obj.date_modifier)

class BpayCollectionSerializer(serializers.ModelSerializer):
    created = serializers.DateField(source='date')
    number_of_files = serializers.IntegerField(source='count')

    class Meta:
        model = BpayCollection
        fields = (
            'created',
            'number_of_files',
            'credit_total',
            'cheque_total',
            'debit_total',
            'total'
        )

    def __init__(self,*args,**kwargs):
        try:
            txn_only = kwargs.pop("txns_only")
        except:
            txn_only = False
        super(BpayCollectionSerializer,self).__init__(*args, **kwargs)

        if txn_only:
            self.fields['transactions'] = BpayTransactionSerializer(many=True,read_only=True)
        else:
            self.fields['files'] = BpayFileSerializer(many=True)

class BpayCollectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BpayCollection.objects.all()
    serializer_class = BpayCollectionSerializer
    renderer_classes = (JSONRenderer,)
    lookup_field = 'created'

    def retrieve(self, request, created=None, format=None):
        try:
            instance = BpayCollection.objects.get(date=created)
            txns_only = bool(request.GET.get('transactions',False))
            serializer = BpayCollectionSerializer(instance,txns_only=txns_only)
            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))


class BpayFileList(viewsets.ReadOnlyModelViewSet):
    queryset = BpayFile.objects.all()
    serializer_class = BpayFileSerializer
    renderer_classes = (JSONRenderer,)

#######################################################
#                                                     #
#                       /BPAY                         #
#                                                     #
#######################################################

#######################################################
#                                                     #
#                        BPOINT                       #
#                                                     #
#######################################################
class BpointTransactionSerializer(serializers.ModelSerializer):
    order = serializers.CharField(source='order.number')
    cardtype = serializers.SerializerMethodField()
    settlement_date = serializers.DateField(format='%B, %d %Y')
    source = serializers.CharField(source='type')
    crn = serializers.CharField(source='crn1')
    last_digits = serializers.SerializerMethodField()
    def get_cardtype(self, obj):
        return dict(BpointTransaction.CARD_TYPES).get(obj.cardtype)

    def get_last_digits(self,obj):
        return obj.last_digits

    class Meta:
        model = BpointTransaction
        fields = (
            'id',
            'action',
            'crn',
            'source',
            'amount',
            'amount_surcharge',
            'cardtype',
            'order',
            'txn_number',
            'original_txn',
            'receipt_number',
            'response_code',
            'response_txt',
            'processed',
            'settlement_date',
            'approved',
            'last_digits',
            'refundable_amount'
        )

class AmountSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    details = serializers.CharField(trim_whitespace=True)

class BpointTransactionViewSet(viewsets.ModelViewSet):
    queryset = BpointTransaction.objects.all()
    serializer_class = BpointTransactionSerializer
    renderer_classes = (JSONRenderer,)

    def create(self,request):
        pass

    @detail_route(methods=['POST'])
    def refund(self,request,*args,**kwargs):
        try:
            http_status = status.HTTP_200_OK
            instance = self.get_object()
            serializer = AmountSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            refund = instance.refund(serializer.validated_data,request.user)
            invoice = Invoice.objects.get(reference=instance.crn1)
            update_payments(invoice.reference)
            serializer = BpointTransactionSerializer(refund)
            return Response(serializer.data,status=http_status)
        except serializers.ValidationError:
            traceback.print_exc()
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))


class CardSerializer(serializers.Serializer):
    cardholdername = serializers.CharField(required=False,max_length=50)
    number = serializers.CharField(min_length=13,max_length=16)
    cvn = serializers.CharField(min_length=3,max_length=4)
    expiry = serializers.DateField(input_formats=['%m%Y',])

class BpointPaymentSerializer(serializers.Serializer):
    invoice = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2,required=False)
    card = CardSerializer(required=False)
    using_token = serializers.BooleanField(default=False)
    token = serializers.CharField(max_length=16, required=False)
    original_txn = serializers.CharField(max_length=50,required=False)
    action = serializers.ChoiceField(choices=BpointTransaction.ACTION_TYPES, default='payment')
    subtype = serializers.ChoiceField(choices=BpointTransaction.SUB_TYPES,default='single')
    type = serializers.ChoiceField(choices=BpointTransaction.TRANSACTION_TYPES)

    def validate(self, data):
        if data.get('using_token') and data.get('token') and data.get('card'):
            raise serializers.ValidationError("You can only use one method to make payments ie 'card' or 'token'.")

        if data['action'] in ['payment','preauth','unmatched_refund'] and not data.get('using_token') and not data.get('card'):
            raise serializers.ValidationError("For the selected action you need to provide 'card' details.")

        if data['action'] in ['payment','preauth','unmatched_refund'] and data.get('using_token') and not data.get('token'):
            raise serializers.ValidationError("You need to supply a stored card token if you are paying using the token.")

        if data['action'] in ['refund','capture','reversal'] and not data.get('original_txn'):
            raise serializers.ValidationError("For the selected action you need to provide the transaction number of the transaction matched to this one.")
        return data

class BpointPaymentCreateView(generics.CreateAPIView):
    ''' Used to create a card point using the api:
        Example of json request using new card:
        {
            "invoice": "1000025",
            "amount": 1,
            "action": "payment",
            "type": "internet",
            "card": {
                "number": "4444333322221111",
                "cvn": "123",
                "expiry": "052017"
            }
        }
        Example of json request using stored card:
        {
            "invoice": "1000025",
            "amount": 1,
            "action": "payment",
            "type": "internet",
            "using_token": "true",
            "token": "<token_id"
            }
        }
    '''
    serializer_class = BpointPaymentSerializer
    renderer_classes = (JSONRenderer,)

    class Bankcard(object):
        def __init__(self,number,cvn,expiry,name=None):
            self.name = name
            self.number = number
            self.cvn = cvn
            self.expiry = expiry

    def create(self, request):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            serializer = BpointPaymentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            txn,res,card, invoice_number, total,original_txn, reference = None, None, None, None, None, None, None
            # Get the optional paramters for the transaction
            if serializer.validated_data.get('amount'): total = serializer.validated_data['amount']
            if serializer.validated_data.get('original_txn'): original_txn = serializer.validated_data['original_txn']
            #Get card details if it is there
            if serializer.validated_data.get('card'):
                card_data = serializer.validated_data['card']
                card = self.Bankcard(
                    card_data.get('number'),
                    card_data.get('cvn'),
                    card_data.get('expiry').strftime("%m%Y")
                )
            # Check if the invoice exists if action is payment,preauth
            try:
                inv = Invoice.objects.get(reference=serializer.validated_data['invoice'])
                reference = inv.reference
            except Invoice.DoesNotExist:
                raise serializers.ValidationError("The invoice doesn't exist.")
            if not total and serializer.validated_data['action'] in ['payment','preauth','unmatched_refund']:
                total = inv.amount
            # intialize the bpoint facade object
            facade = bpoint_facade

            if card:
                # Create card form data
                form_data = {
                    'expiry_month_0': card.expiry[:2],
                    'expiry_month_1': card.expiry[2:],
                    'ccv': card.cvn,
                    'number': card.number
                }
                # Validate card data using BankcardForm from oscar payments
                bankcard_form = forms.BankcardForm(form_data)
                if not bankcard_form.is_valid():
                    errors = bankcard_form.errors
                    for e in errors:
                        raise serializers.ValidationError(errors.get(e)[0])
                txn = facade.post_transaction(
                    serializer.validated_data['action'],
                    serializer.validated_data['type'],
                    serializer.validated_data['subtype'],
                    inv.order_number,
                    reference,
                    total,
                    bankcard_form.bankcard,
                    original_txn
                )
            elif serializer.validated_data.get('using_token'):
                # Get the token
                try:
                    token = BpointToken.objects.get(id=serializer.validated_data.get('token'))
                except BpointToken.DoesNotExist:
                    raise serializers.ValidationError("The selected stored card doesn't exist.")
                txn = facade.pay_with_storedtoken(
                    serializer.validated_data['action'],
                    serializer.validated_data['type'],
                    serializer.validated_data['subtype'],
                    serializer.validated_data.get('token'),
                    inv.order_number,
                    reference,
                    total,
                    original_txn
                )
            res = BpointTransactionSerializer(BpointTransaction.objects.get(txn_number=txn.txn_number))

            return Response(res.data)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))

#######################################################
#                                                     #
#                       /BPOINT                       #
#                                                     #
#######################################################

#######################################################
#                                                     #
#                        CASH                         #
#                                                     #
#######################################################
class CashSerializer(serializers.ModelSerializer):
    original_txn = serializers.CharField(required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2,required=False)
    details = serializers.CharField(allow_null=True,allow_blank=True,required=False)
    invoice = serializers.CharField(source='invoice.reference')
    external = serializers.BooleanField(default=False)
    region = serializers.CharField(required=False)
    district = serializers.CharField(required=False)
    class Meta:
        model = CashTransaction
        fields = (
            'invoice',
            'amount',
            'source',
            'created',
            'type',
            'external',
            'region',
            'district',
            'receipt',
            'original_txn',
            'details'
        )

    def validate(self,data):
        if data['external'] and not (data.get('region') or data.get('district')):
            raise serializers.ValidationError('A region/district must be specified for an external payment.')
        if data['type'] == 'refund' and not data['details']:
            raise serializers.ValidationError('details are required for a refund')
        return data

class CashViewSet(viewsets.ModelViewSet):
    '''Used to create a cash payment using the api:
        Example of json request:
        {
            "invoice": "1000025",
            "amount": 1,
            "details" : "refund details"
            "type": "payment"
            "source": "cash"
        }
    '''
    queryset = CashTransaction.objects.all()
    serializer_class = CashSerializer

    def create(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            serializer = CashSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            invoice,txn = None, None
            #Check if the invoice being paid for exists
            # Check if the invoice exists if action is payment,preauth
            try:
                invoice = Invoice.objects.get(reference=serializer.validated_data['invoice']['reference'])
                serializer.validated_data['invoice'] = invoice
            except Invoice.DoesNotExist:
                raise serializers.ValidationError("The invoice doesn't exist.")
            # Check if the amount was specified otherwise pay the whole amount
            if not serializer.validated_data.get('amount'):
                serializer.validated_data['amount'] = invoice.amount
            with transaction.atomic():
                txn = serializer.save()
                if txn.type == 'refund':
                    TrackRefund.objects.create(user=request.user,type=1,refund_id=txn.id,details=serializer.validated_data['details'])
                    send_refund_email(invoice,'manual',txn.amount)
                update_payments(invoice.reference)

            LEDGER_INVOICE_TRANSACTION_CALLBACK_MODULE =env('LEDGER_INVOICE_TRANSACTION_CALLBACK_MODULE', '')
            if len(LEDGER_INVOICE_TRANSACTION_CALLBACK_MODULE) != 0:
                try:
                    ltc = LEDGER_INVOICE_TRANSACTION_CALLBACK_MODULE.split(":")
                    exec('import '+str(ltc[0]))
                    exec(ltc[1]+"('"+invoice.reference+"')")
                except Exception as e:
                    print (e)

            http_status = status.HTTP_201_CREATED
            serializer = CashSerializer(txn)
            return Response(serializer.data,status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
            if '__all__' in e.error_dict:
                raise serializers.ValidationError(str(e.error_dict['__all__'][0]).replace('[','').replace(']',''))
            else:
                raise serializers.ValidationError(str(''.join(e.error_dict.values()[0][0])))
        except Exception as e:
            raise serializers.ValidationError(str(e[0]))

class DistrictSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    code = serializers.CharField(source='name')
    class Meta:
        model = District
        fields = ('name','code')

    def get_name(self, obj):
        return dict(DISTRICT_CHOICES).get(obj.name)

class RegionSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True)
    name = serializers.SerializerMethodField()
    code = serializers.CharField(source='name')
    class Meta:
        model = Region
        fields = (
            'name',
            'code',
            'districts'
        )

    def get_name(self, obj):
        return dict(REGION_CHOICES).get(obj.name)

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    lookup_field = 'name'

#######################################################
#                                                     #
#                       /CASH                         #
#                                                     #
#######################################################

#######################################################
#                                                     #
#                     INVOICE                         #
#                                                     #
#######################################################
class InvoiceTransactionSerializer(serializers.ModelSerializer):
    cash_transactions=CashSerializer(many=True)
    bpay_transactions=BpayTransactionSerializer(many=True)
    bpoint_transactions=BpointTransactionSerializer(many=True)
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    owner = serializers.CharField(source='owner.email')
    refundable_cards=BpointTransactionSerializer(many=True)
    class Meta:
        model = Invoice
        fields = (
            'id',
            'owner',
            'voided',
            'order_number',
            'num_items',
            'amount',
            'reference',
            'created',
            'balance',
            'refundable',
            'refundable_amount',
            'single_card_payment',
            'payment_amount',
            'payment_status',
            'cash_transactions',
            'bpay_transactions',
            'bpoint_transactions',
            'refundable_cards'
        )
        read_only_fields=(
            'created',
            'id',
            'num_items'
        )

class BpayLinkSerializer(serializers.Serializer):
    bpay = serializers.IntegerField()
    link = serializers.BooleanField(default=True)

    def validate_bpay(self,val):
        try:
            BpayTransaction.objects.get(id=val)
        except BpayTransaction.DoesNotExist:
            raise serializers.ValidationError('The bpay transaction entered does not exist.')

        return val

class InvoiceTransactionViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceTransactionSerializer
    lookup_field = 'reference'

    @detail_route(methods=['get'])
    def linked_bpay(self, request, *args, **kwargs):
        try:
            invoice = self.get_object()

            # Get all linked bpay transactions
            linked = InvoiceBPAY.objects.filter(invoice=invoice).values('bpay')
            txns = BpayTransaction.objects.filter(id__in=linked)
            serializer = BpayTransactionSerializer(txns, many=True)

            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(e)

    @detail_route(methods=['get'])
    def payments(self, request, *args, **kwargs):
        try:
            invoice = self.get_object()

            # Get all linked bpay transactions
            payments = []
            #cash
            cash = invoice.cash_transactions.all()
            for c in cash:
                payments.append(
                    {
                        'date':c.created.strftime('%d/%m/%Y'),
                        'type':c.get_source_display().lower().title() if c.type != 'refund' else 'Manual',
                        'details':"{}{}".format(c.get_type_display().lower().title(),": {}".format(c.details) if c.details else ''),
                        'amount':'$ {}'.format(c.amount) if c.type not in ['refund','move_out'] else '$ -{}'.format(c.amount)
                    })
            #bpay
            bpay = invoice.bpay_transactions
            for b in bpay:
                payments.append(
                    {
                        'date':b.p_date.strftime('%d/%m/%Y'),
                        'type': 'Bpay',
                        'details':b.get_p_instruction_code_display().lower().title(),
                        'amount':'$ {}'.format(b.amount)
                    }
                )
            #bpoint
            bpoint = invoice.bpoint_transactions.filter(response_code=0)
            for b in bpoint:
                payments.append(
                    {
                        'date':b.processed.strftime('%d/%m/%Y'),
                        'type': 'Credit Card',
                        'details':b.get_action_display().lower().title(),
                        'amount':'$ {}'.format(b.amount) if b.action != 'refund' else '$ -{}'.format(b.amount)
                    }
                )


            return Response(payments)
        except serializers.ValidationError:
            traceback.print_exc()
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(e)

    @detail_route(methods=['post'])
    def link(self, request, *args, **kwargs):
        try:
            invoice = self.get_object()
            serializer = BpayLinkSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            bpay = BpayTransaction.objects.get(id=serializer.validated_data['bpay'])


            link = serializer.validated_data['link']
            if link:
                if bpay.matched or bpay.linked:
                    raise serializers.ValidationError('This BPAY transaction has already been linked to another invoice.')
                # Create a link between invoice and bpay txn
                try:
                    InvoiceBPAY.objects.create(bpay=bpay,invoice=invoice)
                except Exception:
                    raise
            else:
                # Delete the link between invoice and txn
                try:
                    b= InvoiceBPAY.objects.get(bpay=bpay,invoice=invoice)
                    b.delete()
                except Exception:
                    raise

            # Get all linked bpay transactions
            linked = InvoiceBPAY.objects.filter(invoice=invoice).values('bpay')
            txns = BpayTransaction.objects.filter(id__in=linked)
            serializer = BpayTransactionSerializer(txns, many=True)

            return Response(serializer.data)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(e)

#######################################################
#                                                     #
#                    /INVOICE                         #
#                                                     #
#######################################################
#######################################################
#                                                     #
#                    REPORTS                          #
#                                                     #
#######################################################

class ReportSerializer(serializers.Serializer):
    system = serializers.CharField(max_length=4)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    banked_start = serializers.DateTimeField(required=False,allow_null=True)
    banked_end = serializers.DateTimeField(required=False,allow_null=True)
    region = serializers.ChoiceField(required=False,allow_null=True,choices=REGION_CHOICES)
    district = serializers.ChoiceField(required=False,allow_null=True,choices=DISTRICT_CHOICES)
    items = serializers.BooleanField(default=False)

    '''def validate_system(self,value):
        try:
            if not is_valid_system(value):
                raise serializers.ValidationError('This is not a valid system.')
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value'''

    def validate(self,data):
        if data['items'] and not (data['banked_start'] and data['banked_end']):
            raise serializers.ValidationError('banked_start and banked_end are required for items csv. ')
        return data

class ReportCreateView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            report = None
            data = {
                "start":request.GET.get('start'),
                "end":request.GET.get('end'),
                "banked_start":request.GET.get('banked_start',None),
                "banked_end":request.GET.get('banked_end',None),
                "system":request.GET.get('system'),
                "items": request.GET.get('items', False),
                "region": request.GET.get('region'),
                "district": request.GET.get('district')
            }
            serializer = ReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'report-{}-{}'.format(str(serializer.validated_data['start']),str(serializer.validated_data['end']))
            # Generate Report
            if serializer.validated_data['items']:
                report = generate_items_csv(systemid_check(serializer.validated_data['system']),
                                            serializer.validated_data['start'],
                                            serializer.validated_data['end'],
                                            serializer.validated_data['banked_start'],
                                            serializer.validated_data['banked_end'],
                                            district = serializer.validated_data['district'])
            else:
                report = generate_trans_csv(systemid_check(serializer.validated_data['system'])
                                            ,serializer.validated_data['start'],
                                            serializer.validated_data['end'],
                                            district = serializer.validated_data['district'])
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))

class ReportCreateAllocatedView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            report = None
            data = {
                "start":request.GET.get('start'),
                "end":request.GET.get('end'),
                "banked_start":request.GET.get('banked_start',None),
                "banked_end":request.GET.get('banked_end',None),
                "system":request.GET.get('system'),
                "items": request.GET.get('items', False),
                "region": request.GET.get('region'),
                "district": request.GET.get('district')
            }
            serializer = ReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'report-{}-{}'.format(str(serializer.validated_data['start']),str(serializer.validated_data['end']))
            # Generate Report
            if serializer.validated_data['items']:
                report = generate_items_csv_allocated(systemid_check(serializer.validated_data['system']),
                                            serializer.validated_data['start'],
                                            serializer.validated_data['end'],
                                            serializer.validated_data['banked_start'],
                                            serializer.validated_data['banked_end'],
                                            district = serializer.validated_data['district'])
            else:
                report = generate_trans_csv(systemid_check(serializer.validated_data['system'])
                                            ,serializer.validated_data['start'],
                                            serializer.validated_data['end'],
                                            district = serializer.validated_data['district'])
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))


#######################################################
#                                                     #
#                    /REPORTS                         #
#                                                     #
#######################################################

def LedgerPayments(request, *args, **kwargs):
    invoice_group_id = request.GET.get('invoice_group_id',None)
    invoice_no = request.GET.get('invoice_no','')
    booking_reference = request.GET.get('booking_reference','')

    data = {"status": 403, "data": {}} 
    
    if helpers.is_payment_admin(request.user) is True:
        exists = False
        #if invoice_group_id: 
        #    if len(invoice_group_id) > 0:
        #       pass

        if len(invoice_no) > 0:
            link_res = LinkedInvoice.objects.filter(invoice_reference=invoice_no)
            if link_res.count() > 0:
                invoice_group_id = link_res[0].invoice_group_id.id
        elif len(booking_reference) > 0:
            link_res = LinkedInvoice.objects.filter(booking_reference=booking_reference)
            if link_res.count() > 0:
                invoice_group_id = link_res[0].invoice_group_id.id

        if invoice_group_id:
                if int(invoice_group_id) > 0:
                     linkinv = LinkedInvoice.objects.filter(invoice_group_id=invoice_group_id)
                     if linkinv.count() > 0:
                         latest_li = LinkedInvoice.objects.filter(invoice_group_id=invoice_group_id).order_by('-created')[0]
                         linked_payments = []
                         invoices = []
                         invoices_data = []
                         orders = []
                         for li in linkinv:
                             invoices.append(li.invoice_reference)
                             linked_payments.append({'id': li.id, 'invoice_reference': li.invoice_reference, 'system_identifier_id': li.system_identifier.id, 'system_identifier_system': li.system_identifier.system_id, 'booking_reference': li.booking_reference, 'booking_reference_linked': li.booking_reference_linked, 'invoice_group_id': li.invoice_group_id.id})
                         invs = Invoice.objects.filter(reference__in=invoices)
                         for i in invs:
                             orders.append(i.order_number)
                             invoices_data.append({'invoice_reference': i.reference, 'payment_status': str(i.payment_status), 'balance': str(i.balance)})
                         invoice_orders = Order.objects.filter(number__in=orders)
                         order_array = []
                         order_obj = order_model.Line.objects.filter(order__number__in=orders).order_by('order__date_placed')
                         rolling_total = Decimal('0.00')
                         total_unallocated = Decimal('0.00')

                         oracle_code_totals = {}
                         data['data']['oracle_code_totals'] = {}
                         for o in order_obj:
                             if o.oracle_code == 'NNP449 GST':
                                 total_unallocated = total_unallocated + o.line_price_incl_tax
                             rolling_total = rolling_total + o.line_price_incl_tax
                             row = {'id': o.id, 'order_number': o.order.number, 'title': o.title, 'line_price_incl_tax': str(o.line_price_incl_tax), 'oracle_code': o.oracle_code, 'rolling_total': str(rolling_total), 'order_date': o.order.date_placed.strftime("%d/%m/%Y %H:%M:%S")}
                             order_array.append(row)

                             if o.oracle_code not in oracle_code_totals:
                                 oracle_code_totals[o.oracle_code] = Decimal('0.00')
                             oracle_code_totals[o.oracle_code] = oracle_code_totals[o.oracle_code] + o.line_price_incl_tax 

                         for cct in oracle_code_totals.keys():
                             data['data']['oracle_code_totals'][cct] = str(oracle_code_totals[cct])

                         bp_array = []
                         bp_txn_refund_hash = {}
                         bp_trans = BpointTransaction.objects.filter(crn1__in=invoices)
                         for bp in bp_trans:
                             if bp.original_txn not in bp_txn_refund_hash:
                                   bp_txn_refund_hash[bp.original_txn] = Decimal('0.00')
                             if bp.action == 'refund':
                                 bp_txn_refund_hash[bp.original_txn] = bp_txn_refund_hash[bp.original_txn] + bp.amount

                         total_gateway_amount = Decimal('0.00')
                         for bp in bp_trans:
                             if bp.action == 'refund':
                                 total_gateway_amount = total_gateway_amount - bp.amount
                             else:
                                 total_gateway_amount = total_gateway_amount + bp.amount

                             row = {}
                             row['id'] = bp.id
                             row['crn1'] = bp.crn1
                             row['txnnumber'] = bp.txn_number
                             row['original_txn'] = bp.original_txn
                             row['amount'] = str(bp.amount)
                             row['response_code'] = bp.response_code
                             row['action'] = bp.action
                             row['processed'] = bp.processed.strftime("%d/%m/%Y %H:%M:%S")
                             row['response_txt'] = bp.response_txt
                             if bp.action == 'payment':
                                row['amount_refunded'] = '0.00'
                                if bp.txn_number in bp_txn_refund_hash:
                                    row['amount_refunded'] = str(bp_txn_refund_hash[bp.txn_number])
                             bp_array.append(row)


                         cash_array = []
                         cash_array_invoices = {}
                         cash_txn_refund_hash = {}
                         cash_trans = CashTransaction.objects.filter(invoice__in=invs)
                         for c in cash_trans:
                             if c.id not in cash_txn_refund_hash:
                                 cash_txn_refund_hash[c.id] = Decimal('0.00')
                             if c.type == 'refund':
                                 cash_txn_refund_hash[c.id] = cash_txn_refund_hash[c.id] + c.amount
                        
                         total_cash_amount = Decimal('0.00')
                         for ch in cash_trans:
                             if ch.type  == 'refund':
                                   total_cash_amount = total_cash_amount - ch.amount
                             elif ch.type == 'payment':
                                   total_cash_amount = total_cash_amount + ch.amount

                             row = {}
                             row['id'] = ch.id
                             row['invoice_reference'] = ch.invoice.reference
                             row['amount'] = str(ch.amount)
                             row['action'] = ch.type
                             row['source'] = ch.source
                             row['receipt'] = ch.receipt
                             row['details'] = ch.details
                             row['created'] = ch.created.strftime("%d/%m/%Y %H:%M:%S")
                             
                             if ch.type == 'payment':
                                  row['amount_refunded'] = '0.00'
                                  if ch.id in cash_txn_refund_hash:
                                      row['amount_refunded'] = str(cash_txn_refund_hash[ch.id])
                             cash_array.append(row)

                         # cash group by invoice
                         for ch in cash_trans:
                             if ch.invoice.reference not in cash_array_invoices:
                                   cash_array_invoices[ch.invoice.reference] = Decimal('0.00')

                             if ch.type  == 'refund':
                                  cash_array_invoices[ch.invoice.reference] = cash_array_invoices[ch.invoice.reference] - ch.amount
                             if ch.type  == 'payment':
                                  cash_array_invoices[ch.invoice.reference] = cash_array_invoices[ch.invoice.reference] + ch.amount

                         cai = []
                         # convert decimal money to string for json dump    
                         for ca in cash_array_invoices.keys():
                               row = {}
                               row['invoice_reference'] = ca
                               row['amount'] = str(cash_array_invoices[ca])
                               cai.append(row)

                         data['data']['linked_payments'] = linked_payments
                         data['data']['total_gateway_amount'] = str(total_gateway_amount)
                         data['data']['total_cash_amount'] = str(total_cash_amount)
                         data['data']['total_unallocated'] = str(total_unallocated)
                         #data['data']['oracle_code_totals']  
                         data['data']['order'] = order_array
                         data['data']['bpoint'] = bp_array
                         data['data']['cash'] = cash_array
                         data['data']['cash_on_invoices'] = cai
                         data['data']['invoices_data'] = invoices_data
                         data['data']['booking_reference'] = latest_li.booking_reference
                         data['data']['booking_reference_linked'] = latest_li.booking_reference_linked
                         data['status'] = 200
                         exists = True
                     else:
                         data['status'] = 404
                         data['message'] =  "No records found"
                         data['data']['linked_payments'] = []
                         data['data']['total_gateway_amount'] = '0.00'
                         data['data']['total_unallocated'] = '0.00'
                         data['data']['order'] = []
                         data['data']['bpoint'] = []
                         data['data']['booking_reference'] = ''
                         data['data']['booking_reference_linked'] = ''

        else:
            data['status'] = 404
            data['message'] =  "No records found"
            data['data']['linked_payments'] = []
            data['data']['total_gateway_amount'] = '0.00'
            data['data']['total_unallocated'] = '0.00'
            data['data']['order'] = []
            data['data']['bpoint'] = []
            data['data']['booking_reference'] = ''
            data['data']['booking_reference_linked'] = ''

    return HttpResponse(json.dumps(data), content_type='application/json')

def CheckOracleCodeView(request, *args, **kwargs):
    if helpers.is_payment_admin(request.user) is True:
        try:
           oracle_code = request.GET.get('oracle_code','')
           if OracleAccountCode.objects.filter(active_receivables_activities=oracle_code).count() > 0:
                 json_obj = {'found': True, 'code': oracle_code}
           else:
                 json_obj = {'found': False, 'code': oracle_code}
           return HttpResponse(json.dumps(json_obj), content_type='application/json')
        except Exception as e:
           print(traceback.print_exc())
           raise

def FailedTransactionCompleted(request, *args, **kwargs):
    if helpers.is_payment_admin(request.user) is True:
        try:
            rfid = kwargs['rfid']
            rf = RefundFailed.objects.get(id=rfid)
            rf.status = 1
            rf.completed_date = datetime.now() 
            rf.completed_by = request.user
            rf.save()

            return HttpResponse(json.dumps({'status': 200, 'message': 'success'}), content_type='application/json')
        except Exception as e:
            print(traceback.print_exc())
            return HttpResponse(json.dumps({'status': 500, 'message': 'error'}), content_type='application/json', status=500)
            raise

def FailedTransactions(request, *args, **kwargs):
    if helpers.is_payment_admin(request.user) is True:
        try:
            query = Q()
            pagestart = int(request.GET.get('pagestart',0))
            pageend = int(request.GET.get('pageend',10))
            status = request.GET.get('status','')
            system = request.GET.get('system','')
            keyword = request.GET.get('keyword','')
         
            if len(status) > 0:
                query &= Q(status=status)
            if len(system) > 0:
                query &= Q(system_identifier__system_id=system)
            if len(keyword) > 0:
                query &= Q(Q(booking_reference=keyword) | Q(invoice_reference=keyword))
            print (query)
            rf_array = {'status': 404, 'data': {'rows': [], 'totalrows': 0}}  
            rf = RefundFailed.objects.filter(query)[pagestart:pageend]
            rf_array['data']['totalrows'] = RefundFailed.objects.filter(query).count() 

            for r in rf: 
                row = {}
                row['id'] = r.id
                row['invoice_group_id'] = r.invoice_group.id
                row['booking_reference'] = r.booking_reference
                row['invoice_reference'] = r.invoice_reference
                row['refund_amount'] = str(r.refund_amount)
                row['status'] = r.status
                row['status_name'] = r.get_status_display()
                row['system_identifier'] = r.system_identifier.system_id
                row['created'] = r.created.strftime('%d/%m/%Y %H:%M:%S')
                rf_array['data']['rows'].append(row)
            return HttpResponse(json.dumps(rf_array), content_type='application/json')
        except Exception as e:
            print(traceback.print_exc())
            raise

def RefundOracleView(request, *args, **kwargs):
        try:
           if helpers.is_payment_admin(request.user) is True:
                money_from = request.POST.get('money_from',[])
                money_to = request.POST.get('money_to',[])
                bpoint_trans_split= request.POST.get('bpoint_trans_split',[])
                refund_method = request.POST.get('refund_method', None)
                booking_id = request.POST.get('booking_id',None)
                newest_booking_id = request.POST.get('newest_booking_id',None)
                booking_reference = request.POST.get('booking_reference',None)
                booking_reference_linked = request.POST.get('booking_reference_linked',None)

                #booking = Booking.objects.get(pk=newest_booking_id)
                money_from_json = json.loads(money_from)
                money_to_json = json.loads(money_to)
                bpoint_trans_split_json = json.loads(bpoint_trans_split)
                failed_refund = False

                system_id = None
                li = LinkedInvoice.objects.filter(booking_reference=booking_reference)
                if li.count() > 0:
                     system_id = li[0].system_identifier.system_id 

                json_obj = {'found': False, 'code': money_from, 'money_to': money_to, 'failed_refund': failed_refund}
                if len(booking_reference_linked) > 0:
                    pass
                else:
                    booking_reference_linked = booking_reference
                lines = []
                if int(refund_method) == 1:
                    lines = []
                    for mf in money_from_json:
                        if Decimal(mf['line-amount']) > 0:
                            money_from_total = (Decimal(mf['line-amount']) - Decimal(mf['line-amount']) - Decimal(mf['line-amount']))
                            lines.append({'ledger_description':str(mf['line-text']),"quantity":1,"price_incl_tax":money_from_total,"oracle_code":str(mf['oracle-code']), 'line_status': 3})

                    for bp_txn in bpoint_trans_split_json:
                        bpoint_id = BpointTransaction.objects.get(txn_number=bp_txn['txn_number'])
                        info = {'amount': Decimal('{:.2f}'.format(float(bp_txn['line-amount']))), 'details' : 'Refund via system'}
                        if info['amount'] > 0:
                             lines.append({'ledger_description':str("Temp fund transfer "+bp_txn['txn_number']),"quantity":1,"price_incl_tax":Decimal('{:.2f}'.format(float(bp_txn['line-amount']))),"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 1})


                    order = invoice_utils.allocate_refund_to_invoice(request, booking_reference, lines, invoice_text=None, internal=False, order_total='0.00',user=None, booking_reference_linked=booking_reference_linked,system_id=system_id)
                    new_invoice = Invoice.objects.get(order_number=order.number)
                    update_payments(new_invoice.reference)

                    for bp_txn in bpoint_trans_split_json:
                        bpoint_id = None
                        try:
                             bpoint_id = BpointTransaction.objects.get(txn_number=bp_txn['txn_number'])
                             info = {'amount': Decimal('{:.2f}'.format(float(bp_txn['line-amount']))), 'details' : 'Refund via system'}
                        except Exception as e:
                             print ("BPOUNT TRANSACTION EXCEPTION") 
                             print (e)
                             info = {'amount': Decimal('{:.2f}'.format('0.00')), 'details' : 'Refund via system'}

                        refund = None
                        lines = []
                        if info['amount'] > 0:
                            lines = []
                            #lines.append({'ledger_description':str("Temp fund transfer "+bp_txn['txn_number']),"quantity":1,"price_incl_tax":Decimal('{:.2f}'.format(float(bp_txn['line-amount']))),"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 1})

                            try:

                                bpoint_money_to = (Decimal('{:.2f}'.format(float(bp_txn['line-amount']))) - Decimal('{:.2f}'.format(float(bp_txn['line-amount']))) - Decimal('{:.2f}'.format(float(bp_txn['line-amount']))))
                                lines.append({'ledger_description':str("Payment Gateway Refund to "+bp_txn['txn_number']),"quantity":1,"price_incl_tax": bpoint_money_to,"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 3})
                                bpoint = BpointTransaction.objects.get(txn_number=bp_txn['txn_number'])
                                refund = bpoint.refund(info,request.user)
                            except Exception as e:
                                print ("BPOINT REFUND EXECEPTION")
                                print (e)
                                failed_refund = True
                                bpoint_failed_amount = Decimal(bp_txn['line-amount'])
                                lines = []
                                lines.append({'ledger_description':str("Refund failed for txn "+bp_txn['txn_number']),"quantity":1,"price_incl_tax":'0.00',"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 1})
                            order = invoice_utils.allocate_refund_to_invoice(request, booking_reference, lines, invoice_text=None, internal=False, order_total='0.00',user=None, booking_reference_linked=booking_reference_linked, system_id=system_id)
                            new_invoice = Invoice.objects.get(order_number=order.number)

                            if refund:
                               bpoint_refund = BpointTransaction.objects.get(txn_number=refund.txn_number)
                               bpoint_refund.crn1 = new_invoice.reference
                               bpoint_refund.save()
                               new_invoice.settlement_date = None
                               new_invoice.save()
                               update_payments(new_invoice.reference)

                else:
                    lines = []
                    for mf in money_from_json:
                        if Decimal(mf['line-amount']) > 0:
                            money_from_total = (Decimal(mf['line-amount']) - Decimal(mf['line-amount']) - Decimal(mf['line-amount']))
                            lines.append({'ledger_description':str(mf['line-text']),"quantity":1,"price_incl_tax":money_from_total,"oracle_code":str(mf['oracle-code']), 'line_status': 3})


                    for mt in money_to_json:
                        lines.append({'ledger_description':mt['line-text'],"quantity":1,"price_incl_tax":mt['line-amount'],"oracle_code":mt['oracle-code'], 'line_status': 1})
                    order = invoice_utils.allocate_refund_to_invoice(request, booking_reference, lines, invoice_text=None, internal=False, order_total='0.00',user=None,  booking_reference_linked=booking_reference_linked, system_id=system_id)
                    new_invoice = Invoice.objects.get(order_number=order.number)
                    update_payments(new_invoice.reference)

                json_obj['failed_refund'] = failed_refund
                return HttpResponse(json.dumps(json_obj), content_type='application/json')
           else:
                raise serializers.ValidationError('Permission Denied.')

        except Exception as e:
           print ("ERROR Making Oracle Refund Move")
           print (traceback.print_exc())
           raise


