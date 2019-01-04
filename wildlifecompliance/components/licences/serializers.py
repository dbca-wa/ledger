from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from ledger.licence.models import LicenceType
from wildlifecompliance.components.licences.models import (
    WildlifeLicence,WildlifeLicenceClass,WildlifeLicenceActivityType,WildlifeLicenceActivity
)
from wildlifecompliance.components.applications.serializers import BaseApplicationSerializer
from wildlifecompliance.components.organisations.models import (
                                Organisation
                            )
from rest_framework import serializers

class WildlifeLicenceSerializer(serializers.ModelSerializer):
    licence_document = serializers.CharField(source='licence_document._file.url')
    status = serializers.CharField(source='get_status_display')
    current_application = BaseApplicationSerializer(read_only=True)

    class Meta:
        model = WildlifeLicence
        fields = (
            'id',
            'licence_document',
            'replaced_by',
            'current_application',
            'activity',
            'region',
            'tenure',
            'title',
            'renewal_sent',
            'issue_date',
            'original_issue_date',
            'start_date',
            'expiry_date',
            'surrender_details',
            'suspension_details',
            'extracted_fields',
            'status'
        )

class DefaultActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    class Meta:
        model = WildlifeLicenceActivity
        fields = (
            'id',
            'name',
            'base_application_fee',
            'base_licence_fee',
            'short_name'
        ) 


#    def __init__(self, *args, **kwargs):
#        # Don't pass the 'fields' arg up to the superclass
#        import ipdb; ipdb.set_trace()
#        fields = kwargs.pop('fields', None)
#
#        # Instantiate the superclass normally
#        super(DefaultActivitySerializer, self).__init__(*args, **kwargs)

#    def get_queryset(self):
#        #import ipdb; ipdb.set_trace()
#        user = self.request.user
#		app_ids = Application.objects.filter(Q(org_applicant_id=u.id) | Q(proxy_applicant=u.id) | Q(submitter=u.id)).values_list('id', flat=True).distinct('id')
#		activity_names = ApplicationActivityType.objects.filter(application_id__in=app_ids).values_list('activity_name').distinct()
#		return WildlifeLicenceActivity.objects.filter(name__in=activity_names)


class DefaultActivityTypeSerializer(serializers.ModelSerializer):

    name = serializers.CharField()
    activity = DefaultActivitySerializer(many=True,read_only=True)
    #activity = DefaultActivitySerializer(many=True,read_only=True, queryset=self.qs_purpose())
    class Meta:
        model = WildlifeLicenceActivityType
        fields = (
            'id',
            'name',
            'activity',
            'short_name',
            'not_for_organisation'
        ) 

#    def qs_purpose(self):
#        #import ipdb; ipdb.set_trace()
#        user = self.request.user
#        app_ids = Application.objects.filter(Q(org_applicant_id=u.id) | Q(proxy_applicant=u.id) | Q(submitter=u.id)).values_list('id', flat=True).distinct('id')
#        activity_names = ApplicationActivityType.objects.filter(application_id__in=app_ids).values_list('activity_name').distinct()
#        return WildlifeLicenceActivity.objects.filter(name__in=activity_names)



class WildlifeLicenceClassSerializer(serializers.ModelSerializer):
    class_status = serializers.SerializerMethodField()
    activity_type = DefaultActivityTypeSerializer(many=True,read_only=True)
    class Meta:
        model = WildlifeLicenceClass
        fields = (
            'id',
            'name',
            'short_name',
            'class_status',
            'activity_type'
            
        )
    def get_class_status(self,obj):
        return obj.get_licence_class_status_display()
