# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-11-07 06:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0011_auto_20240111_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
