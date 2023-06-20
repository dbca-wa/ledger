import json
from datetime import date
from six.moves.urllib import parse as urlparse
from django.views import generic
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import Template, Context, TemplateDoesNotExist
from django.http import HttpResponse
from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger.payments.utils import checkURL
from ledger.payments.cash.models import REGION_CHOICES
from ledger.payments.utils import systemid_check, update_payments, ledger_payment_invoice_calulations 
#
#from oscar.apps.order.models import Order
from ledger.order.models import Order
from ledger.payments.models import Invoice
from ledger.payments.mixins import InvoiceOwnerMixin
from ledger.basket import models as basket_models
from ledger.payments import models as payments_models
from ledger.payments import helpers
from ledger.payments.models import LinkedInvoiceGroupIncrementer, LinkedInvoice
from django.db.models import Q
from decimal import Decimal as D
from django.db.models import Count
from ledger.payments.invoice import utils as invoice_utils
#
from confy import env
#

class InvoicePDFView(InvoiceOwnerMixin,generic.View):
    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        response = HttpResponse(content_type='application/pdf')
        response.write(create_invoice_pdf_bytes('invoice.pdf',invoice))
        return response

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice

class InvoiceDetailView(InvoiceOwnerMixin,generic.DetailView):
    model = Invoice
    template_name = 'dpaw_payments/invoice/invoice.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        ctx = super(InvoiceDetailView,self).get_context_data(**kwargs)
        ctx['bpay_allowed'] = settings.BPAY_ALLOWED
        return ctx

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice

class PaymentErrorView(generic.TemplateView):
    template_name = 'dpaw_payments/payment_error.html'

class InvoiceSearchView(generic.TemplateView):

    template_name = 'dpaw_payments/invoice/invoice_search.html'

class OraclePayments(generic.TemplateView):
    template_name = 'dpaw_payments/oracle_payments.html'

    def get_context_data(self, **kwargs):
        ctx = super(OraclePayments,self).get_context_data(**kwargs)
        if helpers.is_payment_admin(self.request.user) is True:
            invoice_group_id = self.request.GET.get('invoice_group_id','');
            invoice_no = self.request.GET.get('invoice_no','')
            booking_reference = self.request.GET.get('booking_reference','')
            receipt_no = self.request.GET.get('receipt_no','')
            txn_number = self.request.GET.get('txn_number','')
            ctx['payment_oracle_admin'] = helpers.is_payment_oracle_admin(self.request.user)
            #&cur    rent_invoice_no="+ledger_payments.var.current_invoice_no+"&current_booking_reference="+ledger_payments.var.current_booking_reference,
              
            ctx['invoice_group_id'] = invoice_group_id
            ctx['invoice_no'] = invoice_no
            ctx['booking_reference'] = booking_reference
            ctx['receipt_no'] = receipt_no
            ctx['txn_number'] = txn_number

            ctx['oracle_code_refund_allocation_pool'] = settings.UNALLOCATED_ORACLE_CODE
            #self.get_booking_history(invoice_group_id)
        else:
            self.template_name = 'dpaw_payments/forbidden.html'
        return ctx

