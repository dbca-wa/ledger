from django.contrib import admin

# Register your models here.
from . import models

@admin.register(models.CashTransaction)
class CashAdmin(admin.ModelAdmin):
    list_display = (
        'invoice',
        'amount',
        'type',
        'source',
        'region',
        'district',
        'created'
    )
    search_fields = [
        'invoice__reference',
        'type',
        'source',
        'region',
        'district',
    ]

@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('reference','order','payment_status','settlement_date','amount', 'system','created' )
    search_fields = ('reference',)
    list_filter = ('system'),    
   
@admin.register(models.InvoiceBPAY)
class InvoiceBpayAdmin(admin.ModelAdmin):
    pass

@admin.register(models.BpayTransaction)
class BpayTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'crn',
        'type',
        'txn_ref',
        'amount',
        'file',
        'p_date'
    )

@admin.register(models.BpayJobRecipient)
class BpayJobRecipient(admin.ModelAdmin):
    pass

@admin.register(models.BpayFile)
class BpayFileAdmin(admin.ModelAdmin):
    list_display = (
        #'creation_date',
        #'creation_time',
        'created',
    )

class BillerCodeRecipientInline(admin.StackedInline):
    model = models.BillerCodeRecipient
    extra = 1

@admin.register(models.BillerCodeSystem)
class BillerCodeSystemAdmin(admin.ModelAdmin):
    list_display= (
        'system',
        'biller_code'
    )
    inlines = [BillerCodeRecipientInline]

@admin.register(models.BpointTransaction)
class BpointTransactionAdmin(admin.ModelAdmin):
    readonly_fields = (
                        'action',
                        'amount',
                        'amount_original',
                        'amount_surcharge',
                        'cardtype',
                        'crn1',
                        'txn_number',
                        'original_txn',
                        'receipt_number',
                        'type',
                        'response_code',
                        'response_txt',
                        'processed',
                        'settlement_date',
                        'dvtoken',
                        'last_digits',
                        'is_test'
                    )
    list_display = ('created','settlement_date','txn_number','receipt_number','crn1','action','amount','approved','is_test')
    search_fields = ('created','amount','crn1')
    
    def has_delete_permission(self,*args,**kwargs):
        return False
    
    def approved(self,obj):
        if obj.approved:
            return True
        return False
    approved.boolean = True
    
    def has_add_permission(self,request,obj=None):
        return False

class OracleInvoiceParser(admin.TabularInline):
    model = models.OracleParserInvoice
    extra = 0

@admin.register(models.OracleParser)
class OracleParserAdmin(admin.ModelAdmin):
    inlines = [OracleInvoiceParser,]

@admin.register(models.OracleInterface)
class OracleInterfaceAdmin(admin.ModelAdmin):
    list_display = ['activity_name','amount','status','receipt_number','receipt_date','source','method']
    search_fields = ('source','receipt_number')
class OracleInterfaceRecipientInline(admin.TabularInline):
    model = models.OracleInterfaceRecipient
    extra = 1

class OracleInterfaceDeductionInline(admin.TabularInline):
    model = models.OracleInterfaceDeduction
    extra = 1

@admin.register(models.OracleInterfaceSystem)
class OracleInterfaceSystemAdmin(admin.ModelAdmin):
    list_display = ('system_name','system_id')
    inlines = [OracleInterfaceRecipientInline, OracleInterfaceDeductionInline] 

@admin.register(models.OracleAccountCode)
class OracleAccountCode(admin.ModelAdmin):
    list_display = ('active_receivables_activities',)
