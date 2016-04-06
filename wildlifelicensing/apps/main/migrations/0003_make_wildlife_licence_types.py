# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_wildlife_licence_types(apps, schema_editor):
    WildlifeLicenceType = apps.get_model('main', 'WildlifeLicenceType')
    WildlifeLicenceType.objects.create(name='Application for a licence to take fauna for scientific purposes', code='regulation17')


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_condition_wildlifelicencetype'),
    ]

    operations = [
        migrations.RunPython(create_wildlife_licence_types),
    ]
