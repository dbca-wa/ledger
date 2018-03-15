from django.conf import settings
from ledger.accounts.models import EmailUser,Address,Profile
from wildlifecompliance.components.organisations.models import (   
                                    Organisation,
                                    OrganisationRequest,
                                    OrganisationContact
                                )
from wildlifecompliance.components.organisations.utils import can_admin_org
from rest_framework import serializers

class UserOrganisationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationContact
        fields=(
            'user_status',
            'user_role'
            )


class UserOrganisationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='organisation.name')
    abn = serializers.CharField(source='organisation.abn')
    # contacts = UserOrganisationContactSerializer(many=True)
    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
            'abn',
            # 'contacts',
        )

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


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id',
            'line1',
            'line2',
            'line3',
            'locality',
            'state',
            'country',
            'postcode',
        )


class UserProfileSerializer(serializers.ModelSerializer):
    postal_address = UserAddressSerializer()
    class Meta:
        model = Profile
        fields = (
            'id',
            'user',
            'name',
            'email',
            'institution',
            'postal_address'
        )

    def create(self, validated_data):
        print('serialiser create for profile')
        postal_address_data = validated_data.pop('postal_address')
        user = validated_data['user']
        new_postal_address, address_created = Address.objects.get_or_create(user=user,**postal_address_data)
        print(new_postal_address, new_postal_address.id)
        profile = Profile.objects.create(postal_address=new_postal_address,**validated_data)
        return profile


    def update(self, instance, validated_data):
        print('serialiser update for profile')
        print(validated_data)
        
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.institution = validated_data.get('institution', instance.institution)
        print('test')
        postal_address_data = validated_data.pop('postal_address')
        print('address details')
        print(postal_address_data)
        postal_address, address_created = Address.objects.get_or_create(user=instance.user,**postal_address_data)
        #postal_address, address_created = 'no','yes'
        print(address_created)
        print(postal_address)
        instance.postal_address = postal_address
        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    wildlifecompliance_organisations = UserOrganisationSerializer(many=True)
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