class LinkedInvoiceIssue(generic.TemplateView):
    template_name = 'dpaw_payments/linked_invoice_payments_issues.html'

    def get(self, request, **kwargs):
        
        ctx = super(LinkedInvoiceIssue,self).get_context_data(**kwargs)
        if helpers.is_payment_admin(request.user) is True:
            invoice_group_id = self.kwargs['linked_invoice_group_id']
            fix_lgid = request.GET.get('fix_lgid','');            
            
            linked_payments_booking_references = []
            linked_group_issue = False
            if invoice_group_id:
                if int(invoice_group_id) > 0:
                    linkinv = LinkedInvoice.objects.filter(invoice_group_id=invoice_group_id)
                    if linkinv.count() > 0:
                        # invoice_group = LinkedInvoice.objects.filter(invoice_group_id=invoice_group_id).order_by('-created')[0]

                        # invoice_group_checks = LinkedInvoice.objects.filter(Q(booking_reference__in=linked_payments_booking_references) | Q(booking_reference_linked__in=linked_payments_booking_references)).values('invoice_group_id_id').annotate(total=Count('invoice_group_id_id')).order_by('total')

                        for li in linkinv:                                                
                            if li.booking_reference not in linked_payments_booking_references:
                                linked_payments_booking_references.append(li.booking_reference)
                            if li.booking_reference_linked not in linked_payments_booking_references:
                                linked_payments_booking_references.append(li.booking_reference_linked)

                        invoice_group_checks_group_by = LinkedInvoice.objects.filter(Q(booking_reference__in=linked_payments_booking_references) | Q(booking_reference_linked__in=linked_payments_booking_references)).values('invoice_group_id_id').annotate(total=Count('invoice_group_id_id')).order_by('-total')
                        
                        invoice_group_id_highest = invoice_group_checks_group_by[0]['invoice_group_id_id']
                        invoice_group_checks = LinkedInvoice.objects.filter(Q(booking_reference__in=linked_payments_booking_references) | Q(booking_reference_linked__in=linked_payments_booking_references))
                        if invoice_group_checks_group_by.count() > 1:
                            linked_group_issue = True
                        
                        if fix_lgid == 'true':
                            invoice_group_id_highest_obj = LinkedInvoiceGroupIncrementer.objects.filter(id=invoice_group_id_highest)
                            if invoice_group_id_highest_obj.count() > 0:
                                for lgc in invoice_group_checks:
                                    lgc.invoice_group_id = invoice_group_id_highest_obj[0]
                                    lgc.save()
                            response = HttpResponse("<script>window.location='/ledger/payments/oracle/payments/linked-invoice-issues/"+str(invoice_group_id)+"/';</script>", content_type='text/html')
                            return response

            ctx['invoice_group_id_highest'] = invoice_group_id_highest            
            ctx['invoice_group_id'] = invoice_group_id
            ctx['oracle_code_refund_allocation_pool'] = settings.UNALLOCATED_ORACLE_CODE
            ctx['invoice_group_checks'] = invoice_group_checks
            ctx['linked_group_issue'] = linked_group_issue

            #self.get_booking_history(invoice_group_id)
        else:
            self.template_name = 'dpaw_payments/forbidden.html'
        return render(request, self.template_name, ctx)


