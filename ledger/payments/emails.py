from ledger.emails.emails import EmailBase

ledger_email = 'no-reply@dbca.wa.gov.au'

class TemplateEmailBase(EmailBase):
    subject = ''
    html_template = 'dpaw_payments/emails/base.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'dpaw_payments/emails/base.txt'

def send_refund_email(invoice,refund_type,amount,card_ending=None):
    if refund_type == 'card;' and not card_ending:
        raise ValidationError('The last four card numbers are required for a crad refund')

    email_obj = TemplateEmailBase()
    email_obj.subject = 'Refund for invoice {}'.format(invoice.reference)
    email_obj.html_template = 'dpaw_payments/emails/refund.html'
    email_obj.txt_template = 'dpaw_payments/emails/refund.txt'

    email = invoice.owner.email

    if email:
        context = {
            'reference': invoice.reference,
            'amount': amount,
            'refund_type': refund_type,
            'card_ending': card_ending
        }
       
        email_obj.send([email], from_address=ledger_email, context=context) 
