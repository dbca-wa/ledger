# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-17 05:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bpoint', '0016_auto_20211217_1313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bpointtoken',
            name='ois',
        ),
    ]
