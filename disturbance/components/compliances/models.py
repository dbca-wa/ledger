
from __future__ import unicode_literals

import json
import datetime
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
from ledger.licence.models import  Licence
from disturbance import exceptions
from disturbance.components.organisations.models import Organisation
from disturbance.components.main.models import CommunicationsLogEntry, Region, UserAction, Document

class Compliance(models.Model):

    PROCESSING_STATUS_CHOICES = (('due', 'Due'), 
                                 ('future', 'Future'), 
                                 ('with_assessor', 'With Assessor'),
                                 ('approved', 'Approved'),
                                 )

    CUSTOMER_STATUS_CHOICES = (('due', 'Due'), 
                                 ('future', 'Future'), 
                                 ('with_assessor', 'Under Review'),
                                 ('approved', 'Approved'),
                                 )
    

    proposal = models.ForeignKey('disturbance.Proposal',related_name='compliances')
    approval = models.ForeignKey('disturbance.Approval',related_name='compliances')
    due_date = models.DateField()
    text = models.TextField(blank=True)
    processing_status = models.CharField(choices=PROCESSING_STATUS_CHOICES,max_length=20)
    customer_status = models.CharField(choices=CUSTOMER_STATUS_CHOICES,max_length=20, default=CUSTOMER_STATUS_CHOICES[1][0])
    assigned_to = models.ForeignKey(EmailUser,related_name='disturbance_compliance_assignments',null=True,blank=True)
    requirement = models.TextField(null=True,blank=True)
    lodgement_date = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'disturbance'

    @property
    def regions(self):
        return self.proposal.regions_list

    @property
    def activity(self):
        return self.proposal.activity

    @property
    def title(self):
        return self.proposal.title

    @property
    def holder(self):
        return self.proposal.applicant

    @property
    def reference(self):
        return 'C{}'.format(self.id)

    @property
    def can_user_view(self):
        """
        :return: True if the application is in one of the editable status.
        """
        return self.customer_status == 'with_assessor' or self.customer_status == 'approved'

    def submit(self,request):
        with transaction.atomic():
            try:               
                if self.processing_status == 'future' or 'due':
                    self.processing_status = 'with_assessor'
                    self.customer_status = 'with_assessor'

                    if request.FILES:
                        for f in request.FILES:
                            document = self.documents.create()
                            document.name = str(request.FILES[f])
                            document._file = request.FILES[f]
                            document.save()
                self.lodgement_date = datetime.datetime.strptime(timezone.now().strftime('%Y-%m-%d'),'%Y-%m-%d').date()   
                self.save() 
            except:
                raise


def update_proposal_complaince_filename(instance, filename):
    return 'proposals/{}/compliance/{}/{}'.format(instance.compliance.proposal.id,instance.compliance.id,filename)


class ComplianceDocument(Document):
    compliance = models.ForeignKey('Compliance',related_name='documents')
    _file = models.FileField(upload_to=update_proposal_complaince_filename)


    class Meta:
        app_label = 'disturbance'