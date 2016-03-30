# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_licence_types(apps, schema_editor):
    LicenseType = apps.get_model('licence', 'LicenceType')
    LicenseType.objects.create(name='Application for a licence to take fauna for scientific purposes', code='regulation17')


class Migration(migrations.Migration):

    dependencies = [
        ('licence', '0003_auto_20160323_1434'),
    ]

    operations = [
        migrations.RunPython(create_licence_types),
    ]
