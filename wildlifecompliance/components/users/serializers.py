from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from wildlifecompliance.components.organisations.models import (   
                                    Organisation,
                                    OrganisationRequest,
                                    OrganisationContact
                                )
from wildlifecompliance.components.organisations.utils import can_admin_org,is_consultant
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id',
            'line1',
            'locality',
            'state',
            'country',
            'postcode'
        )

class UserOrganisationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationContact
        fields=(
            'user_status',
            'user_role',
            'email',
            )

class UserOrganisationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='organisation.name')
    abn = serializers.CharField(source='organisation.abn')
    email = serializers.SerializerMethodField()
    is_consultant = serializers.SerializerMethodField(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)

    class Meta():
        model = Organisation
        fields = (
            'id',
            'name',
            'abn',
            'email',
            'is_consultant',
            'is_admin'
        )

    def get_is_admin(self,obj):
        user =  self.context['request'].user
        # Check if the request user is among the first five delegates in the organisation
        return can_admin_org(obj,user)

    def get_is_consultant(self,obj):
        user =  self.context['request'].user
        # Check if the request user is among the first five delegates in the organisation
        return is_consultant(obj,user)

    def get_email(self,obj):
        request = self.context.get('request')
        email = request.user.email
        # email = request.user.email
        return email



class UserSerializer(serializers.ModelSerializer):
    # wildlifecompliance_organisations = UserOrganisationSerializer(many=True)
    residential_address = UserAddressSerializer()
    personal_details = serializers.SerializerMethodField()
    address_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            'title',
            'id',
            'last_name',
            'first_name',
            'dob',
            'email',
            'residential_address',
            'phone_number',
            'mobile_number',
            'fax_number',
            'character_flagged',
            'character_comments',
            'wildlifecompliance_organisations',
            'personal_details',
            'address_details',
            'contact_details'
        )


    def get_personal_details(self,obj):
        return True if obj.last_name  and obj.first_name else False

    def get_address_details(self,obj):
        return True if obj.residential_address else False

    def get_contact_details(self,obj):
        if obj.mobile_number and obj.email:
            return True
        elif obj.mobile_number and obj.phone_number:
            return True
        else:
            return False

    def __init__(self,*args,**kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        print(self.fields['email'])
        self.fields['wildlifecompliance_organisations'] = UserOrganisationSerializer(many=True,context={'request':self.context['request']})
   

class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'last_name',
            'first_name',
            'dob',
        )

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'email',
            'phone_number',
            'mobile_number',
        )

    def validate(self, obj):
        if not obj.get('phone_number') and not obj.get('mobile_number'):
            raise serializers.ValidationError('You must provide a mobile/phone number')
        return obj
