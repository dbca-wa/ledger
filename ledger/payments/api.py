from rest_framework import viewsets, serializers, status, generics
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from bpay.models import BpayTransaction, BpayFile, BpayCollection
from invoice.models import Invoice
from bpoint.models import BpointTransaction
from cash.models import CashTransaction
from facade import bpoint_facade
from oscar.apps.order.models import Order
from oscar.apps.payment import forms
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
    date_modifier = serializers.SerializerMethodField()
    transactions = BpayTransactionSerializer(many=True)
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    settled = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = BpayFile
        fields = (
            "id",
            "inserted",
            "created",
            "file_id",
            "settled",
            "date_modifier",
            "credit_items",
            "credit_amount",
            "cheque_items",
            "cheque_amount",
            "debit_amount",
            "debit_items",
            "account_total",
            "account_records",
            "group_total",
            "group_accounts",
            "group_records",
            "file_total",
            "file_groups",
            "file_records",
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
    invoice_reference = serializers.CharField(max_length=50)
    total = serializers.DecimalField(max_digits=12, decimal_places=2,required=False)
    card = CardSerializer(required=False)
    original_txn = serializers.CharField(max_length=50,required=False)
    action = serializers.ChoiceField(choices=BpointTransaction.ACTION_TYPES)
    subtype = serializers.ChoiceField(choices=BpointTransaction.SUB_TYPES,default='single')
    type = serializers.ChoiceField(choices=BpointTransaction.TRANSACTION_TYPES)
    
    def validate(self, data):
        if data['action'] in ['payment','preauth','unmatched_refund'] and not ( data.get('card') and data.get('total')):
            raise serializers.ValidationError("For the selected action you need to provide details for the following 'card' and 'total' details.")
        
        if data['action'] in ['refund','capture','reversal'] and not data.get('original_txn'):
            raise serializers.ValidationError("For the selected action you need to provide the transaction number of the transaction matched to this one.")
        return data
    
class BpointPaymentCreateView(generics.CreateAPIView):
    ''' Used to create a card point using the api:
        Example of json request:
        {
            "invoice_reference": "1000025",
            "total": 1,
            "action": "payment",
            "type": "internet",
            "card": {
                "number": "4444333322221111",
                "cvn": "123",
                "expiry": "052017"
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
            if serializer.validated_data.get('total'): total = serializer.validated_data['total']
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
                inv = Invoice.objects.get(reference=serializer.validated_data['invoice_reference'])
                reference = inv.reference
            except Invoice.DoesNotExist:
                raise serializers.ValidationError("The invoice doesn't exist.")
            # intialize the bpoint facade object
            facade = bpoint_facade
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
                serializer.validated_data['invoice_reference'][:-1],
                reference,
                total,
                bankcard_form.bankcard,
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
    invoice = serializers.CharField(source='invoice.reference')
    class Meta:
        model = CashTransaction
        fields = (
            'invoice',
            'amount',
            'created',
            'type',
            'original_txn'
        )
        
class CashViewSet(viewsets.ModelViewSet):
    '''Used to create a cash payment using the api:
        Example of json request:
        {
            "invoice": "1000025",
            "amount": 1,
            "type": "payment"
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
            #print serializer.validated_data['invoice']
            # Check if the invoice exists if action is payment,preauth
            try:
                serializer.validated_data['invoice'] = Invoice.objects.get(reference=serializer.validated_data['invoice']['reference'])
            except Invoice.DoesNotExist:
                raise serializers.ValidationError("The invoice doesn't exist.")
            
            txn = serializer.save()
            http_status = status.HTTP_201_CREATED
            serializer = CashSerializer(txn)
            return Response(serializer.data,status=http_status)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(str(e))


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
    class Meta:
        model = Invoice
        fields = (
            'id',
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
        read_only_feilds=(
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