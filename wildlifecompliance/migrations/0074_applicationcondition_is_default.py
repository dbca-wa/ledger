# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-09-05 07:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0073_auto_20180905_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationcondition',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]