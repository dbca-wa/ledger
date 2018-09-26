from __future__ import unicode_literals

import json
from django.db import models,transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields.jsonb import JSONField
from django.utils import timezone
from django.contrib.sites.models import Site
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.licence.models import Licence,LicenceType
from wildlifecompliance import exceptions
from wildlifecompliance.components.organisations.models import Organisation
from wildlifecompliance.components.applications.models import Application
from wildlifecompliance.components.main.models import CommunicationsLogEntry, UserAction, Document
#from wildlifecompliance.components.licences.email import send_referral_email_notification


def update_licence_doc_filename(instance, filename):
    return 'licences/{}/documents/{}'.format(instance.id,filename)

class LicenceDocument(Document):
    licence = models.ForeignKey('WildlifeLicence',related_name='documents')
    _file = models.FileField(upload_to=update_licence_doc_filename)

    class Meta:
        app_label = 'wildlifecompliance'

class WildlifeLicenceActivity(models.Model):
    name = models.CharField(max_length = 100)
    short_name = models.CharField(max_length=30, default='')
    schema=JSONField(default=list)
    base_application_fee = models.DecimalField(max_digits=8, decimal_places=2, default='0')
    base_licence_fee = models.DecimalField(max_digits=8, decimal_places=2, default='0')
    
    # application_schema = JSONField(blank=True, null=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Licence purpose'
        verbose_name_plural = 'Licence purposes'

    def __str__(self):
        return self.name

# class WildlifeLicenceDescriptor(models.Model):
#     name = models.CharField(max_length = 100)


class WildlifeLicenceActivityType(models.Model):
    LICENCE_ACTIVITY_STATUS_CHOICES = (
        ('current','Current'),
        ('expired','Expired'),
        ('cancelled','Cancelled'),
        ('surrendered','Surrendered'),
        ('suspended','Suspended')
        )
    licence_activity_status = models.CharField(max_length=40, choices=LICENCE_ACTIVITY_STATUS_CHOICES,default=LICENCE_ACTIVITY_STATUS_CHOICES[0][0])
    name = models.CharField(max_length = 100)
    activity = models.ManyToManyField(WildlifeLicenceActivity, blank= True,through='DefaultActivity',related_name='wildlifecompliance_activity')
    short_name = models.CharField(max_length=30, default='')
    not_for_organisation = models.BooleanField(default=False, help_text='If ticked, this licenced activity will not be available for applications on behalf of an organisation.')
    schema=JSONField(default=list)
    # default_condition = models.ManyToManyField(Condition, through='DefaultCondition',blank= True)
    # default_period = models.PositiveIntegerField('Default Licence Period (days)', blank = True, null = True)
    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Licenced activity'
        verbose_name_plural = 'Licenced activities'

    def __str__(self):
        return self.name

    

# class DefaultCondition(models.Model):
#     condition = models.ForeignKey(Condition)
#     wildlife_licence_activity = models.ForeignKey(WildlifeLicenceActivity)
#     order = models.IntegerField()


# #LicenceType
class WildlifeLicenceClass(LicenceType):
    LICENCE_CLASS_STATUS_CHOICES = (
        ('current','Current'),
        ('expired','Expired'),
        ('cancelled','Cancelled'),
        ('surrendered','Surrendered'),
        ('suspended','Suspended')
        )
    licence_class_status = models.CharField(max_length=40, choices=LICENCE_CLASS_STATUS_CHOICES,default=LICENCE_CLASS_STATUS_CHOICES[0][0])
    # name = models.CharField(max_length = 100)
    activity_type = models.ManyToManyField(WildlifeLicenceActivityType, blank= True,through='DefaultActivityType',related_name='wildlifecompliance_activitytypes')
    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Licence category'
        verbose_name_plural = 'Licence categories'

    @property
    # override LicenceType display_name to display name first instead of short_name
    def display_name(self):
        result = self.name or self.short_name
        if self.replaced_by is None:
            return result
        else:
            return '{} (V{})'.format(result, self.version)

