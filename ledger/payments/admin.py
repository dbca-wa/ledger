from django.contrib import admin
from django.utils.html import format_html

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
    raw_id_fields = ('invoice',)

@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('reference','oracle_invoice_number','order','payment_status','settlement_date','amount', 'system','created' )
    search_fields = ('reference',)
    list_filter = ('system'),    
    raw_id_fields = ('previous_invoice','oracle_invoice_file')
    list_per_page = 30

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
    readonly_fields = ('file',)
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
    list_display = ('created','settlement_date','txn_number','receipt_number','crn1','action','amount','approved','is_test','integrity_check')
    search_fields = ('created','amount','crn1','txn_number','receipt_number')
    
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

class OracleInterfaceReportReceipientInline(admin.TabularInline):
    model = models.OracleInterfaceReportReceipient
    extra = 1
class OracleInterfaceRecipientInline(admin.TabularInline):
    model = models.OracleInterfaceRecipient
    extra = 1

class OracleInterfaceDeductionInline(admin.TabularInline):
    model = models.OracleInterfaceDeduction
    extra = 1

class OracleInterfacePermissionInline(admin.TabularInline):
    model = models.OracleInterfacePermission
    extra = 1

@admin.register(models.OracleInterfaceSystem)
class OracleInterfaceSystemAdmin(admin.ModelAdmin):
    list_display = ('system_name','system_id')
    inlines = [OracleInterfacePermissionInline, OracleInterfaceRecipientInline, OracleInterfaceReportReceipientInline, OracleInterfaceDeductionInline, ] 

@admin.register(models.OracleAccountCode)
class OracleAccountCode(admin.ModelAdmin):
    list_display = ('active_receivables_activities',)


@admin.register(models.LinkedInvoice)
class LinkedInvoiceAdmin(admin.ModelAdmin):
    search_fields = ('invoice_reference','booking_reference','booking_reference_linked',)
    list_display = ('invoice_reference','system_identifier','booking_reference','booking_reference_linked','invoice_group_id_id','created')
    list_filter = ('system_identifier','created',)
    raw_id_fields = ('system_identifier','invoice_group_id',)


@admin.register(models.RefundFailed)
class RefundFailedAdmin(admin.ModelAdmin):
    list_display = ('invoice_group','booking_reference','invoice_reference','refund_amount','status','system_identifier','created','completed_date','completed_by')

@admin.register(models.PaymentTotal)
class PaymentTotal(admin.ModelAdmin):
     list_display = ('oracle_system','settlement_date','bpoint_gateway_total','ledger_bpoint_total','oracle_parser_total','oracle_receipt_total','cash_total','bpay_total','difference','discrepancy','updated')
     list_filter = ('oracle_system','settlement_date',)
     raw_id_fields = ('oracle_system',)
     ordering = ('-settlement_date',)

     def discrepancy(self, obj):
            if obj.bpoint_gateway_total != obj.oracle_receipt_total:
                 return format_html(
                    
                     '<b style="font-weight:bold; color: red">&#x2718;</b>',
                    )
            else:
                 return format_html(

                     '<b style="font-weight:bold; color: #65af22">&#x2713;</b>',
                    )
     def difference(self, obj):
         return obj.bpoint_gateway_total - obj.oracle_receipt_total


     discrepancy.allow_tags = True
     difference.allow_tags = True

@admin.register(models.PaymentInformationLink)
class PaymentInformationLinkAdmin(admin.ModelAdmin):
    list_display = ('title','active','created')