class LinkedPaymentIssue(generic.TemplateView):
    template_name = 'dpaw_payments/linked_payments_issues.html'

    def get(self, request, **kwargs):
        
        ctx = super(LinkedPaymentIssue,self).get_context_data(**kwargs)
        if helpers.is_payment_admin(request.user) is True:
            invoice_group_id = self.kwargs['linked_invoice_group_id']
            generate_receipts_for = []
            fix_discrephency = request.GET.get('fix_discrephency','')            
            
            linked_payments_booking_references = []
            linked_group_issue = False
            if invoice_group_id:
                lpic = ledger_payment_invoice_calulations(invoice_group_id, None, None, None, None)
                total_difference_of_gw_and_oracle = D(lpic['data']['total_gateway_amount']) - D(lpic['data']['total_oracle_amount'])

                #if D(lpic['data']['total_gateway_amount']) >= total_difference_of_gw_and_oracle:
                if  D(lpic['data']['total_gateway_amount']) != D(lpic['data']['total_oracle_amount']):
                    bp_hash = {}
                    inv_hash = {}
                    for bp_data in lpic['data']['bpoint']:
                        hashstr = str(str(bp_data['settlement_date']) + str(bp_data['amount'])).replace("/","").replace(".","")
                        if hashstr in bp_hash:
                            if bp_data['action'] == 'payment':
                                bp_hash[hashstr]['total'] = bp_hash[hashstr]['total'] + 1
                                bp_hash[hashstr]['total_amount'] = str(D(bp_hash[hashstr]['total_amount']) + D(bp_data['amount']))
                            elif bp_data['action'] == 'refund':
                                bp_hash[hashstr]['total'] = bp_hash[hashstr]['total'] + 1
                                bp_hash[hashstr]['total_amount'] = str(D(bp_hash[hashstr]['total_amount']) - D(bp_data['amount']))                                
                        else:
                            if bp_data['action'] == 'payment':
                                bp_hash[hashstr] = {'total':  1, 'total_amount': bp_data['amount'],'amount': bp_data['amount'], 'settlement_date': bp_data['settlement_date']}
                            elif bp_data['action'] == 'refund':
                                total_refund = D(bp_data['amount']) - D(bp_data['amount'])
                                bp_hash[hashstr] = {'total':  1, 'total_amount': total_refund,'amount': total_refund, 'settlement_date': bp_data['settlement_date']}

                    for inv_data in lpic['data']['invoices_data']:
                        hashstr = str(str(inv_data['settlement_date']) + str(inv_data['amount'])).replace("/","").replace(".","")
                        if hashstr in inv_data:
                            inv_hash[hashstr]['total'] = inv_hash[hashstr]['total'] + 2
                            inv_hash[hashstr]['total_amount'] = str(D(inv_hash[hashstr]['total_amount']) + D(inv_data['amount']))
                        else:
                            inv_hash[hashstr] = {'total':  1, 'total_amount' : inv_data['amount'], 'amount': inv_data['amount'], 'settlement_date': inv_data['settlement_date']}

                    for bp_keys in bp_hash:
                        if bp_keys in inv_hash:
                            if bp_keys in inv_hash: 
                                total_trans = bp_hash[bp_keys]['total'] - inv_hash[bp_keys]['total']
                                total_amount = str(total_trans * D(bp_hash[bp_keys]['amount']))                                
                                generate_receipts_for.append({"total_amount": total_amount, "settlement_date": bp_hash[bp_keys]['settlement_date']})                                                                                            



                if fix_discrephency == 'true':
                    lines = []
                    for gr in generate_receipts_for:                    
                        lines.append({'ledger_description':str("Payment disrephency for settlement date {}".format(gr['settlement_date'])),"quantity":1,"price_incl_tax":D('{:.2f}'.format(float(gr['total_amount']))),"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 1})                        
                    order = invoice_utils.allocate_refund_to_invoice(request, lpic['data']['booking_reference'], lines, invoice_text=None, internal=False, order_total='0.00',user=None, booking_reference_linked=lpic['data']['booking_reference_linked'],system_id=lpic['data']['system_id'])
                    new_invoice = Invoice.objects.get(order_number=order.number)
                    new_invoice.settlement_date = gr['settlement_date']
                    update_payments(new_invoice.reference)
                    
                    response = HttpResponse("<script>window.location='/ledger/payments/oracle/payments/linked-payment-issues/"+str(invoice_group_id)+"/';</script>", content_type='text/html')
                    return response


            print ("GENERATE RECEIPTS FOR")
            print (generate_receipts_for)
            print (len(generate_receipts_for))
            ctx['generate_receipts_for'] = generate_receipts_for
            ctx['invoice_group_id'] = invoice_group_id
            ctx['generate_receipts_for_length'] = len(generate_receipts_for)
        else:
            self.template_name = 'dpaw_payments/forbidden.html'
        return render(request, self.template_name, ctx)
    
class InvoicePaymentView(InvoiceOwnerMixin,generic.TemplateView):
    template_name = 'dpaw_payments/invoice/payment.html'
    num_years = 10
    #context_object_name = 'invoice'

    def check_owner(self, user):
        return self.is_payment_admin(user)

    def month_choices(self):
        return ["%.2d" %x for x in range(1,13)]

    def year_choices(self):
        return [x for x in range(
            date.today().year,
            date.today().year + self.num_years
        )]

    def get_context_data(self, **kwargs):
        ctx = super(InvoicePaymentView, self).get_context_data(**kwargs)
        invoices = []
        UPDATE_PAYMENT_ALLOCATION = env('UPDATE_PAYMENT_ALLOCATION', False)
        ctx['payment_allocation'] = UPDATE_PAYMENT_ALLOCATION
        ctx['bpay_allowed'] = settings.BPAY_ALLOWED
        ctx['months'] = self.month_choices
        ctx['years'] = self.year_choices
        ctx['regions'] = list(REGION_CHOICES)

        #invoices = []

        #invoices_obj = Invoice.objects.filter(reference__in=self.request.GET.getlist('invoice')).values('created','text','amount','order_number','reference','system','token','voided','previous_invoice','settlement_date','payment_method').order_by('created')
        #order_numbers = []
        #for i in invoices_obj:
        #    row = {'created': None, 'text': None, 'amount': None, 'order_number': None,'reference': None, 'system': None, 'token' : None, 'voided': None, 'previous_invoice': None,'settlement_date': None, 'payment_method': None, 'order': {}}
        #    row['created'] = i['created']
        #    row['text'] = i['text']
        #    row['amount'] = i['amount']
        #    row['order_number'] = i['order_number']
        #    row['reference'] = i['reference']
        #    row['system'] = i['system']
        #    row['token'] = i['token']
        #    row['voided'] = i['voided']
        #    row['previous_invoice'] =  i['previous_invoice']
        #    row['settlement_date'] = i['settlement_date']
        #    row['payment_method'] = i['payment_method']
        #    #row[''] =
        #    #row[''] =
        #    #row[''] =
        #    #row[''] =
        #    #row[''] =

        #    print (i['order_number'])
        #    #order_numbers.append(i.order_number)
        #    order_obj = Order.objects.filter(number=i['order_number'])

        #    row['order'] = order_obj[0]
        #    invoices.append(row)

        invoices = Invoice.objects.filter(reference__in=self.request.GET.getlist('invoice')).order_by('created')
        ctx['invoices'] = invoices
        if self.request.GET.get('amountProvided') == 'true':
            ctx['amountProvided'] = True
        if self.request.GET.get('redirect_url'):
            try:
                checkURL(self.request.GET.get('redirect_url'))
                ctx['redirect_url'] = self.request.GET.get('redirect_url')
            except:
                pass
        if self.request.GET.get('callback_url'):
            try:
                checkURL(self.request.GET.get('callback_url'))
                domain = urlparse(self.request.GET.get('callback_url')).netloc.split('.')[1]
                if 'dbca.wa.gov.au' == domain or settings.DEBUG:
                    ctx['callback_url'] = self.request.GET.get('callback_url')
            except:
                pass
        if self.request.GET.get('custom_template'):
            try:
                ctx['custom_block'] = get_template(self.request.GET.get('custom_template'))
            except TemplateDoesNotExist as e:
                pass
        return ctx

class RefundPaymentView(generic.TemplateView):
    template_name = 'checkout/refund_payment_api_wrapper.html'

    def get(self, request, *args, **kwargs):
         basket = None
         basket_hash = request.COOKIES.get('ledgergw_basket','')
         basket_hash_split = basket_hash.split("|")
         basket = basket_models.Basket.objects.get(id=basket_hash_split[0])
         return render(request, self.template_name, {'basket': basket})

class ZeroPaymentView(generic.TemplateView):
    template_name = 'checkout/zero_payment_api_wrapper.html'

    def get(self, request, *args, **kwargs):
         basket = None
         basket_hash = request.COOKIES.get('ledgergw_basket','')
         basket_hash_split = basket_hash.split("|")
         basket = basket_models.Basket.objects.get(id=basket_hash_split[0])
         return render(request, self.template_name, {'basket': basket})

class NoPaymentView(generic.TemplateView):
    template_name = 'checkout/no_payment_api_wrapper.html'

    def get(self, request, *args, **kwargs):
         basket = None
         basket_hash = request.COOKIES.get('ledgergw_basket','')
         basket_hash_split = basket_hash.split("|")
         basket = basket_models.Basket.objects.get(id=basket_hash_split[0])
         return render(request, self.template_name, {'basket': basket})

class FailedTransaction(generic.TemplateView):
    template_name = 'dpaw_payments/failed_transaction.html'

    def get_context_data(self, **kwargs):
        ctx = super(FailedTransaction,self).get_context_data(**kwargs)
        if helpers.is_payment_admin(self.request.user) is True:
            system_id = self.request.GET.get('system_id','')
            ctx['oracle_systems'] = payments_models.OracleInterfaceSystem.objects.all()
            ctx['system_id'] = system_id
        else:
            self.template_name = 'dpaw_payments/forbidden.html'
        return ctx


