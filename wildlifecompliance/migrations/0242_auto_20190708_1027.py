# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-07-08 02:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0241_auto_20190708_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callemail',
            name='occurrence_date_from',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='callemail',
            name='occurrence_date_to',
            field=models.DateField(null=True),
        ),
    ]