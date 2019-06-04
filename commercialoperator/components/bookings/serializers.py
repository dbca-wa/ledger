from django.conf import settings
from ledger.accounts.models import EmailUser,Address
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

class ParkBookingSerializer(serializers.ModelSerializer):
    #proposal = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ParkBooking
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    park_bookings = ParkBookingSerializer(many=True, read_only=True)
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


