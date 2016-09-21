from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.core.exceptions import ValidationError
from wsgiref.util import FileWrapper
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from ledger.payments.bpay.models import BpayTransaction, BpayFile, BpayCollection
from ledger.payments.invoice.models import Invoice
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
from ledger.payments.cash.models import CashTransaction, Region, District, DISTRICT_CHOICES, REGION_CHOICES
from ledger.payments.utils import checkURL, createBasket, validSystem, systemid_check
from ledger.payments.facade import bpoint_facade
from ledger.payments.reports import generate_items_csv, generate_trans_csv

from ledger.accounts.models import EmailUser
from ledger.accounts.reports import user_report
from ledger.catalogue.models import Product
from oscar.apps.order.models import Order
from oscar.apps.voucher.models import Voucher
from oscar.apps.payment import forms
import traceback

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
            "approved"
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
    authentication_classes = []
    search_fields = (
        '=crn',
    )
    
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
    authentication_classes = []
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
    authentication_classes = []

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
    original_txn = serializers.CharField(source='original_txn.txn_number')
    order = serializers.CharField(source='order.number')
    cardtype = serializers.SerializerMethodField()
    settlement_date = serializers.DateField(format='%B, %d %Y')
    source = serializers.CharField(source='type')
    crn = serializers.CharField(source='crn1')
    def get_cardtype(self, obj):
        return dict(BpointTransaction.CARD_TYPES).get(obj.cardtype)
        
    class Meta:
        model = BpointTransaction
        fields = (
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
            'approved'
        )
    
class BpointTransactionViewSet(viewsets.ModelViewSet):
    queryset = BpointTransaction.objects.all()
    serializer_class = BpointTransactionSerializer
    renderer_classes = (JSONRenderer,)
    authentication_classes = []
    
    def create(self,request):
        pass
    
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
    authentication_classes = []

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
            'original_txn'
        )
        
    def validate(self,data):
        if data['external'] and not (data.get('region') or data.get('district')):
            raise serializers.ValidationError('A region/district must be specified for an external payment.')
        return data

class CashViewSet(viewsets.ModelViewSet):
    '''Used to create a cash payment using the api:
        Example of json request:
        {
            "invoice": "1000025",
            "amount": 1,
            "type": "payment"
            "source": "cash"
        }
    '''
    queryset = CashTransaction.objects.all()
    serializer_class = CashSerializer
    authentication_classes = []
    
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
            txn = serializer.save()
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
    class Meta:
        model = Invoice
        fields = (
            'id',
            'owner',
            'order_number',
            'num_items',
            'amount',
            'reference',
            'created',
            'payment_amount',
            'payment_status',
            'cash_transactions',
            'bpay_transactions',
            'bpoint_transactions'
        )
        read_only_fields=(
            'created',
            'id',
            'num_items'
        )
    
class InvoiceTransactionViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceTransactionSerializer
    authentication_classes = []
    lookup_field = 'reference'

#######################################################
#                                                     #
#                    /INVOICE                         #
#                                                     #
#######################################################

#######################################################
#                                                     #
#                    CHECKOUT                         #
#                                                     #
#######################################################
class CheckoutProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1,default=1)

    def validate_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist as e:
            raise serializers.ValidationError('{} (id={})'.format(str(e),value))
        return value

class VoucherSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=128)

    def validate_code(self, value):
        try:
            Voucher.objects.get(code=value)
        except Voucher.DoesNotExist as e:
            raise serializers.ValidationError('{} (code={})'.format(str(e),value))
        return value

