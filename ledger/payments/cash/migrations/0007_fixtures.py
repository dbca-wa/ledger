# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import migrations
from django.core.management import call_command

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))


def load_fixture(apps, schema_editor):
    pass
    # call "manage.py load_ledger_fixtures" to do this instead
    #call_command('loaddata', os.path.join(fixture_dir, 'payments_regions.json'))
    #call_command('loaddata', os.path.join(fixture_dir, 'payments_districts.json'))


class Migration(migrations.Migration):

    dependencies = [
        ('cash', '0006_auto_20160823_1127'),
    ]

    operations = [
        migrations.RunPython(load_fixture)
    ]
