# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core.management import call_command

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../components/proposals/fixtures'))

def load_fixture(apps, schema_editor):
    call_command('loaddata', os.path.join(fixture_dir, 'default_proposal_assessor_group.json'))
    call_command('loaddata', os.path.join(fixture_dir, 'default_proposal_approver_group.json'))

def reverse_add_default_group(apps, schema_editor):
    ProposalApproverGroup = apps.get_model('disturbance','ProposalApproverGroup')
    ProposalApproverGroup.objects.filter(default=True).delete()
    ProposalAssessorGroup = apps.get_model('disturbance','ProposalAssessorGroup')
    ProposalAssessorGroup.objects.filter(default=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('disturbance', '0002_compliance'),
    ]

    operations = [
        migrations.RunPython(load_fixture,reverse_add_default_group),
    ]