class CheckoutSerializer(serializers.Serializer):
    card_method = serializers.ChoiceField(choices=BpointTransaction.ACTION_TYPES, default='payment')
    system = serializers.CharField(max_length=4, min_length=4)
    basket_owner = serializers.IntegerField(required=False)
    template = serializers.CharField(required=False)
    fallback_url = serializers.URLField()
    return_url = serializers.URLField()
    associateInvoiceWithToken = serializers.BooleanField(default=False)
    forceRedirect = serializers.BooleanField(default=False)
    sendEmail = serializers.BooleanField(default=False)
    proxy = serializers.BooleanField(default=False)
    checkoutWithToken = serializers.BooleanField(default=False)
    bpay_format = serializers.ChoiceField(choices=['crn','icrn'],default='crn')
    icrn_format = serializers.ChoiceField(choices=['ICRNAMT','ICRNDATE','ICRNAMTDATE'], default='ICRNAMT')
    products = CheckoutProductSerializer(many=True)
    vouchers = VoucherSerializer(many=True,required=False)

    def validate(self, data):
        if data['proxy'] and not data['basket_owner']:
            raise serializers.ValidationError('A proxy payment requires the basket_owner to be set.')
        return data
    def validate_template(self, value):
        try:
            get_template(value)
        except TemplateDoesNotExist as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_system(self, value):
        try:
            if not validSystem(value):
                raise serializers.ValidationError('This is not a valid system')
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_basket_owner(self, value):
        try:
            EmailUser.objects.get(id=value)
        except EmailUser.DoesNotExist as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_fallback_url(self,value):
        try:
            checkURL(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_return_url(self,value):
        try:
            checkURL(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

class CheckoutCreateView(generics.CreateAPIView):
    ''' Initiate checkout process.
    :return: HTTPResponseRedirect
    Example:
    {
        "card_method": "payment", (optional, default='payment')
        "template": "", (optional)
        "system": "", (mandatory)
        "fallback_url": "http://", (mandatory)
        "return_url": "http://", (mandatory)
        "associateInvoiceWithToken": "true", (optional, default=False)
        "forceRedirect": "true", (optional, default=False)
        "sendEmail": "false", (optional, default=False)
        "checkoutWithToken": "true", (optional, default=False)
        "bpay_format": "crn", (optional, default='crn')
        "proxy": "true", (optional, default=False)
        "icrn_format": "ICRNAMT", (optional, default='ICRNAMT')
        "products": [ (mandatory)
            {"id": 1}
        ]
        "vouchers": [ (optional)
            {"code": "<code>}
        ]
    }
    '''
    serializer_class = CheckoutSerializer
    renderer_classes = (JSONRenderer,)
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_redirect_value(self,serializer,value):
        if serializer.validated_data.get(value) is not None:
            return '{}={}'.format(value,serializer.validated_data[value])
        return ''

    def create(self, request):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            #create basket
            if serializer.validated_data.get('vouchers'):
                createBasket(serializer.validated_data['products'],request.user,serializer.validated_data['system'],vouchers=serializer.validated_data['vouchers'])
            else:
                createBasket(serializer.validated_data['products'],request.user,serializer.validated_data['system'])
            redirect = HttpResponseRedirect('/ledger/checkout/checkout?{}&{}&{}&{}&{}&{}&{}&{}&{}&{}&{}&{}'.format(
                                                                                                self.get_redirect_value(serializer,'card_method'),
                                                                                                self.get_redirect_value(serializer,'basket_owner'),
                                                                                                self.get_redirect_value(serializer,'template'),
                                                                                                self.get_redirect_value(serializer,'fallback_url'),
                                                                                                self.get_redirect_value(serializer,'return_url'),
                                                                                                self.get_redirect_value(serializer,'associateInvoiceWithToken'),
                                                                                                self.get_redirect_value(serializer,'forceRedirect'),
                                                                                                self.get_redirect_value(serializer,'sendEmail'),
                                                                                                self.get_redirect_value(serializer,'proxy'),
                                                                                                self.get_redirect_value(serializer,'checkoutWithToken'),
                                                                                                self.get_redirect_value(serializer,'bpay_format'),
                                                                                                self.get_redirect_value(serializer,'icrn_format')))

            return redirect
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))

#######################################################
#                                                     #
#                    /CHECKOUT                        #
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

    def validate_system(self,value):
        try:
            if not validSystem(value):
                raise serializers.ValidationError('This is not a valid system.')
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate(self,data):
        if data['items'] and not (data['banked_start'] and data['banked_end']):
            raise serializers.ValidationError('banked_start and banked_end are required for items csv. ')
        return data

class ReportCreateView(views.APIView):
    authentication_classes = [SessionAuthentication]
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
                                            serializer.validated_data['banked_end'])
            else:
                report = generate_trans_csv(systemid_check(serializer.validated_data['system'])
                                            ,serializer.validated_data['start'],
                                            serializer.validated_data['end'],
                                            district = serializer.validated_data['district'])
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))

class UserReportView(views.APIView):

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            report = None

            filename = 'emailuser-report'
            # Generate Report
            report = user_report()
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
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