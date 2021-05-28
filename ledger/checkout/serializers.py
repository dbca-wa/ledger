from ledger.accounts.models import EmailUser
from ledger.catalogue.models import Product
from ledger.payments.helpers import is_valid_system
from oscar.apps.voucher.models import Voucher
from oscar.apps.shipping.methods import NoShippingRequired
from rest_framework import serializers
from django.template.loader import get_template
from django.template import TemplateDoesNotExist


class CheckoutProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1,default=1)

    def validate_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist as e:
            raise serializers.ValidationError('{} (id={})'.format(str(e),value))
        return value


class CheckoutCustomProductSerializer(serializers.Serializer):
    ledger_description = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1,default=1)
    price_excl_tax = serializers.DecimalField(max_digits=22, decimal_places=12, default=0)
    price_incl_tax = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)


class VoucherSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=128)

    def validate_code(self, value):
        try:
            Voucher.objects.get(code=value)
        except Voucher.DoesNotExist as e:
            raise serializers.ValidationError('{} (code={})'.format(str(e),value))
        return value


class BasketSerializer(serializers.Serializer):
    products = serializers.ListField()
    vouchers = VoucherSerializer(many=True,required=False)
    system = serializers.CharField(max_length=4, min_length=4)
    custom_basket = serializers.BooleanField(default=False)
    booking_reference = serializers.CharField(required=False)

    def validate_system(self, value):
        if not value:
            raise serializers.ValidationError('No system ID provided')
        elif not len(value) == 4:
            raise serializers.ValidationError('The system ID should be 4 characters long')
        if not is_valid_system(value):
            raise serializers.ValidationError('The system ID is not valid')
        
        return value


class CheckoutSerializer(serializers.Serializer):
    system = serializers.CharField(max_length=4, min_length=4)
    card_method = serializers.ChoiceField(choices=['preauth', 'payment'], default='payment')
    shipping_method = serializers.CharField(default=NoShippingRequired().code)
    basket_owner = serializers.IntegerField(required=False, default=None)
    template = serializers.CharField(required=False, default=None)
    fallback_url = serializers.URLField()
    return_preload_url = serializers.URLField(required=False, default=None)
    return_url = serializers.URLField()
    associate_invoice_with_token = serializers.BooleanField(default=False)
    force_redirect = serializers.BooleanField(default=False)
    send_email = serializers.BooleanField(default=False)
    proxy = serializers.BooleanField(default=False)
    checkout_token = serializers.BooleanField(default=False)
    bpay_format = serializers.ChoiceField(choices=['crn', 'icrn'], default='crn')
    icrn_format = serializers.ChoiceField(choices=['ICRNAMT', 'ICRNDATE', 'ICRNAMTDATE'], default='ICRNAMT')
    icrn_date = serializers.DateField(required=False, default=None)
    invoice_text = serializers.CharField(required=False, default=None)
    check_url = serializers.URLField(required=False, default=None)
    amount_override=serializers.FloatField(required=False, default=None)
    session_type = serializers.ChoiceField(choices=['standard', 'ledger_api'], default='standard')


    def validate(self, data):
        if data['proxy'] and not data['basket_owner']:
            raise serializers.ValidationError('A proxy payment requires the basket_owner to be set.')
        return data

    def validate_system(self, value):
        if not value:
            raise serializers.ValidationError('No system ID provided')
        elif not len(value) == 4:
            raise serializers.ValidationError('The system ID should be 4 characters long')
        if not is_valid_system(value):
            raise serializers.ValidationError('The system ID is not valid')

        return value

    def validate_template(self, value):
        if value is not None:
            try:
                get_template(value)
            except TemplateDoesNotExist as e:
                raise serializers.ValidationError(str(e))
        return value

    def validate_basket_owner(self, value):
        if value is not None:
            try:
                EmailUser.objects.get(id=value)
            except EmailUser.DoesNotExist as e:
                raise serializers.ValidationError(str(e))
        return value
