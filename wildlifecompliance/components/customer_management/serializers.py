from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from rest_framework import serializers

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser 
        fields = (
            'id',
            'first_name',
            'last_name',
            'title',
            'dob',
            'email',
            'phone_number',
            'mobile_number',
            'fax_number',
            'character_flagged',
            'character_comments',
        )
