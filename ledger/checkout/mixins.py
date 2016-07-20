from oscar.core.loading import get_class
from ledger.payments.models import Invoice
from django.http import HttpResponseRedirect
CoreOrderPlacementMixin = get_class('checkout.mixins','OrderPlacementMixin')

class OrderPlacementMixin(CoreOrderPlacementMixin):
    
    def handle_successful_order(self, order):
        """
        Handle the various steps required after an order has been successfully
        placed.
        Override this view if you want to perform custom actions when an
        order is submitted.
        """
        # Get the return url
        success_url = self.checkout_session.return_url()

        # Send confirmation message (normally an email)
        self.send_confirmation_message(order, self.communication_type_code)
        
        # Flush all session data
        self.checkout_session.flush()

        # Save order and invoice id in session so thank-you page can load it
        self.request.session['checkout_order_id'] = order.id
        self.request.session['checkout_invoice_id'] = Invoice.objects.get(order_number=order.number).id
        # Check if return url is in session
        if not success_url:
            response = HttpResponseRedirect(self.get_success_url())
        else:
            response = HttpResponseRedirect(success_url)
        self.send_signal(self.request, response, order)
        return response