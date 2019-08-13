from django.conf import settings
from ledger.accounts.models import EmailUser, Address, Profile, EmailIdentity, EmailUserAction, Document
from wildlifecompliance.components.organisations.models import (
    Organisation,
    OrganisationRequest,
    OrganisationContact
)
from wildlifecompliance.components.users.models import CompliancePermissionGroup, RegionDistrict
from wildlifecompliance.components.organisations.utils import can_admin_org, is_consultant
from wildlifecompliance.helpers import is_customer, is_internal
from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from django.contrib.auth.models import Permission


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ('id', 'description', 'file', 'name', 'uploaded_date')


class UserOrganisationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationContact
        fields = (
            'user_status',
            'user_role',
            'email',
        )


class UserOrganisationSerializer(serializers.ModelSerializer):
    # Serializer for an Organisation linked with a User
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

    def get_is_admin(self, obj):
        user = EmailUser.objects.get(id=self.context.get('user_id'))
        return can_admin_org(obj, user)

    def get_is_consultant(self, obj):
        user = EmailUser.objects.get(id=self.context.get('user_id'))
        return is_consultant(obj, user)

    def get_email(self, obj):
        email = EmailUser.objects.get(id=self.context.get('user_id')).email
        return email


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
            raise serializers.ValidationError(
                'You must provide a mobile/phone number')
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
        profile = Profile()
        profile.user = validated_data['user']
        profile.name = validated_data['name']
        profile.email = validated_data['email']
        profile.institution = validated_data.get('institution', '')
        postal_address_data = validated_data.pop('postal_address')
        if profile.email:
            if EmailIdentity.objects.filter(
                    email=profile.email).exclude(
                    user=profile.user).exists():
                # Email already used by other user in email identity.
                raise ValidationError(
                    "This email address is already associated with an existing account or profile.")
        new_postal_address, address_created = Address.objects.get_or_create(
            user=profile.user, **postal_address_data)
        profile.postal_address = new_postal_address
        setattr(profile, "auth_identity", True)
        profile.save()
        return profile

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.institution = validated_data.get(
            'institution', instance.institution)
        postal_address_data = validated_data.pop('postal_address')
        if instance.email:
            if EmailIdentity.objects.filter(
                    email=instance.email).exclude(
                    user=instance.user).exists():
                # Email already used by other user in email identity.
                raise ValidationError(
                    "This email address is already associated with an existing account or profile.")
        postal_address, address_created = Address.objects.get_or_create(
            user=instance.user, **postal_address_data)
        instance.postal_address = postal_address
        setattr(instance, "auth_identity", True)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer()
    personal_details = serializers.SerializerMethodField()
    address_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    wildlifecompliance_organisations = serializers.SerializerMethodField()
    identification = DocumentSerializer()

    class Meta:
        model = EmailUser
        fields = (
            'title',
            'id',
            'last_name',
            'first_name',
            'dob',
            'email',
            'identification',
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

    def get_personal_details(self, obj):
        return True if obj.last_name and obj.first_name and obj.dob else False

    def get_address_details(self, obj):
        return True if obj.residential_address else False

    def get_contact_details(self, obj):
        if obj.mobile_number and obj.email:
            return True
        elif obj.phone_number and obj.email:
            return True
        elif obj.mobile_number and obj.phone_number:
            return True
        else:
            return False

    def get_wildlifecompliance_organisations(self, obj):
        wildlifecompliance_organisations = obj.wildlifecompliance_organisations
        serialized_orgs = UserOrganisationSerializer(
            wildlifecompliance_organisations, many=True, context={
                'user_id': obj.id}).data
        return serialized_orgs


class DTUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailUser
        fields = (
            'title',
            'id',
            'last_name',
            'first_name',
            'dob',
            'email',
            'phone_number',
            'mobile_number',
            'fax_number',
            'character_flagged',
            'character_comments',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields


class MyUserDetailsSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer()
    personal_details = serializers.SerializerMethodField()
    address_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    wildlifecompliance_organisations = serializers.SerializerMethodField()
    identification = DocumentSerializer()
    is_customer = serializers.SerializerMethodField()
    is_internal = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            'title',
            'id',
            'last_name',
            'first_name',
            'dob',
            'email',
            'identification',
            'residential_address',
            'phone_number',
            'mobile_number',
            'fax_number',
            'wildlifecompliance_organisations',
            'personal_details',
            'address_details',
            'contact_details',
            'is_customer',
            'is_internal',
        )

    def get_personal_details(self, obj):
        return True if obj.last_name and obj.first_name and obj.dob else False

    def get_address_details(self, obj):
        return True if obj.residential_address else False

    def get_contact_details(self, obj):
        if obj.mobile_number and obj.email:
            return True
        elif obj.phone_number and obj.email:
            return True
        elif obj.mobile_number and obj.phone_number:
            return True
        else:
            return False

    def get_wildlifecompliance_organisations(self, obj):
        wildlifecompliance_organisations = obj.wildlifecompliance_organisations
        serialized_orgs = UserOrganisationSerializer(
            wildlifecompliance_organisations, many=True, context={
                'user_id': obj.id}).data
        return serialized_orgs

    def get_is_customer(self, obj):
        return is_customer(self.context.get('request'))

    def get_is_internal(self, obj):
        return is_internal(self.context.get('request'))


class ComplianceUserDetailsSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer()
    personal_details = serializers.SerializerMethodField()
    address_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    # compliance_permissions = serializers.SerializerMethodField()

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
            # 'compliance_permissions',
            'personal_details',
            'address_details',
            'contact_details'
        )

    def get_personal_details(self, obj):
        return True if obj.last_name and obj.first_name and obj.dob else False

    def get_address_details(self, obj):
        return True if obj.residential_address else False

    def get_contact_details(self, obj):
        if obj.mobile_number and obj.email:
            return True
        elif obj.phone_number and obj.email:
            return True
        elif obj.mobile_number and obj.phone_number:
            return True
        else:
            return False

    # def get_wildlifecompliance_organisations(self, obj):
    #     wildlifecompliance_organisations = obj.wildlifecompliance_organisations
    #     serialized_orgs = UserOrganisationSerializer(
    #         wildlifecompliance_organisations, many=True, context={
    #             'user_id': obj.id}).data
    #     return serialized_orgs


class ComplianceUserDetailsOptimisedSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            'title',
            'id',
            'last_name',
            'first_name',
            'email',
            'full_name',
        )
    
    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return obj.first_name + ' ' + obj.last_name


class EmailUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')

    class Meta:
        model = EmailUserAction
        fields = '__all__'


class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'last_name',
            'first_name',
            'dob',
        )


class EmailIdentitySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = EmailIdentity
        fields = (
            'user',
            'email'
        )


class RegionDistrictSerializer(serializers.ModelSerializer):
    # region = RegionDistrictSerializer(many=True)

    class Meta:
        model = RegionDistrict
        fields = (
            'id',
            'district',
            'region',
            'display_name',
            'districts'
        )


class CompliancePermissionGroupSerializer(serializers.ModelSerializer):
    region_district = RegionDistrictSerializer(many=True)

    class Meta:
        model = CompliancePermissionGroup
        fields = (
            'id',
            'name',
            'region_district',
            'display_name',
            )


class CompliancePermissionGroupMembersSerializer(serializers.ModelSerializer):
    members = ComplianceUserDetailsOptimisedSerializer(many=True)

    class Meta:
        model = CompliancePermissionGroup
        fields = (
            'members',
            )


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = (
            'codename',
        )
        read_only_fields = (
            'codename',
        )


class CompliancePermissionGroupDetailedSerializer(serializers.ModelSerializer):
    region_district = RegionDistrictSerializer(many=True)
    members = ComplianceUserDetailsOptimisedSerializer(many=True)
    # permissions = PermissionSerializer(many=True)
    permissions_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CompliancePermissionGroup
        fields = (
            'id',
            'name',
            'region_district',
            'display_name',
            'members',
            # 'permissions',
            'permissions_list',
            )

    def get_permissions_list(self, obj):
        permissions_list = []
        for permission in obj.permissions.all():
            permissions_list.append(permission.codename)
        return permissions_list