class DefaultActivityType(models.Model):
    activity_type = models.ForeignKey(WildlifeLicenceActivityType)
    licence_class = models.ForeignKey(WildlifeLicenceClass)

    class Meta:
        unique_together = (('licence_class','activity_type'))
        app_label = 'wildlifecompliance'
        verbose_name = 'Licenced category - licenced activity mapping'
        verbose_name_plural = 'Licenced category - licenced activity mappings'

    def __str__(self):
        return '{} - {}'.format(self.licence_class,self.activity_type)
    

class DefaultActivity(models.Model):
    activity = models.ForeignKey(WildlifeLicenceActivity)
    activity_type = models.ForeignKey(WildlifeLicenceActivityType)

    class Meta:
        unique_together = (('activity_type','activity'))
        app_label = 'wildlifecompliance'
        verbose_name = 'Licenced activity - purpose mapping'
        verbose_name_plural = 'Licenced activity - purpose mappings'

    def __str__(self):
        return '{} - {}'.format(self.activity_type,self.activity)


class WildlifeLicence(models.Model):
    STATUS_CHOICES = (
        ('current','Current'),
        ('expired','Expired'),
        ('cancelled','Cancelled'),
        ('surrendered','Surrendered'),
        ('suspended','Suspended')
    )
    status = models.CharField(max_length=40, choices=STATUS_CHOICES,
                                       default=STATUS_CHOICES[0][0])
    parent_licence=models.ForeignKey('self',blank=True,null=True,related_name='children_licence')
    licence_document = models.ForeignKey(LicenceDocument, blank=True, null=True, related_name='licence_document')
    cover_letter_document = models.ForeignKey(LicenceDocument, blank=True, null=True, related_name='cover_letter_document')
    replaced_by = models.ForeignKey('self', blank=True, null=True)
    current_application = models.ForeignKey(Application,related_name = '+')
    activity = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    tenure = models.CharField(max_length=255,null=True)
    title = models.CharField(max_length=255)
    renewal_sent = models.BooleanField(default=False)
    issue_date = models.DateField()
    original_issue_date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    expiry_date = models.DateField()
    surrender_details = JSONField(blank=True,null=True)
    suspension_details = JSONField(blank=True,null=True)
    applicant = models.ForeignKey(Organisation,on_delete=models.PROTECT, related_name='wildlifecompliance_licences')
    extracted_fields = JSONField(blank=True, null=True)

    # licence_class = models.ForeignKey(WildlifeLicenceClass)
    # licence_activity = models.ForeignKey(WildlifeLicenceActivity)
    # licence_descriptor = models.ForeignKey(WildlifeLicenceDescriptor)


    class Meta:
        app_label = 'wildlifecompliance'

    def __str__(self):
        return self.reference

    @property
    def reference(self):
        return '{}'.format(self.id)

    @property
    def is_issued(self):
        return self.licence_number is not None and len(self.licence_number) > 0

    def generate_doc(self):
        from wildlifecompliance.components.licences.pdf import create_licence_doc 
        self.licence_document = create_licence_doc(self,self.current_application)
        self.save()

    def log_user_action(self, action, request):
        return LicenceUserAction.log_action(self, action, request.user)

class LicenceLogEntry(CommunicationsLogEntry):
    licence = models.ForeignKey(WildlifeLicence, related_name='comms_logs')

    class Meta:
        app_label = 'wildlifecompliance'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.licence.id
        super(ApplicationLogEntry, self).save(**kwargs)

class LicenceUserAction(UserAction):
    ACTION_CREATE_LICENCE = "Create licence {}"
    ACTION_UPDATE_LICENCE = "Create licence {}"
    
    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, licence, action, user):
        return cls.objects.create(
            licence=licence,
            who=user,
            what=str(action)
        )

    licence= models.ForeignKey(WildlifeLicence, related_name='action_logs')

@receiver(pre_delete, sender=WildlifeLicence)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
