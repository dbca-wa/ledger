# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.create(name='Customers')
    Group.objects.create(name='Officers')
    Group.objects.create(name='Assessors')
    Group.objects.create(name='Assessor Management')
    Group.objects.create(name='Others')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]