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
from ledger.payments.models import TrackRefund
from ledger.payments.utils import systemid_check, update_payments
from ledger.payments.facade import bpoint_facade
from ledger.payments.reports import generate_items_csv, generate_trans_csv, generate_items_csv_allocated
from ledger.payments.emails import send_refund_email

from ledger.accounts.models import EmailUser
from oscar.apps.order.models import Order
from oscar.apps.payment import forms
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
            http_status = status.HTTP_201_CREATED
            serializer = CashSerializer(txn)
            return Response(serializer.data,status=http_status)
        except serializers.ValidationError:
            raise
        except ValidationError as e:
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

