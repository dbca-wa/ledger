import requests

from oscar.core.loading import get_class
from ledger.payments.models import Invoice
from django.http import HttpResponseRedirect
from ledger.accounts.models import EmailUser
CoreOrderPlacementMixin = get_class('checkout.mixins','OrderPlacementMixin')

class OrderPlacementMixin(CoreOrderPlacementMixin):
    
    def handle_order_placement(self, order_number, user, basket,
                               shipping_address, shipping_method,
                               shipping_charge, billing_address, order_total,
                               **kwargs):
        """
        Write out the order models and return the appropriate HTTP response
        We deliberately pass the basket in here as the one tied to the request
        isn't necessarily the correct one to use in placing the order.  This
        can happen when a basket gets frozen.
        """
        # Swap out the user if one is present in session
        swap_user = None
        try:
            swap_user = EmailUser.objects.get(id=int(self.checkout_session.basket_owner()))

        except:
            pass
        if swap_user:
            # swap the user to be used for the basket and the order
            user = swap_user
            basket.owner = user
            basket.save()

        order = self.place_order(
            order_number=order_number, user=user, basket=basket,
            shipping_address=shipping_address, shipping_method=shipping_method,
            shipping_charge=shipping_charge, order_total=order_total,
            billing_address=billing_address, **kwargs)
        basket.submit()
        return self.handle_successful_order(order)

    def handle_successful_order(self, order):
        """
        Handle the various steps required after an order has been successfully
        placed.
        Override this view if you want to perform custom actions when an
        order is submitted.
        """
        from ledger.payments.utils import update_payments
        # Get the return url
        return_url = self.checkout_session.return_url()
        return_preload_url = self.checkout_session.return_preload_url()
        force_redirect = self.checkout_session.force_redirect()

        # Update the payments in the order lines
        invoice = Invoice.objects.get(order_number=order.number)
        update_payments(invoice.reference)

        if self.checkout_session.send_email():
            # Send confirmation message (normally an email)
            self.send_confirmation_message(order, self.communication_type_code)
        
        # Flush all session data
        self.checkout_session.flush()

        # Save order and invoice id in session so thank-you page can load it
        self.request.session['checkout_order_id'] = order.id
        self.request.session['checkout_invoice'] = invoice.reference
        self.request.session['checkout_return_url'] = return_url
        self.request.session.save()

        # If preload is enabled, fire off an unmonitored request server-side
        # FIXME: replace with basket one-time secret
        if return_preload_url:
            try:
                requests.get('{}?invoice={}'.format(return_preload_url, invoice.reference),
                                cookies=self.request.COOKIES,
                                verify=False)
                # bodge for race condition: if preload updates the session, we need to update it
                self.request.session._session_cache = self.request.session.load()
            except requests.exceptions.ConnectionError:
                pass

        if not force_redirect:
            response = HttpResponseRedirect(self.get_success_url())
        else:
            response = HttpResponseRedirect('{}?invoice={}'.format(return_url, invoice.reference))

        self.send_signal(self.request, response, order)

        return response
