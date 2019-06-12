from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from ledger.payments.invoice.models import Invoice
from commercialoperator.components.proposals.serializers import ProposalSerializer, InternalProposalSerializer, ProposalParkSerializer
from commercialoperator.components.main.serializers import ApplicationTypeSerializer
from commercialoperator.components.bookings.models import (
    Booking,
    ParkBooking,
    BookingInvoice,
)
from commercialoperator.components.proposals.serializers import ProposalSerializer
from rest_framework import serializers


class BookingInvoiceSerializer(serializers.ModelSerializer):
    #proposal = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = BookingInvoice
        fields = 'invoice_reference'

class BookingSerializer(serializers.ModelSerializer):
    #park_bookings = ParkBookingSerializer(many=True, read_only=True)
    invoice = BookingInvoiceSerializer(read_only=True)
    #invoice = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'
#        datatables_always_serialize = (
#            'id',
#        )

    def get_invoice(self,obj):
        return obj.proposal.fee_invoice_reference

class ParkBookingSerializer(serializers.ModelSerializer):
    #proposal = serializers.SerializerMethodField(read_only=True)
    park = serializers.SerializerMethodField(read_only=True)
    approval_number = serializers.SerializerMethodField(read_only=True)
    booking = BookingSerializer(read_only=True)
    applicant = serializers.SerializerMethodField(read_only=True)
    org_applicant = serializers.SerializerMethodField(read_only=True)
    proxy_applicant = serializers.SerializerMethodField(read_only=True)
    payment_status = serializers.SerializerMethodField(read_only=True)
    invoice_reference = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ParkBooking
        fields = (
            'id',
            'park',
            'arrival',
            'no_adults',
            'no_children',
            'no_free_of_charge',
            'cost',
            'booking',
            'approval_number',
            'applicant',
            'org_applicant',
            'proxy_applicant',
            'payment_status',
            'invoice_reference',
        )
        datatables_always_serialize = (
            'id',
            'park',
            'arrival',
            'no_adults',
            'no_children',
            'no_free_of_charge',
            'cost',
            'booking',
            'approval_number',
            'applicant',
            'org_applicant',
            'proxy_applicant',
            'payment_status',
            'invoice_reference',

        )

    def get_park(self,obj):
        return obj.park.name

    def get_approval_number(self,obj):
        try:
            return obj.booking.proposal.approval.lodgement_number
        except:
            return ''

    def get_applicant(self,obj):
        try:
            return obj.booking.proposal.approval.applicant
        except:
            return ''

    def get_org_applicant(self,obj):
        try:
            return obj.booking.proposal.approval.org_applicant.name
        except:
            return ''

    def get_proxy_applicant(self,obj):
        try:
            return obj.booking.proposal.approval.proxy_applicant
        except:
            return ''

    def get_invoice_reference(self,obj):
        #import ipdb; ipdb.set_trace()
        if obj.booking and obj.booking.invoices.all().last():
            inv = obj.booking.invoices.all().last()
            return inv.invoice_reference
        return None

    def get_payment_status(self,obj):
        #import ipdb; ipdb.set_trace()
        if obj.booking and obj.booking.invoices.all().last():
            inv = obj.booking.invoices.all().last()
            return Invoice.objects.get(reference=inv.invoice_reference).payment_status
        return None

